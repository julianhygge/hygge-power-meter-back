from peewee import Expression
from hyggepowermeter.data.power_meter_schemas import db, PowerMeter, HourlyKwh, DailyKwh, ProcessedReadings, \
    PowerMeterDevices
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
        self.__create_table_if_not_exists(ProcessedReadings)
        self.__create_table_if_not_exists(PowerMeterDevices)

    def insert_power_meter_reading(self, data):
        self.__insert(PowerMeter, data)

    def upsert_hourly_kwh(self, data):
        self.__upsert(HourlyKwh, data)

    def upsert_daily_kwh(self, data):
        self.__upsert(DailyKwh, data)

    @staticmethod
    def __upsert(model_class, data):
        query = (
            model_class
            .insert(data)
            .on_conflict(
                conflict_target=[model_class.timestamp, model_class.device_id, model_class.box_id],
                update={model_class.power: data['power']}
            )
        )
        query.execute()

    def insert_hourly_kwh(self, data):
        self.__insert(HourlyKwh, data)

    def insert_daily_kwh(self, data):
        self.__insert(DailyKwh, data)

    def read_power_meter_readings(self, filters=None, order_by=None, limit=None, between=None):
        self.__read(PowerMeter, filters, order_by, limit, between)

    def read_last_power_meter_readings(self, after_id, box_id, device_id):
        meter_reading_filter = Expression(PowerMeter.id, ">", after_id)
        box_filter = Expression(PowerMeter.box_id, "=", box_id)
        device_filter = Expression(PowerMeter.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter]
        meter_readings = self.__read(PowerMeter, filters=filters)
        return meter_readings

    def read_last_kwh_readings(self, after_id, box_id, device_id):
        meter_reading_filter = Expression(HourlyKwh.id, ">", after_id)
        box_filter = Expression(HourlyKwh.box_id, "=", box_id)
        device_filter = Expression(HourlyKwh.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter]
        meter_readings = self.__read(HourlyKwh, filters=filters)
        return meter_readings

    def read_last_hourly_kwh(self, after_id, box_id, device_id):
        meter_reading_filter = Expression(HourlyKwh.id, ">", after_id)
        box_filter = Expression(HourlyKwh.box_id, "=", box_id)
        device_filter = Expression(HourlyKwh.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter]
        meter_readings = self.__read(HourlyKwh, filters=filters)
        return meter_readings

    @staticmethod
    def insert_into_power_meter_table(voltage, current, timestamp, device_id, box_id):
        power = (current * voltage) / 1000
        PowerMeter.create(timestamp=timestamp, device_id=device_id, box_id=box_id, current=current, voltage=voltage,
                          power=power)

    def get_last_processed_meter_reading(self, box_id, device_id, table_type):
        processed_table_filter = Expression(ProcessedReadings.processed_table, "=", table_type)
        box_id_filter = Expression(ProcessedReadings.box_id, "=", box_id)
        device_id_filter = Expression(ProcessedReadings.device_id, "=", device_id)

        filters = [processed_table_filter, box_id_filter, device_id_filter]
        read_iter = self.__read(ProcessedReadings, filters=filters)

        if isinstance(read_iter, list):
            return read_iter[0] if read_iter else None
        elif hasattr(read_iter, '__iter__'):
            return next(iter(read_iter), None)
        else:
            return None

    def get_all_meter_devices(self):
        power_meter_devices = self.__read(PowerMeterDevices)
        return power_meter_devices

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

    @staticmethod
    def insert_processed_reading(data):
        # Try to get the record matching device_id, box_id, and processed_table
        record, created = ProcessedReadings.get_or_create(
            device_id=data["device_id"],
            box_id=data["box_id"],
            processed_table=data["processed_table"],
            defaults=data,
        )

        # If the record already exists, update it with the new values
        if not created:
            record.timestamp = data["timestamp"]
            record.last_processed_reading = data["last_processed_reading"]
            record.save()

# power_meter_repository = PowerMeterRepository(CONFIGURATION.db)
