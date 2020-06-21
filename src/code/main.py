import csv
from src.code.DataSupplier import DataSupplier
from src.code.InputManager import InputManager
from src.code.Searcher import Searcher

if __name__ == '__main__':
    data_supplier =\
        DataSupplier("C:\\Users\\Александр\\Desktop\\JobFinder Project\\src\\resources\\url_list.txt",
                        "C:\\Users\\Александр\\Desktop\\JobFinder Project\\src\\resources\\not_in_job_title.txt",
                        "C:\\Users\\Александр\\Desktop\\JobFinder Project\\src\\resources\\in_job_title.txt",
                        "C:\\Users\\Александр\\Desktop\\JobFinder Project\\src\\resources\\not_in_job_post.txt",
                        "C:\\Users\\Александр\\Desktop\\JobFinder Project\\src\\resources\\in_job_post.txt",
                        "C:\\Users\\Александр\\Desktop\\JobFinder Project\\src\\resources\\special_pagination_xpath.txt")
    data_supplier.add_language_pack("C:\\Users\\Александр\\Desktop\\JobFinder Project\\src\\resources\\german.txt")
    searcher = Searcher(data_supplier.url_list, InputManager.request_input(),
                        data_supplier.language_pack, data_supplier.not_in_job_title,
                        data_supplier.in_job_title, data_supplier.not_in_job_post,
                        data_supplier.in_job_post, data_supplier.special_pagination)
    searcher.set_mode(searcher.FAST_MODE)
    searcher.output_founded(InputManager.request_file_name())
