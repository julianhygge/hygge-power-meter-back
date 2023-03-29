import time
from datetime import datetime, timedelta
import pytz
from dateutil import tz
from hyggepowermeter.data.power_meter_repository import power_meter_repository


class MeterDataProcessorService:
    def __init__(self):
        self.run_hourly_and_daily()

    @staticmethod
    def store_hourly_kwh():
        # Calculate the start and end times for the past hour
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_time = now_utc.replace(minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(hours=1)
        # Get the readings for the past hour
        readings = power_meter_repository.read_power_meter_readings(between=(start_time, end_time))

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

        power_meter_repository.insert_hourly_kwh(data)

    def run_hourly_and_daily(self):
        while True:
            now = datetime.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            sleep_time = (next_hour - now).total_seconds()
            time.sleep(sleep_time)
            self.store_hourly_kwh()
            # Check if it's time to store the daily kWh
            if now.hour == 23:
                self.store_daily_kwh()

    @staticmethod
    def store_daily_kwh():
        # Calculate the start and end times for the past day
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=1)

        # Get the readings for the past hour
        readings = power_meter_repository.read_power_meter_readings(between=(start_date, end_date))
        # Calculate the daily kWh
        # daily_kwh = sum([record[3] for record in hourly_kwh_records])
        # print(f"Daily kWh stored for {start_date.date()} - {end_date.date()}: {daily_kwh}")
