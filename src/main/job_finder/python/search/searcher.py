import _io
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from requests_html import HTMLSession
from multipledispatch import dispatch
import re


class Searcher:

    __REGEX_IDENTIFIER = "regex!"
    __DRIVER_PATH = "C:\\Program Files (x86)\\chromedriver.exe"
    FAST_MODE = {"load_wait_time": 2, "popup_wait_time": 1}
    MILD_MOD = {"load_wait_time": 4, "popup_wait_time": 2}
    SLOW_MOD = {"load_wait_time": 6, "popup_wait_time": 3}

    def __init__(self, url_list, search_request, language_pack, not_in_job_title=None,
                 in_job_title=None, not_in_job_post=None,
                 in_job_post=None, special_pagination=None):
        self.__url_list = url_list
        self.search_request = search_request
        self.__language_pack = language_pack
        self.__not_in_job_title = not_in_job_title
        self.__in_job_title = in_job_title
        self.__not_in_job_post = not_in_job_post
        self.__in_job_post = in_job_post
        self.__special_pagination = special_pagination
        self.__mode = self.MILD_MOD

    @dispatch()
    def output_founded(self):
        findings = self.search()
        for key in [*findings]:
            print(key)
            for page in findings[key]:
                for job in page:
                    print(job[0], ": ", job[-1], "\n")

    @dispatch(str)
    def output_founded(self, new_file_name):
        findings = self.search()
        with open(f"{new_file_name}.csv", "w", newline="", encoding='UTF-8') as csv_file:
            field_names = self.__language_pack["column_names"]
            file_writer = csv.DictWriter(csv_file, field_names, dialect='excel')
            file_writer.writeheader()
            for key in [*findings]:
                for page in findings[key]:
                    for job in page:
                        file_writer.writerow(
                            {field_names[0]: key, field_names[1]: job[0], field_names[2]: job[-1]})

    @dispatch(_io.TextIOWrapper)
    def output_founded(self, file_name):
        findings = self.search()
        field_names = self.__language_pack["column_names"]
        file_writer = csv.DictWriter(file_name, field_names, dialect='excel')
        file_writer.writeheader()
        for key in [*findings]:
            for page in findings[key]:
                for job in page:
                    file_writer.writerow(
                        {field_names[0]: key, field_names[1]: job[0], field_names[2]: job[-1]})

    def set_mode(self, mode):
        try:
            if isinstance(mode["load_wait_time"], int) \
                    and isinstance(mode["popup_wait_time"], int):
                self.__mode = mode
                print("Mode set successfully")
            else:
                raise TypeError
        except TypeError or KeyError:
            print("Cannot set mode, incorrect format object")

    def search(self):
        driver = webdriver.Chrome(self.__DRIVER_PATH)
        findings = {}
        try:
            for base_url in self.__url_list:
                if self.__check_url_validity(base_url):
                    website_jobs = []
                    website_cash = []
                    driver.get(base_url)

                    try:
                        WebDriverWait(driver, self.__mode["load_wait_time"]).until(
                            ec.presence_of_element_located((By.XPATH, "//input")))
                        search_job, search_location = self.__find_search_fields(driver)
                    except TimeoutException:
                        continue

                    if not search_job or not search_location:
                        continue

                    ActionChains(driver).click(search_job)\
                        .send_keys_to_element(search_job, self.search_request[0])\
                        .click(search_location)\
                        .send_keys_to_element(search_location, self.search_request[-1], Keys.RETURN)\
                        .pause(self.__mode["load_wait_time"]).perform()

                    while True:
                        ActionChains(driver).pause(self.__mode["popup_wait_time"])\
                            .send_keys(Keys.ESCAPE).send_keys(Keys.PAGE_DOWN)\
                            .perform()
                        html = etree.HTML(driver.page_source)
                        if not self.__get_results(html):
                            break
                        website_jobs.append(self.__find_jobs(self.__get_results(html),
                                                             base_url, driver.current_url, website_cash))
                        if not self.__open_next_page(driver, base_url, driver.current_url):
                            break
                    findings[base_url] = website_jobs
                else:
                    print(f"Could not get response from {base_url}")
        finally:
            driver.delete_all_cookies()
            driver.quit()
            return findings

    def __open_next_page(self, driver, base_url, current_url):
        for key_word in self.__language_pack["next_page_flags"]:
            try:
                next_page_nav = etree.HTML(driver.page_source).xpath(
                    f"//div/a[contains(text(), '{key_word}')]|"
                    f"//div/a[contains(@title, '{key_word}')]|"
                    f"//div/a[span[span[contains(text(), '{key_word}')]]]"
                    + self.__adjust_special_pagination())
                href = next_page_nav[0].get("href")
                if href:
                    driver.get(self.__get_page_link(base_url, current_url, href, True))
                    driver.delete_all_cookies()
                    return True
            except IndexError:
                if self.__get_page_link("", current_url, "", True):
                    driver.get(self.__get_page_link("", current_url, "", True))
                    return True
                return False
        return False

    def __find_jobs(self, html_results, base_url, current_url, cash):
        jobs_found = []
        for result in html_results:
            soup = BeautifulSoup(etree.tostring(result), features="lxml")
            job_title = soup.a.text.rstrip()
            href = soup.a.get("href")
            if (job_title, href) not in cash:
                cash.append((job_title, href))
                if self.__check_job(job_title, self.__not_in_job_title, self.__in_job_title):
                    link = self.__get_page_link(base_url, current_url, href)
                    if link:
                        response = HTMLSession().get(link)
                        response.html.render()
                        job_post = response.text
                        if self.__check_job(job_post,
                                            self.__not_in_job_post, self.__in_job_post):
                            link.rstrip()
                            jobs_found.append((job_title, link))
        return jobs_found

    @staticmethod
    def __get_results(html):
        return html.xpath(
            "//div[a[*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5]]]|"
            "//div[*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5][a]]|"
            "//div[header[a[*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5]]]]|"
            "//div[header[*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5][a]]]")

    def __find_search_fields(self, driver):
        search_job, search_location = None, None

        for key_word in self.__language_pack["job_input_flags"]:
            try:
                search_job = driver.find_element_by_xpath(
                    f"//input[contains(@placeholder, '{key_word}')]")
            except NoSuchElementException:
                continue
            if search_job:
                break

        for key_word in self.__language_pack["location_input_flags"]:
            try:
                search_location = driver.find_element_by_xpath(
                    f"//input[contains(@placeholder, '{key_word}')]")
            except NoSuchElementException:
                continue
            if search_location:
                break

        return search_job, search_location

    def __get_page_link(self, base_url, current_url, href, next_page=False):
        href_page_id = self.__find_page_query(href)
        url_page_id = self.__find_page_query(current_url)
        if href_page_id and next_page:
            page_number = re.search(re.compile("\\d+"),
                                    href_page_id.group(0))\
                .group(0)
            if self.__find_page_query(current_url):
                return re.sub("&page=\\d+", f"&page={page_number}", current_url)
            else:
                return f"{current_url}&page={page_number}"
        elif url_page_id and next_page:
            page_number = int(re.search(re.compile("\\d+"),
                                        url_page_id.group(0))
                              .group(0)) + 1
            return re.sub("&page=\\d+", f"&page={page_number}", current_url)
        elif self.__check_url_validity(href):
            return href
        elif self.__check_url_validity(self.__construct_url(base_url, href)):
            return self.__construct_url(base_url, href)
        return None

    def __adjust_special_pagination(self):
        adjustment = ""
        if self.__special_pagination:
            for xpath in self.__special_pagination:
                adjustment += "|" + xpath
        return adjustment

    @classmethod
    def __check_job(cls, to_check, not_in_=None, in_=None):
        if not_in_:
            for line in not_in_:
                if cls.__REGEX_IDENTIFIER in line:
                    if re.search(re.compile(line.split(" ")[-1], re.I), to_check):
                        return False
        if in_:
            for line in in_:
                if cls.__REGEX_IDENTIFIER in line:
                    if re.search(re.compile(line.split(" ")[-1], re.I), to_check):
                        return True
            return False
        return True

    @staticmethod
    def __find_page_query(link):
        return re.search(re.compile("page=\\d+"), link)

    @staticmethod
    def __construct_url(url, href=None):
        elements = urlparse(url)
        return f"{elements.scheme}://{elements.netloc}{href}"

    @staticmethod
    def __check_url_validity(url):
        try:
            if requests.get(url, timeout=10).ok:
                return True
        except Exception as e:
            return False
