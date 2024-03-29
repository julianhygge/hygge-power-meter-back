from peewee import Expression, fn
from hyggepowermeter.data.energy_system_schemas import db, MainRegisters, HourlyKwh, DailyKwh, ProcessedReadings, \
    MeterLoads, BaseModel, MeterDevices, FullRegisters, School, Lab, Inverter, \
    BSP, VarioTrack, DailyProductionKwh, User, AuthAttempts
from hyggepowermeter.data.repository_base import RepositoryBase
from hyggepowermeter.utils.logger import logger


class EnergySystemRepository(RepositoryBase):
    def __init__(self, db_config):
        super().__init__(db_config)
        db.init(database=db_config.database,
                host=db_config.host,
                port=db_config.port,
                user=db_config.user,
                password=db_config.password)
        self._create_schema_if_not_exists('measurements')
        self._create_schema_if_not_exists('control')
        self._create_schema_if_not_exists('studer')
        self._create_schema_if_not_exists('power_meter')
        self._create_schema_if_not_exists('auth')
        self._create_table_if_not_exists(User)
        self._create_table_if_not_exists(AuthAttempts)
        self._create_table_if_not_exists(MainRegisters)
        self._create_table_if_not_exists(MeterLoads)
        self._create_table_if_not_exists(DailyKwh)
        self._create_table_if_not_exists(HourlyKwh)
        self._create_table_if_not_exists(ProcessedReadings)
        self._create_table_if_not_exists(ProcessedReadings)
        self._create_table_if_not_exists(MeterDevices)
        self._create_table_if_not_exists(FullRegisters)
        self._create_table_if_not_exists(School)
        self._create_table_if_not_exists(Lab)
        self._create_table_if_not_exists(Inverter)
        self._create_table_if_not_exists(BSP)
        self._create_table_if_not_exists(VarioTrack)
        self._create_table_if_not_exists(DailyProductionKwh)

    def insert_power_meter_reading(self, data):
        self._insert(MainRegisters, data)

    def insert_inverter_reading(self, data):
        self._insert(Inverter, data)

    def insert_bsp_reading(self, data):
        self._insert(BSP, data)

    def insert_vario_track_reading(self, data):
        self._insert(VarioTrack, data)

    def insert_school_meter_reading(self, data):
        self._insert(School, data)

    def insert_lab_meter_reading(self, data):
        self._insert(Lab, data)

    def upsert_hourly_kwh(self, data):
        self._upsert(HourlyKwh, data)

    def upsert_daily_kwh(self, data):
        self._upsert(DailyKwh, data)

    @staticmethod
    def _upsert(model_class, data):
        exists_query = (model_class
                        .select()
                        .where((model_class.timestamp == data['timestamp']) &
                               (model_class.device_id == data['device_id']) &
                               (model_class.box_id == data['box_id']) &
                               (model_class.load_id == data['load_id'])
                               )

                        .exists())

        if exists_query:
            update_query = (model_class.update({model_class.power: data['power']})
                            .where((model_class.timestamp == data['timestamp']) &
                                   (model_class.device_id == data['device_id']) &
                                   (model_class.box_id == data['box_id']) &
                                   (model_class.load_id == data['load_id'])
                                   ))

            update_query.execute()
        else:
            insert_query = model_class.insert(data)
            insert_query.execute()

    def insert_hourly_kwh(self, data):
        self._insert(HourlyKwh, data)

    def insert_daily_kwh(self, data):
        self._insert(DailyKwh, data)

    def insert_full_registers(self, data):
        self._insert(FullRegisters, data)

    def read_power_meter_readings(self, filters=None, order_by=None, limit=None, between=None):
        self._read(MainRegisters, filters, order_by, limit, between)

    def find_table_class(self, cls, table_name):
        for subclass in cls.__subclasses__():
            if subclass.get_table_name() == table_name:
                return subclass
            found = self.find_table_class(subclass, table_name)
            if found is not None:
                return found
        return None

    def read_last_power_meter_readings(self, table_name, after_id, box_id, device_id):
        table_class = self.find_table_class(BaseModel, table_name)

        if table_class is None:
            logger.error(f"Table name not found: {table_name}")
            return []

        meter_reading_filter = Expression(table_class.id, ">", after_id)
        box_filter = Expression(table_class.box_id, "=", box_id)
        device_filter = Expression(table_class.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter]
        meter_readings = self._read(table_class, filters=filters)
        return meter_readings

    def read_last_kwh_readings(self, load_id, after_id, box_id, device_id):
        load_filter = Expression(HourlyKwh.load_id, "=", load_id)
        meter_reading_filter = Expression(HourlyKwh.id, ">", after_id)
        box_filter = Expression(HourlyKwh.box_id, "=", box_id)
        device_filter = Expression(HourlyKwh.device_id, "=", device_id)
        filters = [meter_reading_filter, box_filter, device_filter, load_filter]
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
        self._insert(MainRegisters, data)

    def get_last_processed_meter_reading(self, box_id, device_id, table_type, load_id=None):
        processed_table_filter = Expression(ProcessedReadings.processed_table, "=", table_type)
        box_id_filter = Expression(ProcessedReadings.box_id, "=", box_id)
        device_id_filter = Expression(ProcessedReadings.device_id, "=", device_id)
        filters = [processed_table_filter, box_id_filter, device_id_filter]

        if load_id is not None:
            load_filter = Expression(ProcessedReadings.load_id, "=", load_id)
            filters.append(load_filter)

        read_iter = self._read(ProcessedReadings, filters=filters)

        if isinstance(read_iter, list):
            return read_iter[0] if read_iter else None
        elif hasattr(read_iter, '__iter__'):
            return next(iter(read_iter), None)
        else:
            return None

    def get_all_meter_devices(self):
        power_meter_devices = self._read(MeterDevices)
        return power_meter_devices

    def get_all_loads_by_box_id(self, box_id):
        box_id_filter = Expression(MeterLoads.box_id, "=", box_id)
        filters = [box_id_filter]
        loads = self._read(MeterLoads, filters=filters)
        return loads

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

    @staticmethod
    def select_pv_generations_by_day_after_date(last_date, device_id):
        start_hour = 1
        end_hour = 23
        query = (VarioTrack
                 .select(VarioTrack.id, VarioTrack.timestamp, VarioTrack.vt_prod_pre_day_kwh, VarioTrack.device_id)
                 .where((fn.date_part('hour', VarioTrack.timestamp) >= start_hour) &
                        (fn.date_part('hour', VarioTrack.timestamp) <= end_hour) &
                        (VarioTrack.timestamp >= last_date) &
                        (VarioTrack.device_id == device_id) &
                        (~VarioTrack.vt_prod_pre_day_kwh.is_null())))
        return query

    def select_last_daily_generation(self, box_id, device_id):
        device_id_filter = Expression(DailyProductionKwh.device_id, "=", device_id)
        box_id_filter = Expression(DailyProductionKwh.box_id, "=", box_id)
        filters = [device_id_filter, box_id_filter]
        records = self._read(DailyProductionKwh, order_by=[DailyProductionKwh.id.desc()], filters=filters, limit=1)
        return records
