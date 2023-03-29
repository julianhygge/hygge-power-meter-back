from datetime import datetime
from peewee import Model, IntegerField, FloatField, CharField, DateTimeField, AutoField
from playhouse.postgres_ext import PostgresqlExtDatabase

db = PostgresqlExtDatabase("power-meter")


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

    class Meta:
        table_name = 'processed_readings'
        schema = 'control'


class HourlyKwh(PowerMeterBase):
    class Meta:
        table_name = 'hourly_kwh'
        schema = 'measurements'


class DailyKwh(PowerMeterBase):
    class Meta:
        table_name = 'daily_kwh'
        schema = 'measurements'
