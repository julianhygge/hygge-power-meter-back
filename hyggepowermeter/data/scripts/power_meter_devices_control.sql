CREATE OR REPLACE FUNCTION control.check_and_insert_powermeter_device()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the combination of device_id and box_id exists in PowerMeterDevices
    IF NOT EXISTS (
        SELECT 1 FROM control.powermeter_devices
        WHERE device_id = NEW.device_id AND box_id = NEW.box_id
    ) THEN
        -- If not, insert a new record into PowerMeterDevices
        INSERT INTO control.powermeter_devices (device_id, box_id, description)
        VALUES (NEW.device_id, NEW.box_id, 'Automatically added by trigger');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER control.powermeter_insert_trigger
AFTER INSERT ON measurements.power_meter
FOR EACH ROW
EXECUTE FUNCTION check_and_insert_powermeter_device();
