from pathlib import Path
import os
from configobj import ConfigObj


class PowerMeterSubscriberConfiguration:
    def __init__(self, file_path):
        self.config = ConfigObj(file_path)
        self.mqtt = self.__get_mqtt_config()
        self.db = self.__get_postgres_config()
        self.logging = self.__get_logging_config()

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

    def __get_postgres_config(self):
        data = self.config['postgres']
        temp_obj = self.ConfigObject()
        temp_obj.host = data["host"]
        temp_obj.port = int(data["port"])
        temp_obj.database = data["database"]
        temp_obj.user = data["user"]
        temp_obj.password = data["password"]
        temp_obj.options = data["options"]

        return temp_obj

    def __get_logging_config(self):
        data = self.config['logging']
        temp_obj = self.ConfigObject()
        temp_obj.level = data["level"]
        temp_obj.log_directory = data["log_directory"]
        return temp_obj

    class ConfigObject:
        pass


APP_ENV = os.environ.get("APP_ENV") or "local"

if APP_ENV == 'local':
    CONFIGURATION = PowerMeterSubscriberConfiguration(str(Path.cwd()) + "/services/configuration/{}.ini".format(APP_ENV))
else:
    CONFIGURATION = PowerMeterSubscriberConfiguration(str(Path.cwd()) + "/hyggepowermeter/services/configuration/{}.ini".format(APP_ENV))