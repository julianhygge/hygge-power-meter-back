from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from hyggepowermeter.implementations.wirenboard_map12h.data.power_meter_repository import Map12Repository
from hyggepowermeter.implementations.power_meter_base import PowerMeterBase
from hyggepowermeter.contracts.power_meter_contract import PowerMeterContract
from hyggepowermeter.hygge_logging.hygge_logging import logger
import struct
import json
import paho.mqtt.publish as publish
import time
from contextlib import contextmanager

from hyggepowermeter.implementations.wirenboard_map12h.registers import REGISTER_CONFIGS


@contextmanager
def modbus_client_context(client):
    try:
        if not client.connect():
            logger.error("Failed to connect to the Modbus client")
            yield None
        else:
            yield client
    finally:
        client.close()


class WBMap12H(PowerMeterContract, PowerMeterBase):
    """Implementation of Wirenboard Power Meter WB-MAP12H """

    def __init__(self, port,
                 device_id,
                 stop_bits,
                 byte_size,
                 baud_rate,
                 time_out,
                 parity,
                 frequency):
        PowerMeterBase.__init__(self, Map12Repository(self.__class__.__name__), None, device_id)
        # db_service, publish_service, when completed should inject the services.
        self._port = port
        self._stop_bits = int(stop_bits)
        self._baud_rate = int(baud_rate)
        self._byte_size = int(byte_size)
        self._device_id = int(device_id)
        self._frequency_inst_sec = int(frequency)

        self._client = ModbusSerialClient(
            method=self.method,
            port=self._port,
            parity=parity,
            timeout=time_out,
            baudrate=self._baud_rate,
            stopbits=stop_bits,
            bytesize=self._byte_size)

        self.register_configs = REGISTER_CONFIGS

        logger.info("Power meter configuration parameters:")
        logger.info(f"port: {port}")
        logger.info(f"stop_bits: {self._stop_bits}")
        logger.info(f"byte_size: {self._byte_size}")
        logger.info(f"baud_rate: {self._baud_rate}")
        logger.info(f"device_address: {self._device_id}")
        logger.info(f"parity: {parity}")

    # metadata
    meter_name = "Wirenboard"
    meter_model = 'WB-MAP12H'
    meter_version = "1.0-1"
    method = "Rtu"
    retry_to_read_register = 3

    # default configuration
    _default_stop_bits = 1
    _default_device_id = 111
    _default_byte_size = 8
    _default_port = "/dev/ttyMAX0"
    _default_baud_rate = 115200
    _default_timeout = 1
    _default_parity = 'N'
    _default_reading_frequency = 60

    @classmethod
    def default_reading_frequency(cls) -> int:
        return cls._default_reading_frequency

    @classmethod
    def default_stop_bits(cls) -> int:
        return cls._default_stop_bits

    @classmethod
    def default_device_id(cls) -> int:
        return cls._default_device_id

    @classmethod
    def default_byte_size(cls) -> int:
        return cls._default_byte_size

    @classmethod
    def default_port(cls) -> str:
        return cls._default_port

    @classmethod
    def default_baud_rate(cls) -> int:
        return cls._default_baud_rate

    @classmethod
    def default_timeout(cls) -> int:
        return cls._default_timeout

    @classmethod
    def default_parity(cls) -> str:
        return cls._default_parity

    @property
    def current_in_ma(self) -> float:
        return 0

    @property
    def frequency_inst_sec(self) -> float:
        return self._frequency_inst_sec

    @property
    def power_in_kw(self) -> float:
        return 0

    def read_register_address(self, register_address: int) -> float:
        return 0

    @property
    def baud_rate(self) -> int:
        return self._baud_rate

    @property
    def byte_size(self) -> int:
        return self._byte_size

    @property
    def stop_bits(self) -> int:
        return self._stop_bits

    @property
    def communication_port(self) -> str:
        return self._port

    def start_meter(self):
        pass

    def read_registers(self) -> dict:
        register_values = {}

        with modbus_client_context(self._client) as client:
            if client is None:
                return register_values

            for register in self.register_configs:
                time.sleep(0.5)
                position, address, address_name, factor, signed, num_bytes, big_endian = self.unpack_register(register)

                logger.info(f"Address {position} {hex(address)} {address_name}")
                logger.debug(f"Factor: {factor}")
                logger.debug(f"Signed: {signed}")
                logger.debug(f"Number of bytes: {num_bytes}")
                logger.debug(f"Endian: {big_endian}")

                for _ in range(self.retry_to_read_register):
                    try:
                        result = client.read_holding_registers(address=address, count=num_bytes // 2,
                                                               unit=self._device_id)
                    except ModbusIOException as e:
                        # Handle Modbus communication errors
                        logger.error("Modbus Communication Error: %s", e)
                        continue
                    except Exception as e:
                        # Handle other errors
                        logger.error("Error: %s", e)
                        continue

                    if result.isError():
                        exception_code = getattr(result, 'exception_code', None)
                        if exception_code is not None:
                            exception_name = self.MODBUS_EXCEPTION_CODES.get(exception_code, "Unknown")
                            logger.warning("Modbus Exception - Code: %s, Name: %s", exception_code, exception_name)
                            continue
                        else:
                            logger.warning("Error: 'ModbusIOException' Unknown Modbus error'")
                            continue
                    else:
                        registers = result.registers
                        response_int = self.process_response(registers, signed, num_bytes, big_endian)
                        value = response_int * factor
                        register_values[address_name] = value
                        logger.info(f"{address_name} raw value: {response_int}, value: {value}")
                        break

        self.save_values(register_values)
        # values = self.read_saved_values()

        # self.publish_to_mqtt(values, "")

        # print(str(values))
        return register_values

    @staticmethod
    def publish_to_mqtt(rows, hostname, topic, username=None, password=None):
        auth = None
        if username and password:
            auth = {'username': username, 'password': password}
        for row in rows:
            payload = json.dumps(row)
            publish.single(topic, payload=payload, hostname=hostname, auth=auth)

    @staticmethod
    def process_response(registers, signed, num_bytes, is_big_endian):
        response_bytes = bytearray()

        if num_bytes == 4:
            response_bytes.extend([
                registers[0] >> 8, registers[0] & 0xFF,
                registers[1] >> 8, registers[1] & 0xFF
            ])
        elif num_bytes == 2:
            response_bytes.extend([registers[0] >> 8, registers[0] & 0xFF])
        elif num_bytes == 8:
            response_bytes.extend([
                registers[0] >> 8, registers[0] & 0xFF,
                registers[1] >> 8, registers[1] & 0xFF,
                registers[2] >> 8, registers[2] & 0xFF,
                registers[3] >> 8, registers[3] & 0xFF
            ])
        else:
            raise ValueError("Invalid byte size")

        if is_big_endian == 0:
            fmt = '<'
        else:
            fmt = '>'

        if signed:
            fmt += 'q' if num_bytes == 8 else 'i' if num_bytes == 4 else 'h'
        else:
            fmt += 'Q' if num_bytes == 8 else 'I' if num_bytes == 4 else 'H'
        response_int = struct.unpack(fmt, response_bytes)[0]
        return response_int

    @staticmethod
    def unpack_register(register):
        return register[0], register[1], register[2], register[3], register[4], register[5], register[6]
