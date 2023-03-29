import logging
import sys
from pathlib import Path

from playhouse.postgres_ext import PostgresqlExtDatabase
from hyggepowermeter.data.power_meter_repository import PowerMeterRepository
from hyggepowermeter.services.configuration.configuration import PowerMeterSubscriberConfiguration
from hyggepowermeter.services.mqtt.subscriber_client import PowerMeterSubscriberClient

db = PostgresqlExtDatabase("power-meter", autorollback=True, autocreate=True)


def run_subscriber():
    config_path = str(Path.cwd()) + "/local.ini"
    for i, arg in enumerate(sys.argv):
        if arg == "-config":
            config_path = sys.argv[i + 1]
            break

    config = PowerMeterSubscriberConfiguration(config_path)
    power_meter_repository = PowerMeterRepository(config.db)
    mqtt_client = PowerMeterSubscriberClient(config, power_meter_repository)

    if mqtt_client:
        try:
            mqtt_client.listen()
            # power_meter_repository.insert_into_power_meter_table()
            logging.info("Exiting")
        except BaseException as err:
            logging.exception(f"Unexpected exception, {type(err)} when connecting to mqtt server")
            raise
        finally:
            mqtt_client.client.disconnect()


if __name__ == '__main__':
    run_subscriber()
