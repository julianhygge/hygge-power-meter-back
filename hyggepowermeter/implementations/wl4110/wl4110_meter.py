import time

from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException


from hyggepowermeter.contracts.power_meter_contract import PowerMeterContract
from hyggepowermeter.implementations.power_meter_base import PowerMeterBase
from hyggepowermeter.main import logger

MODBUS_EXCEPTION_CODES = {
    1: "ILLEGAL FUNCTION",
    2: "ILLEGAL DATA ADDRESS",
    3: "ILLEGAL DATA VALUE",
    4: "SLAVE DEVICE FAILURE",
    5: "ACKNOWLEDGE",
    6: "SLAVE DEVICE BUSY",
    7: "NEGATIVE ACKNOWLEDGE",
    8: "MEMORY PARITY ERROR",
    10: "GATEWAY PATH UNAVAILABLE",
    11: "GATEWAY TARGET DEVICE FAILED TO RESPOND"
}


class Wl4110Meter(PowerMeterContract, PowerMeterBase):
    def __init__(self, port, device_address=5, stop_bits=1, byte_size=8, baud_rate=9600):
        super().__init__(None, None)  # db_service, publish_service, when completed should inject the services.
        self._port = port
        self._stop_bits = stop_bits
        self._baud_rate = baud_rate
        self._byte_size = byte_size
        self._device_address = device_address
        parity = "E"

        logger.info("Power meter configuration parameters:")
        logger.info("port:" + str(port))
        logger.info("stop_bits:" + str(self._stop_bits))
        logger.info("byte_size:" + str(self._byte_size))
        logger.info("baud_rate:" + str(self._baud_rate))
        logger.info("device_address:" + str(self._device_address))
        logger.info("parity:" + parity)

        # self.modbus_client.connect()

        self.register_addresses = {
            'pf_avg_address': 40117,
            'pf_r_phase': 40119,
            'vyr_phase': 40135,
            'vbr_phase': 40139,
            'current_total': 4149,
            'current_r_phase': 4151,
            'frequency': 40157,
            'high_current': 40183,
            'rpm': 40215}

    meter_name = "LARSEN & TOUBRO METER"
    meter_model = 'wl4110'
    meter_version = "1.1"
    method = "rtu"
    frequency_inst_sec = 10000

    @property
    def current_in_ma(self) -> float:
        pass

    @property
    def power_in_kw(self) -> float:
        pass

    def read_register_address(self, register_address: int) -> float:
        pass

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

    def read_registers(self) -> list:
        # self.modbus_client.write_register(register_addresses["current_total"], 106, unit=1)  # delete

        register_values = []
        start_address = 40101
        end_address = 40251
        modbus_client = ModbusSerialClient(
            method="rtu",
            port=self._port,
            baudrate=9600,
            parity="E",
            timeout=1,
            bytesize=8,
            stopbits=1,
            unit=1
        )
        # for register in self.register_addresses:
        for register_address in range(start_address, end_address, 2):
            time.sleep(1)
            try:
                # result = self.modbus_client.read_holding_registers(address=self.register_addresses[register],
                #                                                    count=2,
                #                                                    unit=self._device_address)
                #
                # register_address = self.register_addresses[register]
                #

                if not modbus_client.connect():
                    print("Unable to connect to Modbus server")
                    exit(1)
                logger.info("Reading value " + str(register_address))

                register = int(register_address)

                result = modbus_client.write_register(address=register_address, value=5,
                                                              count=1)

                result = modbus_client.read_holding_registers(address=register_address,
                                                              count=1)

                # # Decode the two 16-bit integers into a single 32-bit integer
                # decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
                # value = decoder.decode_32bit_int()
                # print(value)
                result_string = str(result)
                print(result_string)

                register_value = 0
                # Check if the operation was successful
                if result.isError():
                    exception_code = result.exception_code
                    exception_name = MODBUS_EXCEPTION_CODES.get(exception_code, "Unknown")
                    print("Modbus Exception - Code: {}, Name: {}".format(exception_code, exception_name))
                    continue
                else:
                    # Print the register value
                    register_value = result.registers[0]
                    # decoder = BinaryPayloadDecoder.fromRegisters(
                    #     result.registers, byteorder=Endian.Big, wordorder=Endian.Big
                    # )
                    # values = decoder.decode_32bit_float()
                    print("Register value:", result.registers[0])
            except ModbusIOException as e:
                # Handle Modbus communication errors
                print("Modbus Communication Error:", e)
                continue
            except Exception as e:
                # Handle Modbus communication errors
                print("Error:", e)
                continue

            # item_dictionary = {register + '_' + str(self.register_addresses[register]): register_value}
            # logger.info(register + '_' + str(self.register_addresses[register]) + ":" + str(register_value))
            # register_values.append(item_dictionary)
        modbus_client.close()

        return register_values
