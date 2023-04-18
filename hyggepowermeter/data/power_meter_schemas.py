from datetime import datetime
from peewee import Model, IntegerField, FloatField, CharField, AutoField, DateTimeField, PostgresqlDatabase
from playhouse.postgres_ext import PostgresqlExtDatabase


class PostgresqlUTCDatabase(PostgresqlDatabase):
    def _connect(self, *args, **kwargs):
        conn = super(PostgresqlUTCDatabase, self)._connect(*args, **kwargs)
        cursor = conn.cursor()
        cursor.execute("SET TIME ZONE 'UTC';")
        cursor.close()
        return conn


db = PostgresqlUTCDatabase("power-meter")


class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def get_table_name(cls):
        return cls._meta.table_name


class PowerMeterBase(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    device_id = IntegerField()
    box_id = CharField(max_length=50)
    power = FloatField()


class PowerMeter(PowerMeterBase):
    current = FloatField()
    voltage = FloatField()

    class Meta:
        table_name = 'power_meter'
        schema = 'measurements'


class ProcessedReadings(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    last_processed_reading = IntegerField()
    processed_table = CharField(max_length=20)
    box_id = CharField(max_length=20)
    device_id = IntegerField()

    class Meta:
        table_name = 'processed_readings'
        schema = 'control'


class PowerMeterDevices(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    box_id = CharField(max_length=20)
    device_id = IntegerField()
    description = CharField(max_length=50)
    timezone = CharField(max_length=65, default='Asia/Kolkata')

    class Meta:
        table_name = 'powermeter_devices'
        schema = 'control'


class HourlyKwh(PowerMeterBase):
    class Meta:
        table_name = 'hourly_kwh'
        schema = 'measurements'
        indexes = (
            (('timestamp', 'device_id', 'box_id'), True),
        )


class DailyKwh(PowerMeterBase):
    class Meta:
        table_name = 'daily_kwh'
        schema = 'measurements'
        indexes = (
            (('timestamp', 'device_id', 'box_id'), True),
        )
