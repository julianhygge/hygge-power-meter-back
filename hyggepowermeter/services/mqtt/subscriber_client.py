from hyggepowermeter.data.power_meter_repository import  PowerMeterRepository
from hyggepowermeter.services.configuration.configuration import PowerMeterSubscriberConfiguration
from hyggepowermeter.services.mqtt.mqtt_base_client import MQTTClient
import logging
from hyggepowermeter.services.mqtt.topics.topics_factory import TopicFactory


class PowerMeterSubscriberClient(MQTTClient):
    def on_message(self, _, __, msg):
        try:
            topic = TopicFactory.get_topic_subscriber(msg.topic)
            topic.do_action(msg, self._db_client, self.config)
            # topic.do_action(msg, self.config)
        except BaseException as err:
            logging.exception(str(err))

    # def __init__(self, config: BookingSubscriberConfiguration, ev_db: EvChargerDb):
    def __init__(self, config: PowerMeterSubscriberConfiguration, power_meter_db):
        super().__init__(config.mqtt)
        self.client.on_message = self.on_message
        self.client_id = config.mqtt.id
        self._db_client = power_meter_db
        self.config = config
