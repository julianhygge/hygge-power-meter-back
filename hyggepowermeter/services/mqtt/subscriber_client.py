from hyggepowermeter.services.mqtt.mqtt_base_client import MQTTClient
from hyggepowermeter.services.mqtt.topics.topics_factory import TopicFactory
from hyggepowermeter.utils.logger import logger


class EnergySubscriberClient(MQTTClient):
    def on_message(self, _, __, msg):
        try:
            topic = TopicFactory.get_topic_subscriber(msg.topic)
            topic.do_action(msg, self._db_client)
        except BaseException as err:
            logger.exception(str(err))

    def __init__(self, config, power_meter_db):
        super().__init__(config.mqtt)
        self.client.on_message = self.on_message
        self.client_id = config.mqtt.id
        self._db_client = power_meter_db
        self.config = config
