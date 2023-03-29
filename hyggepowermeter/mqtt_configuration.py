import logging
import sys
from enum import Enum
from configobj import ConfigObj

logger = logging.getLogger('HYGGE BOOKING SUBSCRIBER')


class ErrorLevel(Enum):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class PowerMeterSubscriberConfiguration:
    def __init__(self, file_path):
        self.config = ConfigObj(file_path)
        # self.project_db_path = self.config["project_db_path"]
        self.mqtt = self.__get_mqtt_config()

    def __get_mqtt_config(self):
        data = self.config['mqtt']
        temp_obj = self.ConfigObject()
        temp_obj.username = data["username"]
        temp_obj.password = data["password"]
        temp_obj.id = data["id"]

        temp_obj.port = int(data["port"])
        temp_obj.host = data["host"]
        topics = self.config['topic']['topics']

        temp_obj.topics = []
        for t in topics:
            topic = self.ConfigObject()
            topic.topic = t.split(' ')[0]
            topic.qos = int(t.split(' ')[1])
            temp_obj.topics.append(topic)
        return temp_obj

    class ConfigObject:
        pass
