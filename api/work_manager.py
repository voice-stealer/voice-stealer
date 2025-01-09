from confluent_kafka import Producer

from db_manager import DatabaseManager

import json


class WorkManager:
    def __init__(self, kafka_conf, db: DatabaseManager):
        self.producer = Producer(**kafka_conf)
        self.db = db

    def create_task(self, request_id, username, message, selected_audio, topic='requests'):
        msg = {
            "reqid": request_id,
            "text": f"{message}",
            "audio": f"{username}/{selected_audio}"
        }
        self.db.create_request(request_id, username, selected_audio)
        self.producer.produce(topic, value=json.dumps(msg, ensure_ascii=False, indent=4).encode('utf-8'))



