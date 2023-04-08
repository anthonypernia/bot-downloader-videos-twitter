"""Module to read config file"""
from typing import Dict, Union

import yaml


class Config:
    """Class to read config file"""

    def __init__(self, config_file: str) -> None:
        """create a config object
        Args:
            config_file (str): path to config file
        """
        with open(config_file, encoding="utf-8") as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)

    def get(self, key: str) -> Union[str, Dict[str, str]]:
        """get a value from the config file
        Args:
            key (str): key to get value for
        Returns:
            str: value for key
        """
        return self.config[key]

    def get_all(self) -> dict:
        """get all values from the config file
        Returns:
            dict: all values from the config file
        """
        return self.config
