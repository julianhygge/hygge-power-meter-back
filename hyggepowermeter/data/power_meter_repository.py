from peewee import Expression
from hyggepowermeter.data.power_meter_schemas import db, PowerMeter, HourlyKwh, DailyKwh, ProcessedReadings, \
    PowerMeterDevices, MeterFullRegisters, SchoolMeters, LabMeters
from hyggepowermeter.data.repository_base import RepositoryBase


class PowerMeterRepository(RepositoryBase):
    def __init__(self, db_config):
        super().__init__(db_config)
        db.init(database=db_config.database,
                host=db_config.host,
                port=db_config.port,
                user=db_config.user,
                password=db_config.password)
        self._create_schema_if_not_exists('measurements')
        self._create_schema_if_not_exists('control')
        self._create_table_if_not_exists(PowerMeter)
        self._create_table_if_not_exists(DailyKwh)
        self._create_table_if_not_exists(HourlyKwh)
        self._create_table_if_not_exists(ProcessedReadings)
        self._create_table_if_not_exists(ProcessedReadings)
        self._create_table_if_not_exists(PowerMeterDevices)
        self._create_table_if_not_exists(MeterFullRegisters)
        self._create_table_if_not_exists(SchoolMeters)
        self._create_table_if_not_exists(LabMeters)

    def insert_power_meter_reading(self, data):
        self._insert(PowerMeter, data)

    def insert_school_meter_reading(self, data):
        self._insert(SchoolMeters, data)

    def insert_lab_meter_reading(self, data):
        self._insert(LabMeters, data)

    def upsert_hourly_kwh(self, data):
        self._upsert(HourlyKwh, data)

    def upsert_daily_kwh(self, data):
        self._upsert(DailyKwh, data)

    @staticmethod
    def _upsert(model_class, data):
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
        self._insert(HourlyKwh, data)

    def insert_daily_kwh(self, data):
        self._insert(DailyKwh, data)

    def insert_full_registers(self, data):
        self._insert(MeterFullRegisters, data)

    def read_power_meter_readings(self, filters=None, order_by=None, limit=None, between=None):
        self._read(PowerMeter, filters, order_by, limit, between)

    def read_last_power_meter_readings(self, after_id, box_id, device_id):
        meter_reading_filter = Expression(PowerMeter.id, ">", after_id)
        box_filter = Expression(PowerMeter.box_id, "=", box_id)
        device_filter = Expression(PowerMeter.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter]
        meter_readings = self._read(PowerMeter, filters=filters)
        return meter_readings

    def read_last_kwh_readings(self, after_id, box_id, device_id):
        meter_reading_filter = Expression(HourlyKwh.id, ">", after_id)
        box_filter = Expression(HourlyKwh.box_id, "=", box_id)
        device_filter = Expression(HourlyKwh.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter]
        meter_readings = self._read(HourlyKwh, filters=filters)
        return meter_readings

    def read_last_hourly_kwh(self, after_id, box_id, device_id):
        meter_reading_filter = Expression(HourlyKwh.id, ">", after_id)
        box_filter = Expression(HourlyKwh.box_id, "=", box_id)
        device_filter = Expression(HourlyKwh.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter]
        meter_readings = self._read(HourlyKwh, filters=filters)
        return meter_readings

    def insert_into_power_meter_table(self, data):
        self._insert(PowerMeter, data)

    def get_last_processed_meter_reading(self, box_id, device_id, table_type):
        processed_table_filter = Expression(ProcessedReadings.processed_table, "=", table_type)
        box_id_filter = Expression(ProcessedReadings.box_id, "=", box_id)
        device_id_filter = Expression(ProcessedReadings.device_id, "=", device_id)

        filters = [processed_table_filter, box_id_filter, device_id_filter]
        read_iter = self._read(ProcessedReadings, filters=filters)

        if isinstance(read_iter, list):
            return read_iter[0] if read_iter else None
        elif hasattr(read_iter, '__iter__'):
            return next(iter(read_iter), None)
        else:
            return None

    def get_all_meter_devices(self):
        power_meter_devices = self._read(PowerMeterDevices)
        return power_meter_devices

    @staticmethod
    def insert_processed_reading(data):
        record, created = ProcessedReadings.get_or_create(
            device_id=data["device_id"],
            box_id=data["box_id"],
            processed_table=data["processed_table"],
            defaults=data,
        )
        if not created:
            record.timestamp = data["timestamp"]
            record.last_processed_reading = data["last_processed_reading"]
            record.save()
