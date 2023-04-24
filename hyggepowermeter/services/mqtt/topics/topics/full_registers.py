import json
from types import SimpleNamespace

from hyggepowermeter.services.log.logger import logger
from hyggepowermeter.services.mqtt.topics.topic_base import TopicBase


class FullRegisters(TopicBase):
    def do_action(self, msg, db_client):
        power_meter_reading = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
        logger.info("Message received")
        meter_registers_dict = vars(power_meter_reading.meter_registers)
        data = {
            "box_id": power_meter_reading.box_id,
            "device_id": power_meter_reading.device_id,
            "timestamp": power_meter_reading.utc_timestamp,
            **meter_registers_dict,
        }
        # db_client.insert_full_registers(data)

