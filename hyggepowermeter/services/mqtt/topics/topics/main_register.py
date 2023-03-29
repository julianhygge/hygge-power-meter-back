import json
from types import SimpleNamespace
from hyggepowermeter.data.power_meter_repository import power_meter_repository
from hyggepowermeter.services.mqtt.topics.topic_base import TopicBase


class MainRegisters(TopicBase):
    def do_action(self, msg,  config):
        power_meter_reading = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
        print(f'This is power meter reading, {msg.payload}')
        test = power_meter_repository
        # db_client.update_otp_status(booking.resource.bookingId, booking.resource.status)