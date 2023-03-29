import json
from types import SimpleNamespace

from hyggepowermeter.services.mqtt.topics.topic_base import TopicBase


class MainRegisters(TopicBase):
    def do_action(self, msg, db_client, config):
        power_meter_reading = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
        rms_l1_voltage = power_meter_reading.meter_registers.rms_l1_voltage
        rms_l1_current_ch1 = power_meter_reading.meter_registers.rms_l1_current_ch1
        db_client.insert_into_power_meter_table(rms_l1_voltage, rms_l1_current_ch1, power_meter_reading.utc_timestamp,
                                                power_meter_reading.device_id, power_meter_reading.box_id)

