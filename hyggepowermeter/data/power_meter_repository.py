from peewee import Expression
from hyggepowermeter.data.power_meter_schemas import db, PowerMeter, HourlyKwh, DailyKwh, ProcessedReadings
from hyggepowermeter.services.log.logger import logger


class PowerMeterRepository:
    def __init__(self, db_config):
        db.init(database=db_config.database,
                host=db_config.host,
                port=db_config.port,
                user=db_config.user,
                password=db_config.password)
        self.__create_schema_if_not_exists('measurements')
        self.__create_schema_if_not_exists('control')
        self.__create_table_if_not_exists(PowerMeter)
        self.__create_table_if_not_exists(DailyKwh)
        self.__create_table_if_not_exists(HourlyKwh)
        self.__create_table_if_not_exists(ProcessedReadings)

    def insert_power_meter_reading(self, data):
        self.__insert(PowerMeter, data)

    def insert_hourly_kwh(self, data):
        self.__insert(HourlyKwh, data)

    def insert_daily_kwh(self, data):
        self.__insert(DailyKwh, data)

    def read_power_meter_readings(self, filters=None, order_by=None, limit=None, between=None):
        self.__read(PowerMeter, filters, order_by, limit, between)

    def read_last_power_meter_readings(self, after_id):
        meter_reading_filter = Expression(PowerMeter.id, ">", after_id)
        filters = [meter_reading_filter]
        meter_readings = self.__read(PowerMeter, filters=filters)
        return meter_readings

    @staticmethod
    def insert_into_power_meter_table(voltage, current, timestamp, device_id, box_id):
        power = (current * voltage) / 1000
        PowerMeter.create(timestamp=timestamp, device_id=device_id, box_id=box_id, current=current, voltage=voltage,
                          power=power)

    def get_last_processed_meter_reading(self):
        processed_table_filter = Expression(ProcessedReadings.processed_table, "=", "meter_readings")
        filters = [processed_table_filter]
        read_iter = self.__read(ProcessedReadings, filters=filters)

        if isinstance(read_iter, list):
            return read_iter[0] if read_iter else None
        elif hasattr(read_iter, '__iter__'):
            return next(iter(read_iter), None)
        else:
            return None


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
    def __read(table_class, filters=None, order_by=None, limit=None, between=None, as_iterator=False):
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

            if as_iterator:
                return query.iterator()

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

# power_meter_repository = PowerMeterRepository(CONFIGURATION.db)
