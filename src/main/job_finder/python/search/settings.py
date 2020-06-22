import pkg_resources


class Settings:
    LANGUAGE_DIR = "language"
    FILTERS_DIR = "filters"

    def __init__(self, resources_root):
        self.resources_root = resources_root
        self.language_resources = pkg_resources.resource_listdir(resources_root, self.LANGUAGE_DIR)
        self.filter_resources = pkg_resources.resource_listdir(resources_root, self.FILTERS_DIR)

    def set_language(self, requested_language):
        for language in self.language_resources:
            if requested_language.strip().lower() in language:
                return f"{self.LANGUAGE_DIR}\\{language}"
        print("This language is not supported")
        return None

    def set_filters(self):
        pass

    def __add_filter(self):
        pass

    def __remove_filter(self):
        pass

    def __get_filters(self):
        pass