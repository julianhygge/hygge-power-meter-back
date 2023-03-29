from hyggepowermeter.services.configuration.configuration import CONFIGURATION
from hyggepowermeter.services.log.logger import logger
from hyggepowermeter.services.mqtt.subscriber_client import PowerMeterSubscriberClient


def run_subscriber():
    mqtt_client = PowerMeterSubscriberClient(CONFIGURATION)

    if mqtt_client:
        try:
            mqtt_client.listen()
            logger.info("Exiting")
        except BaseException as err:
            logger.exception(f"Unexpected exception, {type(err)} when connecting to mqtt server")
            raise
        finally:
            mqtt_client.client.disconnect()


if __name__ == '__main__':
    run_subscriber()
