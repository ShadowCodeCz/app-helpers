import glob
import json
import logging
import logging.config
import os.path
import pathlib


class AppDescription:
    def __init__(self, name, version=""):
        self.name = name
        self.version = version


# TODO: SUB APPLICATION
# TODO: help vs helps, resource vs resources

class LoggerHelper:
    def __init__(self, app_description, locale_path_helper):
        self.app_description = app_description
        self.locale_path_helper = locale_path_helper

    def logger_name(self):
        return f"{self.app_description.name}.{self.app_description.version}"

    def output_file(self):
        return os.path.join(self.locale_path_helper.log_directory(), "log.txt")

    def prepare_output_directory(self):
        os.makedirs(self.locale_path_helper.log_directory(), exist_ok=True)

    def configuration(self):
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'loggers': {
                f"{self.logger_name()}": {
                    'level': logging.DEBUG,
                    'propagate': False,
                    'handlers': ['console_handler', 'time_rotating_file_handler'],
                },
            },

            'handlers': {
                'console_handler': {
                    'level': logging.INFO,
                    'formatter': 'simple',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                },

                'time_rotating_file_handler': {
                    'level': logging.DEBUG,
                    'formatter': 'generic',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': self.output_file(),
                    'when': 'midnight',
                    'backupCount': 5
                },
            },

            'formatters': {
                'generic': {
                    'format': '%(asctime)s %(levelname)s %(message)s'
                },
                'simple': {
                    'format': '%(message)s'
                }
            },
        }

    def configure(self):
        logging.config.dictConfig(self.configuration())


class LocalePaths:
    def __init__(self, app_description):
        self.app_description = app_description
        self.app_version_as_subdirectory = True

    def user_home_directory(self):
        return str(pathlib.Path.home())

    def apps_directory(self):
        return self.user_home_directory()

    def app_directory(self):
        if self.app_version_as_subdirectory:
            return os.path.join(self.apps_directory(), f"{self.app_description.name}", self.app_description.version)
        else:
            return os.path.join(self.apps_directory(), f"{self.app_description.name}.{self.app_description.version}")

    def configuration_directory(self):
        return os.path.join(self.app_directory(), "configuration")

    def plugin_directory(self):
        return os.path.join(self.app_directory(), "plugin")

    def log_directory(self):
        return os.path.join(self.app_directory(), "log")

    def help_directory(self):
        return os.path.join(self.app_directory(), "help")


class PackagePaths:
    def __init__(self, app_description, python_package_directory):
        self.app_description = app_description
        self.python_package_directory = python_package_directory
        self.app_version_as_subdirectory = True

    def root_directory(self):
        if self.app_version_as_subdirectory:
            return os.path.join(self.python_package_directory, self.app_description.version)
        else:
            return self.python_package_directory
    def resource_directory(self):
        return os.path.join(self.root_directory(), "resource")

    def configuration_directory(self):
        return os.path.join(self.root_directory(), "configuration")

    def image_directory(self):
        return os.path.join(self.resource_directory(), "image")

    def plugin_directory(self):
        return os.path.join(self.root_directory(), "plugin")


# TODO: Configuration helpers ... save to JSON file


class Help:
    # TODO: logger
    def __init__(self, locale_path_helper, logger):
        self.locale_path_helper = locale_path_helper
        self.helps = {}
        self.logger = logger

    def read(self):
        for help_file in self.find_help_files():
            self.helps[self.help_key(help_file)] = self.read_file(help_file)

    def read_file(self, path):
        # TODO: Try except log
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Reading help file '{path}' failed.{e}")

    def help_key(self, help_file):
        return os.path.basename(help_file).replace(".txt", "")

    def find_help_files(self):
        template = os.path.join(self.locale_path_helper.help_directory(), "*.txt")
        return glob.glob(template)

    def get_help(self, key):
        if key in self.helps:
            return self.helps[key]
        else:
            return ""

    def create_empty_help(self, key):
        try:
            # TODO: Try except log
            os.makedirs(self.locale_path_helper.help_directory(), exist_ok=True)

            path = os.path.join(self.locale_path_helper.help_directory(), f"{key}.txt")
            if not os.path.exists(path):
                with open(path, "w+") as f:
                    f.write("")
            else:
                self.logger.debug(f"Help file '{path}' already exists. ")
        except Exception as e:
            self.logger.error(f"Creating of empty help file '{path}' failed.{e}")


class Configuration:
    def __init__(self, path_helper, logger):
        self.path_helper = path_helper
        self.cfgs = {}
        self.logger = logger

    def read(self):
        for cfg_file in self.find_cfg_files():
            self.cfgs[self.cfg_key(cfg_file)] = self.read_file(cfg_file)

    def read_file(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Reading configuration file '{path}' failed.{e}")
    def cfg_key(self, cfg_file):
        return os.path.basename(cfg_file).replace(".json", "")

    def find_cfg_files(self):
        template = os.path.join(self.path_helper.configuration_directory(), "*.json")
        return glob.glob(template)

    def get_cfg(self, key):
        if key in self.cfgs:
            return self.cfgs[key]
        else:
            return {}

    def create_cfg(self, key, data):
        try:
            os.makedirs(self.path_helper.configuration_directory(), exist_ok=True)

            path = os.path.join(self.path_helper.configuration_directory(), f"{key}.json")
            if not os.path.exists(path):
                with open(path, "w+") as f:
                    json.dump(data, f, indent=4)
            else:
                self.logger.debug(f"Configuration file '{path}' already exists. ")
        except Exception as e:
            self.logger.error(f"Creating configuration file '{path}' failed.{e}")


def cli_arguments_to_dict(arguments, key_mapping=None):
    arguments_dict = vars(arguments)
    del arguments_dict["func"]

    if key_mapping is None:
        return arguments_dict
    else:
        return {key_mapping[old_key]: value for old_key, value in arguments_dict.items()}