from confluent_kafka import Consumer, Producer, KafkaError

class Kafka:
    def __init__(self, endpoint: str, group_id: str, offset: str, on_message_callback):
        self.endpoint = endpoint
        self.group_id = group_id
        self.offset = offset
        self.consumer = Consumer({
            'bootstrap.servers': endpoint,
            'group.id': group_id,
            'auto.offset.reset': offset,
        })
        self.producer = Producer({
            'bootstrap.servers': endpoint,
        })
        self.on_message = on_message_callback

    def consume(self, topic):
        self.consumer.subscribe([topic])

        try:
            while True:
                msg = self.consumer.poll(1)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print(f"Reached end of partition for {msg.topic()}/{msg.partition()}")
                    else:
                        print(f"Error: {msg.error()}")
                else:
                    print('got message')
                    self.on_message(msg)

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def produce(self, topic, message):
        self.producer.produce(topic, value=message)