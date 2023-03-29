from hyggepowermeter.topics.topics.main_register import MainRegisters


class TopicFactory:
    @staticmethod
    def get_topic_subscriber(topic):
        if "main_registers" in topic:
            t = MainRegisters()
            return t
