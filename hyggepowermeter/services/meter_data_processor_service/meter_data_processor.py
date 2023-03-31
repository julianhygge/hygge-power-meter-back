import time
from datetime import datetime, timedelta
import pytz
from dateutil import tz
from collections import defaultdict


class MeterDataProcessorService:
    def __init__(self, db_client):
        self.__db_client = db_client
        self.__run_next_hour = False
        self.__run_next_day = False

    def __store_hourly_kwh(self):
        # Calculate the start and end times for the past hour
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_time = now_utc.replace(minute=0, second=0, microsecond=0)
        power_meter_devices = self.__db_client.get_all_meter_devices()
        processed_table = "meter_readings"

        for device in power_meter_devices:
            # Get the readings since last time
            reading = self.__db_client.get_last_processed_meter_reading(box_id=device.box_id,
                                                                        device_id=device.device_id,
                                                                        table_type=processed_table)
            last_reading_id = 0
            if reading is not None:
                last_reading_id = reading.last_processed_reading

            readings = self.__db_client.read_last_power_meter_readings(after_id=last_reading_id,
                                                                       box_id=device.box_id,
                                                                       device_id=device.device_id)

            if not any(readings):
                return

            grouped_readings = self.group_readings_by_hour(readings)
            hour = 0
            last_hour = None
            for (hour, box_id, device_id), readings_group in grouped_readings.items():
                # Calculate the hourly kWh
                kwh = self.calculate_kwh(readings_group)
                timestamp = end_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                data = {
                    "timestamp": timestamp + timedelta(hours=1),
                    "device_id": device_id,
                    "box_id": box_id,
                    "power": kwh
                }

                self.__db_client.upsert_hourly_kwh(data)
                last_hour = hour

            last_item = grouped_readings[last_hour, device.box_id, device.device_id][-1]

            data = {
                "timestamp":
                    last_item.timestamp.replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(hours=1),
                "last_processed_reading": last_item.id,
                "processed_table": processed_table,
                "box_id": device.box_id,
                "device_id": device.device_id
            }

            if self.__run_next_hour:
                self.__db_client.insert_processed_reading(data)
                self.__run_next_hour = False

    def run_hourly_and_daily(self):
        while True:
            now = datetime.utcnow()
            time.sleep(60)
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            sleep_time = (next_hour - now).total_seconds()
            if sleep_time < 60:
                time.sleep(sleep_time)
                self.__run_next_hour = True
            self.__store_hourly_kwh()
            # Check if it's time to store the daily kWh
            if now.hour == 23:  # 23:
                self.__run_next_day = True
            self.__store_daily_kwh()

    def __store_daily_kwh(self):
        # Calculate the start and end times for the past hour
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_time = now_utc.replace(minute=0, second=0, microsecond=0)
        power_meter_devices = self.__db_client.get_all_meter_devices()

        for device in power_meter_devices:
            processed_table = "hourly_kwh"
            # Get the readings since last time
            reading = self.__db_client.get_last_processed_meter_reading(box_id=device.box_id,
                                                                        device_id=device.device_id,
                                                                        table_type=processed_table
                                                                        )
            last_reading_id = 0
            if reading is not None:
                last_reading_id = reading.last_processed_reading

            readings = self.__db_client.read_last_kwh_readings(after_id=last_reading_id,
                                                               box_id=device.box_id,
                                                               device_id=device.device_id)

            if not any(readings):
                return

            grouped_readings = self.group_readings_by_day(readings)

            last_day = None
            for (day, box_id, device_id), readings_group in grouped_readings.items():
                kwh = self.calculate_total_kwh(readings_group)
                timestamp = end_time.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
                data = {
                    "timestamp": timestamp,
                    "device_id": device_id,
                    "box_id": box_id,
                    "power": kwh
                }

                self.__db_client.upsert_daily_kwh(data)
                last_day = day

            last_item = grouped_readings[last_day, device.box_id, device.device_id][-1]

            data = {
                "timestamp":
                    last_item.timestamp.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
                "last_processed_reading": last_item.id,
                "processed_table": processed_table,
                "box_id": device.box_id,
                "device_id": device.device_id
            }
            if self.__run_next_day:
                self.__db_client.insert_processed_reading(data)
                self.__run_next_day = False

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
            day = reading.timestamp.day
            box_id = reading.box_id
            device_id = reading.device_id
            group_key = (day, box_id, device_id)

            grouped_readings[group_key].append(reading)

        # Sort the dictionary by hour
        sorted_grouped_readings = dict(sorted(grouped_readings.items(), key=lambda x: x[0][0]))

        return sorted_grouped_readings

    @staticmethod
    def group_readings_by_hour(readings):
        grouped_readings = defaultdict(list)

        for reading in readings:
            hour = reading.timestamp.hour
            box_id = reading.box_id
            device_id = reading.device_id
            group_key = (hour, box_id, device_id)

            grouped_readings[group_key].append(reading)

        # Sort the dictionary by hour
        sorted_grouped_readings = dict(sorted(grouped_readings.items(), key=lambda x: x[0][0]))

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

        total_energy_in_kwh = avg_power/1000

        return total_energy_in_kwh
