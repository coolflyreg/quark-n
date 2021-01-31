# -*- coding:utf-8 -*-

import os
import sys
from ruamel.yaml import YAML
import logging
from core import Singleton

logger = logging.getLogger('display.ui')

class Config(metaclass=Singleton):

    __config_data = None
    __listeners = {}

    def __init__(self):
        self.reload()

    def reload(self):
        yaml = YAML()
        yaml.default_flow_style = False
        config_file = open(os.path.join(sys.path[0], 'config.yaml'), 'r')
        # self.__config_data = yaml.load(config_file, yaml.FullLoader)
        self.__config_data = yaml.load(config_file)
        config_file.close()

    def save(self):
        yaml = YAML()
        yaml.default_flow_style = False
        config_file = open(os.path.join(sys.path[0], 'config.yaml'), 'w')
        yaml.dump(self.__config_data, config_file)
        config_file.close()

    def get(self, key_path, default=None):
        keys = key_path.split('.')
        value = self.__config_data
        for key in keys:
            if value.__contains__(key):
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path, value):
        keys = key_path.split('.')
        item = self.__config_data
        for key in keys[:-1]:
            item = item[key]

        item[keys[-1]] = value

        self.call_listeners(key_path, value)

    def dump(self):
        return yaml.dump(self.__config_data, sys.stdout)

    def call_listeners(self, key_path, value):
        if self.__listeners.__contains__(key_path) is False:
            return

        listeners = self.__listeners[key_path]
        for listener in listeners:
            if listener is not None:
                listener(key_path, value)

    def add_listener(self, key_path, func):
        if func is None:
            return

        if self.__listeners.__contains__(key_path) is False:
            self.__listeners[key_path] = []

        if self.__listeners[key_path].__contains__(func) is False:
            self.__listeners[key_path].append(func)

        pass

    def remove_listener(self, key_path, func):
        if func is None:
            return

        if self.__listeners.__contains__(key_path):
            if self.__listeners[key_path].__contains__(func):
                self.__listeners[key_path].remove(func)

        pass

    def dump_listeners(self, key_path=None):
        if key_path is not None:
            if self.__listeners.__contains__(key_path) is False:
                print(None)
            else:
                print(self.__listeners[key_path])
        else:
            print(self.__listeners)
        pass

    def __str__(self):
        return self.dump()

    pass

