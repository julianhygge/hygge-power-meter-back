import time
import paho.mqtt.client as mqtt
import socket
from hyggepowermeter.utils.logger import logger

MAX_ATTEMPTS = 360
RETRY_INTERVAL = 10


class MQTTClient(object):
    """base mqtt hygge client - server connection"""

    def __init__(self, config):
        self.client = mqtt.Client(client_id=config.id, clean_session=True)
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        self.client.enable_logger(logger)
        self.disconnected = True

        self.config = config
        self.client_id = config.id
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_publish = self._on_publish
        self.client.on_disconnect = self._on_disconnect
        self.topics = []

        self.client.username_pw_set(config.username, config.password)
        try:
            self.client.connect(config.host, config.port)
            self.disconnected = False
            for topic in config.topics:
                self.topics.append(topic.topic)
        except Exception as e:
            logger.error(f"Failed to connect {self.client_id}: {e}")

    def _on_connect(self, _, __, flags, rc):
        self.disconnected = False
        logger.info(
            f"Connected {self.client_id}, result code: {str(rc)} {str(flags)}")
        for topic in self.topics:
            self.client.subscribe(topic)

    def _on_subscribe(self, _, __, mid, granted_qos):
        logger.info(
            f"Subscribed {self.client_id}, mid: {mid}, granted qos: {granted_qos}")
        logger.info(
            f"Listening for {self.client_id}  messages, topics: {str(self.topics)}")

    def _on_disconnect(self, _, rc, properties=None):
        logger.info("Disconnected, result code: " + str(rc))

        self.disconnected = True
        attempts = 0
        while self.disconnected and attempts < MAX_ATTEMPTS:
            try:
                self.client.reconnect()
                self.disconnected = False
                attempts = 0
            except socket.error as e:
                logger.info("Reconnection failed: " + str(e))
                attempts += 1
                time.sleep(RETRY_INTERVAL)
        if self.disconnected and attempts == MAX_ATTEMPTS:
            logger.info("Reconnection failed after " + str(MAX_ATTEMPTS) + " attempts")
            self.client.loop_stop()

    def _on_publish(self, _, __, mid):
        logger.info(f"Published by {self.client_id}, mid: {mid}")

    def listen(self):
        try:
            while True:
                if not self.disconnected:
                    self.client.loop(timeout=1.0)
        except KeyboardInterrupt:
            logger.info(f"Received KeyboardInterrupt, disconnecting {self.config.mqtt.id}")
            try:
                self.client.disconnect()
            except socket.error as e:
                logger.info(f"Disconnection failed: {e}")
                try:
                    self.client.reconnect()
                except socket.error as e:
                    logger.info(f"Reconnection failed: {e}")
                    self.client.loop_stop()
