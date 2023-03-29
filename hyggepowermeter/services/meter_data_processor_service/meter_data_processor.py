import time
from datetime import datetime, timedelta
import pytz
from dateutil import tz
from collections import defaultdict


class MeterDataProcessorService:
    def __init__(self, db_client):
        self.__db_client = db_client

    def __store_hourly_kwh(self):
        # Calculate the start and end times for the past hour
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_time = now_utc.replace(minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(hours=1)
        # Get the readings since last time
        reading = self.__db_client.get_last_processed_meter_reading()
        last_reading_id = 0
        if reading is not None:
            last_reading_id = reading.last_processed_reading

        readings = self.__db_client.read_last_power_meter_readings(after_id=last_reading_id)
        grouped_readings = self.group_readings_by_hour(readings)

        data = {
            "timestamp": end_time,
            "device_id": 111,
            "box_id": "box_1",
            "power": 5
        }

        self.__db_client.insert_hourly_kwh(data)

        # Calculate the hourly kWh
        kwh = 0
        num_readings = len(readings)
        total_time_span = (datetime.strptime(readings[-1][2], "%Y-%m-%d %H:%M:%S") -
                           datetime.strptime(readings[0][2], "%Y-%m-%d %H:%M:%S")).total_seconds()
        average_time_interval = total_time_span / (num_readings - 1)

        for reading in readings:
            voltage, current = reading[3], reading[4]
            power = voltage * current
            kwh += (power / 1000) * (average_time_interval / 3600)  # Assuming power is in W

        data = {
            "timestamp": end_time,
            "device_id": 111,
            "box_id": "box_1",
            "power": kwh
        }

        self.__db_client.insert_hourly_kwh(data)

    def run_hourly_and_daily(self):
        while True:
            now = datetime.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            sleep_time = (next_hour - now).total_seconds()
            sleep_time = 10
            time.sleep(sleep_time)
            self.__store_hourly_kwh()
            # Check if it's time to store the daily kWh
            if now.hour == 23:
                self.__store_daily_kwh()

    def __store_daily_kwh(self):
        # Calculate the start and end times for the past day
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=1)

        # Get the readings for the past hour
        readings = self.__db_client.read_power_meter_readings(between=(start_date, end_date))
        # Calculate the daily kWh
        # daily_kwh = sum([record[3] for record in hourly_kwh_records])
        # print(f"Daily kWh stored for {start_date.date()} - {end_date.date()}: {daily_kwh}")

    @staticmethod
    def group_readings_by_hour(readings):
        grouped_readings = defaultdict(list)

        for reading in readings:
            hour = reading.timestamp.hour
            grouped_readings[hour].append(reading)

        return grouped_readings
