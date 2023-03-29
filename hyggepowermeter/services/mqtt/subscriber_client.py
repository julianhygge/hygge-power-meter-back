from hyggepowermeter.services.configuration.configuration import PowerMeterSubscriberConfiguration
from hyggepowermeter.services.mqtt.mqtt_base_client import MQTTClient
from hyggepowermeter.services.log.logger import logger
from hyggepowermeter.services.mqtt.topics.topics_factory import TopicFactory


class PowerMeterSubscriberClient(MQTTClient):
    def on_message(self, _, __, msg):
        try:
            topic = TopicFactory.get_topic_subscriber(msg.topic)
            topic.do_action(msg, self.config)
        except BaseException as err:
            logger.exception(str(err))

    def __init__(self, config: PowerMeterSubscriberConfiguration):
        super().__init__(config.mqtt)
        self.client.on_message = self.on_message
        self.client_id = config.mqtt.id
        # self._db_client = ev_db
        self.config = config
