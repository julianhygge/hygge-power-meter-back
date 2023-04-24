from hyggepowermeter.services.mqtt.topics.topics.full_registers import FullRegisters
from hyggepowermeter.services.mqtt.topics.topics.main_register import MainRegisters


class TopicFactory:
    @staticmethod
    def get_topic_subscriber(topic):
        if "main" in topic:
            t = MainRegisters()
            return t

        elif "full" in topic:
            t = FullRegisters()
            return t
