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


class PowerMeterRepository:
    def __init__(self, db_config):
        db.init(database=db_config.database,
                host=db_config.host,
                port=db_config.port,
                user=db_config.user,
                password=db_config.password)
        self.__create_schema_if_not_exists('measurements')
        self.__create_table_if_not_exists(PowerMeter)
        self.__create_table_if_not_exists(DailyKwh)
        self.__create_table_if_not_exists(HourlyKwh)

    @staticmethod
    def __create_table_if_not_exists(table_class):
        if not table_class.table_exists():
            table_class.create_table()
            print(f"Table {table_class.get_table_name()} created.")
        else:
            print(f"Table {table_class.get_table_name()} already exists.")

    @staticmethod
    def __create_schema_if_not_exists(schema_name):
        schema_exists_query = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_name}'"

        with db.atomic():
            cursor = db.cursor()
            cursor.execute(schema_exists_query)
            schema_exists = cursor.fetchone()

        if not schema_exists:
            create_schema_query = f"CREATE SCHEMA {schema_name}"
            db.execute_sql(create_schema_query)
            print(f"Schema {schema_name} created.")
        else:
            print(f"Schema {schema_name} already exists.")

