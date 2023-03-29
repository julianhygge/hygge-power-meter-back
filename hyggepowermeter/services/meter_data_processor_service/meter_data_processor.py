import time
from datetime import datetime, timedelta
import pytz
from dateutil import tz

from hyggepowermeter.data.power_meter_repository import power_meter_repository


class MeterDataProcessorService:
    def __init__(self):
        pass

    @staticmethod
    def store_hourly_kwh():

        # Calculate the start and end times for the past hour
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_time = now_utc.replace(minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(hours=1)

        # Get the readings for the past hour
        readings = power_meter_repository.read_power_meter_readings

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

        # # Store the hourly kWh in the new table
        # cursor.execute(f"INSERT INTO {table_name} (device_id, timestamp, kwh) VALUES (?, ?, ?)",
        #                (readings[0][1], end_time, kwh))
        # conn.commit()
        # conn.close()
        #
        # print(f"Hourly kWh stored for {start_time} - {end_time}: {kwh}")

    def run_hourly_and_daily(hourly_func, daily_func, db_name, hourly_table_name, daily_table_name):
        while True:
            now = datetime.now()
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            sleep_time = (next_hour - now).total_seconds()
            time.sleep(sleep_time)
            hourly_func(db_name, hourly_table_name)
            # Check if it's time to store the daily kWh
            if now.hour == 23:
                daily_func(db_name, hourly_table_name, daily_table_name)

    def store_daily_kwh(db_name, hourly_table_name, daily_table_name):
        db = db_name + ".db"
        conn = sqlite3.connect(db)

        # Calculate the start and end times for the past day
        now = datetime.now()
        local_tz = tz.tzlocal()
        now_utc = now.replace(tzinfo=local_tz).astimezone(pytz.utc)
        end_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=1)

        # Get the hourly kWh for the past day
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {hourly_table_name} WHERE timestamp >= ? AND timestamp < ?",
                       (start_date, end_date))
        hourly_kwh_records = cursor.fetchall()

        # Calculate the daily kWh
        daily_kwh = sum([record[3] for record in hourly_kwh_records])

        # Store the daily kWh in the new table
        cursor.execute(f"INSERT INTO {daily_table_name} (device_id, date, kwh) VALUES (?, ?, ?)",
                       (hourly_kwh_records[0][1], end_date.date(), daily_kwh))
        conn.commit()
        conn.close()

        print(f"Daily kWh stored for {start_date.date()} - {end_date.date()}: {daily_kwh}")

    def create_table_if_not_exists(db_name, table_name):
        db = db_name + ".db"
        conn = sqlite3.connect(db)

        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone()

        if not table_exists:
            cursor.execute(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                device_id INTEGER,
                date DATE,
                kwh REAL
            );
            """)
            conn.commit()
            print(f"Table {table_name} created.")
        else:
            print(f"Table {table_name} already exists.")

        conn.close()
