import json
from types import SimpleNamespace
from hyggepowermeter.data.power_meter_repository import power_meter_repository
from hyggepowermeter.services.log.logger import logger
from hyggepowermeter.services.mqtt.topics.topic_base import TopicBase


class MainRegisters(TopicBase):
    def do_action(self, msg, config):
        power_meter_reading = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
        logger.info(f'This is power meter reading, {msg.payload}')
        # power_meter_repository.insert_power_meter_reading()
