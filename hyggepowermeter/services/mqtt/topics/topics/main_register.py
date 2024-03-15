import json
from types import SimpleNamespace
from hyggepowermeter.services.mqtt.topics.topic_base import TopicBase
from hyggepowermeter.utils.logger import logger


class MainRegisters(TopicBase):
    def do_action(self, msg, db_client):
        power_meter_reading = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
        logger.info("Message received")
        rms_l1_voltage = power_meter_reading.meter_registers.rms_l1_voltage
        rms_l1_current_ch1 = power_meter_reading.meter_registers.rms_l1_current_ch1
        power = (rms_l1_voltage * rms_l1_current_ch1) / 1000
        data = {
            "box_id": power_meter_reading.box_id,
            "device_id": power_meter_reading.device_id,
            "timestamp": power_meter_reading.utc_timestamp,
            "power": power,
            "current": rms_l1_current_ch1,
            "voltage": rms_l1_voltage
        }

        db_client.insert_into_power_meter_table(data)
