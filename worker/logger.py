class Logger:
    def __init__(self, kafka):
        self.kafka = kafka
        self.fields = {}

    def with_field(self, key, value):
        logger = Logger(self.kafka)
        logger.fields = self.fields.copy()
        logger.fields[key] = value
        return logger

    def info(self, message):
        self.__write(self.__build_message("info", message))

    def error(self, message):
        self.__write(self.__build_message("error", message))

    def __write(self, message):
        print(message)
        self.kafka.produce("logs", message)

    def __build_message(self, level, message):
        fields = self.fields.copy()
        fields["message"] = message
        fields["level"] = level
        return str(fields)
