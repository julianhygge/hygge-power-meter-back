from hyggepowermeter.data.power_meter_repository import PowerMeterRepository
from hyggepowermeter.services.configuration.configuration import CONFIGURATION
from hyggepowermeter.services.log.logger import logger
from hyggepowermeter.services.meter_data_processor_service.meter_data_processor import MeterDataProcessorService
from hyggepowermeter.services.mqtt.subscriber_client import PowerMeterSubscriberClient


def run_subscriber():
    power_meter_repository = PowerMeterRepository(CONFIGURATION.db)
    mqtt_client = PowerMeterSubscriberClient(CONFIGURATION, power_meter_repository)
    meter_data_processor_service = MeterDataProcessorService(power_meter_repository)

    # meter_data_processor_service.run_hourly_and_daily()

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
