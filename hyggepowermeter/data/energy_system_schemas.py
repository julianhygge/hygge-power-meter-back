from datetime import datetime
from peewee import Model, IntegerField, FloatField, CharField, AutoField, DateTimeField, PostgresqlDatabase, \
    ForeignKeyField, DateField
from datetime import date
from playhouse.pool import PooledPostgresqlDatabase


class PooledPostgresqlUTCDatabase(PooledPostgresqlDatabase):
    def _connect(self, *args, **kwargs):
        conn = super()._connect(*args, **kwargs)
        cursor = conn.cursor()
        cursor.execute("SET TIME ZONE 'UTC';")
        cursor.close()
        return conn


db = PooledPostgresqlUTCDatabase(
    "power-meter",
    max_connections=10,
    stale_timeout=300,
)


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


class Inverter(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    device_id = IntegerField()
    xt_bat_charge_a = FloatField(null=True)
    xt_phase = IntegerField(null=True)
    xt_transfert = IntegerField(null=True)
    xt_mode = IntegerField(null=True)
    xt_aux1 = IntegerField(null=True)
    xt_aux2 = IntegerField(null=True)
    xt_bat_dis_pre_day_kwh = FloatField(null=True)
    xt_from_grid_pre_day_kwh = FloatField(null=True)
    xt_from_grid_kwh = FloatField(null=True)
    xt_energy_day_kwh = FloatField(null=True)
    xt_rme = FloatField(null=True)
    xt_ubat_min_vdc = FloatField(null=True)
    xt_ubat_avg_vdc = FloatField(null=True)
    xt_ibat_avg_adc = FloatField(null=True)
    xt_pout_max_kva = FloatField(null=True)
    xt_pout_avg_kva = FloatField(null=True)
    xt_pout_a_avg_kw = FloatField(null=True)
    xt_dev1_temp_max = FloatField(null=True)
    xt_fout_hz = FloatField(null=True)
    xt_uin_vac = FloatField(null=True)
    xt_iin_aac = FloatField(null=True)
    xt_pin_a_avg_kw = FloatField(null=True)
    xt_fin_hz = FloatField(null=True)
    xt_dev_dbg1 = FloatField(null=True)

    class Meta:
        table_name = 'inverter'
        schema = 'studer'


class BSP(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    device_id = IntegerField()
    bsp_charged_day_ah = FloatField(null=True)
    bsp_discharged_day_ah = FloatField(null=True)
    bsp_ubat_avg_vdc = FloatField(null=True)
    bsp_ibat_avg_adc = FloatField(null=True)
    bsp_soc = FloatField(null=True)
    bsp_tbat = FloatField(null=True)

    class Meta:
        table_name = 'bsp'
        schema = 'studer'


class VarioTrack(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    device_id = IntegerField()
    vt_battery_a = FloatField(null=True)
    vt_prod_day_ah = FloatField(null=True)
    vt_prod_day_kwh = FloatField(null=True)
    vt_prod_pre_day_kwh = FloatField(null=True)
    vt_mode = IntegerField(null=True)
    vt_phas = IntegerField(null=True)
    vt_ubam_avg_vdc = FloatField(null=True)
    vt_ibam_avg_adc = FloatField(null=True)
    vt_upvm_avg_vdc = FloatField(null=True)
    vt_psom_avg_kw = FloatField(null=True)
    vt_dev_temp_avg = FloatField(null=True)
    vt_aux = IntegerField(null=True)
    vt_aux2 = IntegerField(null=True)
    vt_dev_locer = FloatField(null=True)
    vt_rme = IntegerField(null=True)

    class Meta:
        table_name = 'vario_track'
        schema = 'studer'


class MainRegisters(PowerMeterBase):
    current = FloatField()
    voltage = FloatField()

    class Meta:
        table_name = 'main_registers'
        schema = 'power_meter'


class School(PowerMeterBase):
    current = FloatField()
    voltage = FloatField()

    class Meta:
        table_name = 'school'
        schema = 'power_meter'


class Lab(PowerMeterBase):
    current = FloatField()
    voltage = FloatField()

    class Meta:
        table_name = 'lab'
        schema = 'power_meter'


class ProcessedReadings(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    last_processed_reading = IntegerField()
    processed_table = CharField(max_length=20)
    box_id = CharField(max_length=20)
    device_id = IntegerField()
    load_id = IntegerField(null=True)

    class Meta:
        table_name = 'processed_readings'
        schema = 'control'


class MeterDevices(BaseModel):
    id = AutoField(primary_key=True)
    timestamp = DateTimeField(default=datetime.now)
    box_id = CharField(max_length=20)
    device_id = IntegerField()
    description = CharField(max_length=50)
    timezone = CharField(max_length=65, default='Asia/Kolkata')

    class Meta:
        table_name = 'meter_devices'
        schema = 'control'


class MeterLoads(BaseModel):
    id = AutoField(primary_key=True)
    created_on = DateTimeField(default=datetime.now)
    description = CharField(max_length=50)
    box_id = CharField(max_length=20)
    measurements_table = CharField(max_length=20)

    class Meta:
        table_name = 'meter_loads'
        schema = 'control'


class HourlyKwh(PowerMeterBase):
    load_id = ForeignKeyField(MeterLoads, field='id', backref='hourly_kwh')

    class Meta:
        table_name = 'hourly_kwh'
        schema = 'power_meter'
        indexes = (
            (('timestamp', 'device_id', 'box_id', "load_id"), True),
        )


class DailyKwh(PowerMeterBase):
    load_id = ForeignKeyField(MeterLoads, field='id', backref='daily_kwh')

    class Meta:
        table_name = 'daily_kwh'
        schema = 'power_meter'
        indexes = (
            (('timestamp', 'device_id', 'box_id', "load_id"), True),
        )


class DailyProductionKwh(BaseModel):
    id = AutoField(primary_key=True)
    measurement_date = DateField(default=date.today)
    device_id = IntegerField()
    box_id = CharField(max_length=50)
    kwh = FloatField()

    class Meta:
        table_name = 'daily_production_kwh'
        schema = 'studer'


class FullRegisters(BaseModel):
    id = AutoField(primary_key=True)
    box_id = CharField()
    device_id = IntegerField()
    timestamp = DateTimeField()

    consumption_active_ch1 = FloatField(null=True)
    consumption_active_ch2 = FloatField(null=True)
    consumption_active_ch3 = FloatField(null=True)
    consumption_active_ch4 = FloatField(null=True)

    consumption_apparent_ch1 = FloatField(null=True)
    consumption_apparent_ch2 = FloatField(null=True)
    consumption_apparent_ch3 = FloatField(null=True)
    consumption_apparent_ch4 = FloatField(null=True)

    consumption_reactive_ch1 = FloatField(null=True)
    consumption_reactive_ch2 = FloatField(null=True)
    consumption_reactive_ch3 = FloatField(null=True)
    consumption_reactive_ch4 = FloatField(null=True)

    frequency = FloatField(null=True)

    phase_angle_l1_ch1 = FloatField(null=True)
    phase_angle_l1_ch2 = FloatField(null=True)
    phase_angle_l1_ch3 = FloatField(null=True)
    phase_angle_l1_ch4 = FloatField(null=True)

    phase_angle_l2_ch1 = FloatField(null=True)
    phase_angle_l2_ch2 = FloatField(null=True)
    phase_angle_l2_ch3 = FloatField(null=True)
    phase_angle_l2_ch4 = FloatField(null=True)

    phase_angle_l3_ch1 = FloatField(null=True)
    phase_angle_l3_ch2 = FloatField(null=True)
    phase_angle_l3_ch3 = FloatField(null=True)
    phase_angle_l3_ch4 = FloatField(null=True)

    rms_l1_current_ch1 = FloatField(null=True)
    rms_l1_current_ch2 = FloatField(null=True)
    rms_l1_current_ch3 = FloatField(null=True)
    rms_l1_current_ch4 = FloatField(null=True)

    rms_l1_voltage = FloatField(null=True)

    rms_l2_current_ch1 = FloatField(null=True)
    rms_l2_current_ch2 = FloatField(null=True)
    rms_l2_current_ch3 = FloatField(null=True)
    rms_l2_current_ch4 = FloatField(null=True)

    rms_l2_voltage = FloatField(null=True)

    rms_l3_current_ch1 = FloatField(null=True)
    rms_l3_current_ch2 = FloatField(null=True)
    rms_l3_current_ch3 = FloatField(null=True)
    rms_l3_current_ch4 = FloatField(null=True)

    rms_l3_voltage = FloatField(null=True)

    total_active_power_ch1 = FloatField(null=True)
    total_active_power_ch2 = FloatField(null=True)
    total_active_power_ch3 = FloatField(null=True)
    total_active_power_ch4 = FloatField(null=True)

    total_apparent_power_ch1 = FloatField(null=True)
    total_apparent_power_ch2 = FloatField(null=True)
    total_apparent_power_ch3 = FloatField(null=True)
    total_apparent_power_ch4 = FloatField(null=True)

    total_reactive_power_ch1 = FloatField(null=True)
    total_reactive_power_ch2 = FloatField(null=True)
    total_reactive_power_ch3 = FloatField(null=True)
    total_reactive_power_ch4 = FloatField(null=True)

    class Meta:
        table_name = 'full_registers'
        schema = 'power_meter'
        indexes = (
            (('timestamp', 'device_id', 'box_id'), True),
        )
