import logging
import sys
from pathlib import Path
from hyggepowermeter.mqtt_configuration import PowerMeterSubscriberConfiguration
from subscriber_client import PowerMeterSubscriberClient


class Subscriber:
    @staticmethod
    def run_subscriber():
        config_path = str(Path.cwd()) + "/local.ini"
        for i, arg in enumerate(sys.argv):
            if arg == "-config":
                config_path = sys.argv[i + 1]
                break
        config = PowerMeterSubscriberConfiguration(config_path)

        # ev_charger_db = EvChargerDb(config.project_db_path)
        # mqtt_client = BookingSubscriberClient(config, ev_charger_db)
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
