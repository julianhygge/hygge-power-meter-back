import json
from types import SimpleNamespace

from hyggepowermeter.services.log.logger import logger
from hyggepowermeter.services.mqtt.topics.topic_base import TopicBase


class StuderRegisters(TopicBase):
    def do_action(self, msg, db_client):
        power_meter_reading = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
        logger.info("Message received")
        meter_reading_dict = vars(power_meter_reading)
        messages = meter_reading_dict['messages']

        device_id_list = []
        for msg in messages:
            if msg.device_id not in device_id_list:
                device_id_list.append(msg.device_id)

        for device_id in device_id_list:
            inverter_data = {}
            bsp_data = {}
            vt_data = {}
            for msg in messages:
                if device_id == msg.device_id:
                    if 'xt_' in msg.name:
                        inverter_data['device_id'] = device_id
                        inverter_data['timestamp'] = msg.time_stamp
                        inverter_data[msg.name] = msg.value
                    if 'vt_' in msg.name:
                        vt_data['device_id'] = device_id
                        vt_data['timestamp'] = msg.time_stamp
                        vt_data[msg.name] = msg.value
                    if 'bsp_' in msg.name:
                        bsp_data['device_id'] = device_id
                        bsp_data['timestamp'] = msg.time_stamp
                        bsp_data[msg.name] = msg.value

            if bool(inverter_data):
                db_client.insert_inverter_reading(inverter_data)
            if bool(vt_data):
                db_client.insert_vario_track_reading(vt_data)
            if bool(bsp_data):
                db_client.insert_bsp_reading(bsp_data)



