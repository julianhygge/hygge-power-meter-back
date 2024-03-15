import threading
from hyggepowermeter.data.energy_system_repository import EnergySystemRepository
from hyggepowermeter.config.configuration import CONFIGURATION
from hyggepowermeter.services.meter_data_processor.meter_data_processor import MeterDataProcessorService
from hyggepowermeter.services.mqtt.subscriber_client import EnergySubscriberClient
from hyggepowermeter.services.studer_data_processor.studer_processor import StuderDataProcessor
from hyggepowermeter.utils.logger import logger


def run_subscriber():
    repository = EnergySystemRepository()
    mqtt_client = EnergySubscriberClient(CONFIGURATION, repository)
    meter_data_processor_service = MeterDataProcessorService(repository)
    studer_processor_service = StuderDataProcessor(repository)

    try:
        mqtt_thread = threading.Thread(target=mqtt_client.listen)
        mqtt_thread.start()

        studer_thread = threading.Thread(target=studer_processor_service.process_studer_data)
        studer_thread.start()

        meter_data_processor_thread = threading.Thread(target=meter_data_processor_service.run_hourly_and_daily)
        meter_data_processor_thread.start()

        mqtt_thread.join()
        meter_data_processor_thread.join()
        studer_thread.join()

        logger.info("Exiting")
    except BaseException as err:
        logger.exception(f"Unexpected exception, {type(err)} when connecting to mqtt server")
        raise
    finally:
        mqtt_client.client.disconnect()


if __name__ == '__main__':
    run_subscriber()
