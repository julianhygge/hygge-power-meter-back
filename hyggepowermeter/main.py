from hyggepowermeter.meter_loader import MetersLoader
from hyggepowermeter.power_meter_subscriber import Subscriber
from hyggepowermeter.services.power_meter_service import PowerMeterService
from hyggepowermeter.hygge_logging.hygge_logging import logger


def run(meters, power_meter_service):
    logger.info("HYGGE POWER METER started...")
    power_meter_service.read_values_in_meters(meters)
    logger.info("HYGGE POWER METER finished...")


def main():
    subscriber = Subscriber()
    subscriber.run_subscriber()
    meters = MetersLoader()
    meter_service = PowerMeterService()
    run(meters.meter_instances_container, meter_service)


if __name__ == '__main__':
    main()


