class PowerMeterBase:
    def __init__(self, db_service, publish_service, device_id):
        self.__store_service = db_service
        self.__publish_service = publish_service
        self._device_id = device_id
        self.MODBUS_EXCEPTION_CODES = {
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

    def save_values(self, values):
        self.__store_service.save(values, device_id=self._device_id)

    def read_saved_values(self, ):
        return self.__store_service.read_all_values(device_id=self._device_id)

    def publish_values(self, values):
        self.__publish_service.save(values)
