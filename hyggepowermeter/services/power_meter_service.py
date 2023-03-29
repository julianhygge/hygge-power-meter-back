import sched
import time
from hyggepowermeter.hygge_logging.hygge_logging import logger


class PowerMeterService:
    def __init__(self):
        self.__priority = 1
        self.__delay = 0

    def read_meter_values(self, scheduler, meter):
        logger.info("Function: read_all_meter_values")
        scheduler.enter(meter.frequency_inst_sec, self.__priority, self.read_meter_values, (scheduler, meter))
        test_registers = meter.read_registers()
        logger.info("Registers:   " + str(test_registers))
        logger.info("Reading values every " + str(meter.frequency_inst_sec) + " seconds...")

    def read_values_in_meters(self, meters):
        my_scheduler = sched.scheduler(time.time, time.sleep)
        for meter in meters:
            logger.info(meter.meter_name)
            logger.info("Meter model: " + meter.meter_model)
            logger.info("Meter version: " + meter.meter_version)
            logger.info("Meter method: " + meter.method)

            my_scheduler.enter(self.__delay, self.__priority, self.read_meter_values, (my_scheduler, meter))

        my_scheduler.run()
