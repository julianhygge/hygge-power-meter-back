from abc import ABC, abstractmethod


class PowerMeterContract(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        """This constructor should be implemented by the inheriting classes
        to receive the required parameters specified in the `required_params`
        method.
        """
        pass

    @property
    @abstractmethod
    def current_in_ma(self) -> float:
        """Current intensity in milli-amps.
        """
        pass

    @property
    @abstractmethod
    def power_in_kw(self) -> str:
        """Power in Kw"""
        pass

    @abstractmethod
    def read_register_address(self, register_address: int):
        pass

    @abstractmethod
    def start_meter(self):
        pass

    @property
    @abstractmethod
    def meter_name(self) -> str:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @abstractmethod
    def meter_version(self) -> str:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_reading_frequency(cls) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_stop_bits(cls) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_parity(cls) -> str:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_port(cls) -> str:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_device_id(cls) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_byte_size(cls) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_baud_rate(cls) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @classmethod
    @abstractmethod
    def default_timeout(cls) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @property
    @abstractmethod
    def stop_bits(self) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @property
    @abstractmethod
    def communication_port(self) -> str:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @property
    @abstractmethod
    def frequency_inst_sec(self) -> int:
        """Frequency to read instantaneous values.
        """
        pass

    @property
    @abstractmethod
    def byte_size(self) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @property
    @abstractmethod
    def baud_rate(self) -> int:
        """This property should be supplied by the inheriting classes
        individually.
        """
        pass

    @property
    @abstractmethod
    def method(self) -> str:
        return self.method

    @communication_port.setter
    def communication_port(self, communication_port):
        self.communication_port = communication_port

    @stop_bits.setter
    def stop_bits(self, stop_bits):
        self.stop_bits = stop_bits

    @baud_rate.setter
    def baud_rate(self, baud_rate):
        self.baud_rate = baud_rate

    @byte_size.setter
    def byte_size(self, byte_size):
        self.byte_size = byte_size
