import pkg_resources
from job_finder.python.util.data_supplier import DataSupplier
from job_finder.python.util.input_manager import InputManager
from job_finder.python.search.settings import Settings
from job_finder.python.search.searcher import Searcher

resources_root = "job_finder.resources"

if __name__ == '__main__':
    data_supplier =\
        DataSupplier(pkg_resources.resource_filename(resources_root, "url_list.txt"),
                     pkg_resources.resource_filename(resources_root, "filters\\not_in_job_title.txt"),
                     pkg_resources.resource_filename(resources_root, "filters\\in_job_title.txt"),
                     pkg_resources.resource_filename(resources_root, "filters\\not_in_job_post.txt"),
                     pkg_resources.resource_filename(resources_root, "filters\\in_job_post.txt"),
                     pkg_resources.resource_filename(resources_root, "special_pagination_xpath.txt"))
    while True:
        language = Settings(resources_root).set_language(input("Enter your language: "))
        if language:
            break
    data_supplier.add_language_pack(
        pkg_resources.resource_filename(resources_root, language))
    #searcher = Searcher(data_supplier.url_list, InputManager.request_input(),
                        #data_supplier.language_pack, data_supplier.not_in_job_title,
                        #data_supplier.in_job_title, data_supplier.not_in_job_post,
                        #data_supplier.in_job_post, data_supplier.special_pagination)
    #searcher.set_mode(searcher.FAST_MODE)
    #searcher.output_founded(InputManager.request_file_name())
