from hyggepowermeter.data.power_meter_schemas import db, PowerMeter, HourlyKwh, DailyKwh
from hyggepowermeter.services.configuration.configuration import CONFIGURATION
from hyggepowermeter.services.log.logger import logger


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

    def insert_power_meter_reading(self, data):
        self.__insert(PowerMeter, data)

    def insert_hourly_kwh(self, data):
        self.__insert(HourlyKwh, data)

    def insert_daily_kwh(self, data):
        self.__insert(DailyKwh, data)

    def read_power_meter_readings(self, filters=None, order_by=None, limit=None, between=None):
        self.__read(PowerMeter, filters, order_by, limit, between)

    @staticmethod
    def __insert(table_class, data):
        try:
            with db.atomic():
                record = table_class.create(**data)
                logger.info(f"Inserted record with ID {record.id} into {table_class.get_table_name()}.")
                return record
        except Exception as e:
            logger.error(f"Error inserting record into {table_class.get_table_name()}: {e}")
            return None

    @staticmethod
    def __read(table_class, filters=None, order_by=None, limit=None, between=None):
        try:
            query = table_class.select()
            if filters:
                query = query.where(*filters)

            if between:
                start_time, end_time = between
                query = query.where((table_class.timestamp >= start_time) & (table_class.timestamp < end_time))

            if order_by:
                query = query.order_by(*order_by)

            if limit:
                query = query.limit(limit)

            records = list(query)
            logger.info(f"Read {len(records)} records from {table_class.get_table_name()}.")
            return records
        except Exception as e:
            logger.error(f"Error reading records from {table_class.get_table_name()}: {e}")
            return []

    @staticmethod
    def __create_table_if_not_exists(table_class):
        if not table_class.table_exists():
            table_class.create_table()
            logger.info(f"Table {table_class.get_table_name()} created.")
        else:
            logger.info(f"Table {table_class.get_table_name()} already exists.")

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
            logger.info(f"Schema {schema_name} created.")
        else:
            logger.info(f"Schema {schema_name} already exists.")


power_meter_repository = PowerMeterRepository(CONFIGURATION.db)
