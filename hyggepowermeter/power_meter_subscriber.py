import logging
import sys
from pathlib import Path
from hyggepowermeter.configuration.mqtt_configuration import PowerMeterSubscriberConfiguration
from hyggepowermeter.mqtt.subscriber_client import PowerMeterSubscriberClient


def run_subscriber():
    config_path = str(Path.cwd()) + "/local.ini"
    for i, arg in enumerate(sys.argv):
        if arg == "-config":
            config_path = sys.argv[i + 1]
            break
    config = PowerMeterSubscriberConfiguration(config_path)
    mqtt_client = PowerMeterSubscriberClient(config)
    if mqtt_client:
        try:
            mqtt_client.listen()
            logging.info("Exiting")
        except BaseException as err:
            logging.exception(f"Unexpected exception, {type(err)} when connecting to mqtt server")
            raise
        finally:
            mqtt_client.client.disconnect()


if __name__ == '__main__':
    run_subscriber()
