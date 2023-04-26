from datetime import datetime
from peewee import Model, IntegerField, FloatField, CharField, AutoField, DateTimeField, PostgresqlDatabase, \
    ForeignKeyField


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


class PowerMeterLoads(BaseModel):
    id = AutoField(primary_key=True)
    created_on = DateTimeField(default=datetime.now)
    description = CharField(max_length=50)
    box_id = CharField(max_length=20)
    measurements_table = CharField(max_length=20)

    class Meta:
        table_name = 'power_meter_loads'
        schema = 'control'


class HourlyKwh(PowerMeterBase):
    load_id = ForeignKeyField(PowerMeterLoads, field='id', backref='hourly_kwh')

    class Meta:
        table_name = 'hourly_kwh'
        schema = 'measurements'
        indexes = (
            (('timestamp', 'device_id', 'box_id'), True),
        )


class DailyKwh(PowerMeterBase):
    load_id = ForeignKeyField(PowerMeterLoads, field='id', backref='daily_kwh')

    class Meta:
        table_name = 'daily_kwh'
        schema = 'measurements'
        indexes = (
            (('timestamp', 'device_id', 'box_id'), True),
        )


class MeterFullRegisters(BaseModel):
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
        table_name = 'meter_full_registers'
        schema = 'measurements'
        indexes = (
            (('timestamp', 'device_id', 'box_id'), True),
        )
