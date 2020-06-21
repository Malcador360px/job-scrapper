import os


class DataSupplier:

    def __init__(self, url_list_path, not_in_job_title_path,
                 in_job_title_path, not_in_job_post_path, in_job_post_path, special_pagination=None):
        self.url_list = self.extract_data_from_files(url_list_path)
        self.not_in_job_title = self.extract_data_from_files(not_in_job_title_path)
        self.in_job_title = self.extract_data_from_files(in_job_title_path)
        self.not_in_job_post = self.extract_data_from_files(not_in_job_post_path)
        self.in_job_post = self.extract_data_from_files(in_job_post_path)
        self.special_pagination = self.extract_data_from_files(special_pagination)
        self.language_pack = {"job_input_flags": [],
                              "location_input_flags": [], "next_page_flags": [], "column_names": []}

    def add_language_pack(self, language_config):
        if os.path.isfile(language_config):
            with open(language_config) as file:
                data_list = []
                for line in file.readlines():
                    data_list.append(line.rstrip().split(", "))
                for data in data_list:
                    self.language_pack[data[0]] = data[1:]
        else:
            print("Cannot locate file " + language_config)

    @staticmethod
    def extract_data_from_files(file_path):
        if file_path:
            if os.path.isfile(file_path):
                with open(file_path) as file:
                    data_list = []
                    for line in file.readlines():
                        data_list.append(line.rstrip())
                    return data_list
            else:
                print("Cannot locate file " + file_path)
        return []
