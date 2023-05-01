import time
from datetime import datetime, timedelta
import pytz
from collections import defaultdict


class MeterDataProcessorService:
    def __init__(self, db_client):
        self.__db_client = db_client

    def __store_hourly_kwh(self):
        power_meter_devices = self.__db_client.get_all_meter_devices()

        for device in power_meter_devices:
            # Get the readings since last time

            loads = self.__db_client.get_all_loads_by_box_id(box_id=device.box_id)
            for load in loads:
                reading = self.__db_client.get_last_processed_meter_reading(box_id=device.box_id,
                                                                            device_id=device.device_id,
                                                                            table_type=load.measurements_table)
                last_reading_id = 0
                if reading is not None:
                    last_reading_id = reading.last_processed_reading

                # for now, I am querying a specific table, but it should be same table by load id
                readings = self.__db_client.read_last_power_meter_readings(table_name=load.measurements_table,
                                                                           after_id=last_reading_id,
                                                                           box_id=device.box_id,
                                                                           device_id=device.device_id
                                                                           )

                if not any(readings):
                    continue

                readings = self.convert_timestamps(readings, device.timezone)

                grouped_readings = self.group_readings_by_hour(readings)
                year, month, day, hour = 0, 0, 0, 0
                last_hour = None
                for key, readings_group in grouped_readings.items():
                    (year, month, day, hour, box_id, device_id) = key
                    kwh = self.calculate_kwh(readings_group)
                    last_time = readings_group[-1].timestamp
                    timestamp = last_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                    timestamp = timestamp.astimezone(pytz.utc)

                    data = {
                        "timestamp": timestamp,
                        "device_id": device_id,
                        "box_id": box_id,
                        "power": kwh,
                        "load_id": load.id
                    }

                    self.__db_client.upsert_hourly_kwh(data)
                    last_hour = hour

                last_item = grouped_readings[year, month, day, last_hour, device.box_id, device.device_id][-1]

                data = {
                    "timestamp":
                        last_item.timestamp.replace(hour=hour, minute=0, second=0, microsecond=0),
                    "last_processed_reading": last_item.id,
                    "processed_table": load.measurements_table,
                    "box_id": device.box_id,
                    "device_id": device.device_id,
                    "load_id": load.id
                }

                ist_tz = pytz.timezone(device.timezone)  # we need to change logic when we have more time zones
                now_aware_of_time_zone = datetime.utcnow().astimezone(ist_tz)
                next_hour = now_aware_of_time_zone.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                sleep_time = (next_hour - now_aware_of_time_zone).total_seconds()
                if sleep_time < 60:
                    self.__db_client.insert_processed_reading(data)

    def run_hourly_and_daily(self):
        while True:
            self.__store_hourly_kwh()
            self.__store_daily_kwh()
            time.sleep(60)

    def __store_daily_kwh(self):
        power_meter_devices = self.__db_client.get_all_meter_devices()
        processed_table = "hourly_kwh"
        for device in power_meter_devices:

            loads = self.__db_client.get_all_loads_by_box_id(box_id=device.box_id)
            for load in loads:
                # Get the readings since last time
                reading = self.__db_client.get_last_processed_meter_reading(box_id=device.box_id,
                                                                            device_id=device.device_id,
                                                                            table_type=processed_table,
                                                                            load_id=load.id
                                                                            )
                last_reading_id = 0
                if reading is not None:
                    last_reading_id = reading.last_processed_reading

                readings = self.__db_client.read_last_kwh_readings(load_id=load.id,
                                                                   after_id=last_reading_id,
                                                                   box_id=device.box_id,
                                                                   device_id=device.device_id)

                if not any(readings):
                    continue

                readings = self.convert_timestamps(readings, device.timezone)

                grouped_readings = self.group_readings_by_day(readings)

                last_day = None
                year, month = 0, 0
                for (year, month, day, box_id, device_id), readings_group in grouped_readings.items():
                    kwh = self.calculate_total_kwh(readings_group)
                    last_time = readings_group[-1].timestamp
                    timestamp = last_time.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
                    timestamp = timestamp.astimezone(pytz.utc)
                    data = {
                        "timestamp": timestamp,
                        "device_id": device_id,
                        "box_id": box_id,
                        "power": kwh,
                        "load_id": load.id
                    }

                    self.__db_client.upsert_daily_kwh(data)
                    last_day = day

                last_item = grouped_readings[year, month, last_day, device.box_id, device.device_id][-1]

                data = {
                    "timestamp":
                        last_item.timestamp.replace(hour=0, minute=0, second=0, microsecond=0),
                    "last_processed_reading": last_item.id,
                    "processed_table": processed_table,
                    "box_id": device.box_id,
                    "device_id": device.device_id,
                    "load_id": load.id
                }

                device_timezone = pytz.timezone(device.timezone)
                now_aware_of_time_zone = datetime.utcnow().astimezone(device_timezone)
                if now_aware_of_time_zone.hour == 23:  # 23:
                    self.__db_client.insert_processed_reading(data)

    @staticmethod
    def calculate_total_kwh(hourly_kwh_list) -> float:
        total_kwh = 0

        for hourly_kwh in hourly_kwh_list:
            total_kwh += hourly_kwh.power

        return total_kwh

    @staticmethod
    def group_readings_by_day(readings):
        grouped_readings = defaultdict(list)

        for reading in readings:
            year = reading.timestamp.year
            month = reading.timestamp.month
            day = reading.timestamp.day
            box_id = reading.box_id
            device_id = reading.device_id
            group_key = (year, month, day, box_id, device_id)

            grouped_readings[group_key].append(reading)

        # Sort the dictionary by year, month, and day
        sorted_grouped_readings = dict(sorted(grouped_readings.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])))

        return sorted_grouped_readings

    @staticmethod
    def group_readings_by_hour(readings):
        grouped_readings = defaultdict(list)

        for reading in readings:
            year = reading.timestamp.year
            month = reading.timestamp.month
            day = reading.timestamp.day
            hour = reading.timestamp.hour
            box_id = reading.box_id
            device_id = reading.device_id
            group_key = (year, month, day, hour, box_id, device_id)

            grouped_readings[group_key].append(reading)

        # Sort the dictionary by year, month, day, and hour
        sorted_grouped_readings = dict(
            sorted(grouped_readings.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3])))

        return sorted_grouped_readings

    @staticmethod
    def calculate_kwh(readings_by_hour):
        n_readings = len(readings_by_hour)

        if n_readings == 0:
            return 0

        # Calculate average power for available readings
        total_power = 0
        for reading in readings_by_hour:
            power = reading.voltage * reading.current
            total_power += power
        avg_power = total_power / n_readings

        total_energy_in_kwh = avg_power / 1000

        return total_energy_in_kwh

    @staticmethod
    def convert_timestamps(readings, target_timezone):
        time_zone = pytz.timezone(target_timezone)
        for r in readings:
            r.timestamp = r.timestamp.replace(tzinfo=pytz.utc).astimezone(time_zone)
        return readings
