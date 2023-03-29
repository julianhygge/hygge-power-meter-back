from datetime import datetime
from peewee import Model, IntegerField, FloatField, CharField, DateTimeField
from playhouse.postgres_ext import PostgresqlExtDatabase

db = PostgresqlExtDatabase("power-meter")


class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def get_table_name(cls):
        return cls._meta.table_name


class PowerMeter(BaseModel):
    id = IntegerField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    device_id = IntegerField()
    box_id = CharField(max_length=50)
    current = FloatField()
    voltage = FloatField()
    power = FloatField()

    class Meta:
        table_name = 'power_meter'
        schema = 'measurements'


class HourlyKwh(PowerMeter):
    class Meta:
        table_name = 'hourly_kwh'
        schema = 'measurements'


class DailyKwh(PowerMeter):
    class Meta:
        table_name = 'daily_kwh'
        schema = 'measurements'
