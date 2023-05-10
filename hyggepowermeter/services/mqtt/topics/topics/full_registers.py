import json
from types import SimpleNamespace
from hyggepowermeter.services.mqtt.topics.topic_base import TopicBase
from hyggepowermeter.utils.logger import logger


class FullRegisters(TopicBase):
    def do_action(self, msg, db_client):
        power_meter_reading = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
        # print(power_meter_reading)
        logger.info("Message received")
        meter_registers_dict = vars(power_meter_reading.meter_registers)
        lab_data = {
            "box_id": power_meter_reading.box_id,
            "device_id": power_meter_reading.device_id,
            "timestamp": power_meter_reading.utc_timestamp,
            "current": meter_registers_dict['rms_l1_current_ch1'],
            "voltage": meter_registers_dict['rms_l1_voltage']
        }
        lab_data["power"] = (lab_data["current"]*lab_data["voltage"])/1000
        school_data = {
            "box_id": power_meter_reading.box_id,
            "device_id": power_meter_reading.device_id,
            "timestamp": power_meter_reading.utc_timestamp,
            "current": meter_registers_dict['rms_l1_current_ch2'],
            "voltage": meter_registers_dict['rms_l1_voltage']
        }

        school_data["power"] = (school_data["current"] * school_data["voltage"]) / 1000

        data = {
            "box_id": power_meter_reading.box_id,
            "device_id": power_meter_reading.device_id,
            "timestamp": power_meter_reading.utc_timestamp,
            **meter_registers_dict,
        }
        db_client.insert_full_registers(data)
        db_client.insert_school_meter_reading(school_data)
        db_client.insert_lab_meter_reading(lab_data)
