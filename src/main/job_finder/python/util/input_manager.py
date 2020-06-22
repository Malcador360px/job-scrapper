class InputManager:
    def __init__(self):
        pass

    @staticmethod
    def request_input():
        return input("Enter key word for a job: "),\
               input("Enter your desired location: ")

    @staticmethod
    def request_file_name():
        return input("Enter the name for csv file: ")
