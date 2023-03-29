from .contracts.power_meter_contract import PowerMeterContract
from .implementations.wirenboard_map12h.wirenboard_map12h import WBMap12H
# from .implementations.wl4110.wl4110_meter import Wl4110Meter
import os
import configparser


METERS = [
    WBMap12H
]


class MetersLoader:
    def __init__(self):
        self.meter_instances_container = []
        self.config = configparser.ConfigParser()
        self.config_file = 'meters_config.ini'
        self.load_meters()

    def load_meters(self):
        for instance in METERS:
            if issubclass(instance, PowerMeterContract):
                # Check if config file exists
                if os.path.exists(self.config_file):
                    self.config.read(self.config_file)
                else:
                    # Create config file if it does not exist
                    self.config.read_dict({})

                # Check if section for instance exists
                instance_name = instance.__name__
                if instance_name not in self.config:
                    # Create section for instance if it does not exist
                    self.config[instance_name] = {
                        'port': instance.default_port(),
                        'device_id': instance.default_device_id(),
                        'stop_bits': instance.default_stop_bits(),
                        'byte_size': instance.default_byte_size(),
                        'baud_rate': instance.default_baud_rate(),
                        'time_out': instance.default_timeout(),
                        'parity': instance.default_parity(),
                        'reading_frequency': instance.default_reading_frequency(),
                    }
                    with open(self.config_file, 'w') as f:
                        self.config.write(f)

                # Load parameters from config file
                params = {k: v for k, v in self.config[instance_name].items()}
                port = params['port']
                device_id = int(params['device_id'])
                stop_bits = int(params['stop_bits'])
                byte_size = int(params['byte_size'])
                baud_rate = int(params['baud_rate'])
                frequency = int(params['reading_frequency'])
                time_out = float(params['time_out'])
                parity = params['parity']

                # Create instance with parameters
                meter_instance = instance(port=port, device_id=device_id, stop_bits=stop_bits, byte_size=byte_size,
                                          baud_rate=baud_rate, time_out=time_out, parity=parity, frequency=frequency)

                self.meter_instances_container.append(meter_instance)

            else:
                raise TypeError('Meter instance does not implement the MeterInterface')
        return self.meter_instances_container
