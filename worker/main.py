import json
import os.path
import time

from db import DatabaseManager
from kafka import Kafka
from s3 import FileManager
from tts import VoiceStealer
from logger import Logger
import os

audio_prefix = "audio"

logger = None

db_password = os.environ["DB_PASSWORD"].strip()
aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"].strip()
hostname = os.getenv("HOSTNAME")
kafka_ip = os.environ["KAFKA_IP"].strip()

db_config = f"""
    host=rc1a-2qr3lpuy4yr5p1cc.mdb.yandexcloud.net
    port=6432
    sslmode=verify-full
    dbname=preprod
    user=voice-stealer-preprod
    password={db_password}
    target_session_attrs=read-write
"""

db = None
s3 = FileManager({'aws_access_key_id': 'YCAJEFDI3ulOo8HCiAi2wPZSK', 'aws_secret_access_key': aws_secret_access_key})
vc = VoiceStealer()

def clear_old_speaker_files():
    global audio_prefix
    global logger

    current_time = time.time()
    age_threshold_in_seconds = 3600 # 1 hour
    directory = os.getcwd()

    for filename in os.listdir(directory):
        if filename.startswith(audio_prefix):
            file_path = os.path.join(directory, filename)
            file_mod_time = os.path.getmtime(file_path)
            if current_time - file_mod_time > age_threshold_in_seconds:
                os.remove(file_path)
                logger.info(f"Deleted old speaker file: {file_path}")


def on_message_callback(msg):
    global logger

    try:
        js = json.loads(msg.value().decode('utf8').replace("'", '"'))
        request_id = js["reqid"]
        text = js["text"]
        audio_path = js["audio"]
    except json.decoder.JSONDecodeError as e:
        logger.error(f"failed to loads json: {e}")
        return

    request_logger = logger.with_field("request_id", request_id)

    try:
        local_audio_path = audio_prefix + audio_path.replace('/', '_')
        if db.fetch_status(request_id) == "pending":
            db.set_status(request_id, "in_progress")
            if not os.path.exists(local_audio_path):
                request_logger.info("starting audio downloading")
                audio = s3.get_file(audio_path)
                with open(local_audio_path, 'wb') as file:
                    file.write(audio)
                request_logger.info("audio downloaded")
            request_logger.info("starting generating")
            result_filepath = vc.generate(request_id, text, local_audio_path)
            request_logger.info("generated")
            s3.save_file(result_filepath)
            os.remove(result_filepath)
            request_logger.info('generated audio saved')
            db.set_status(request_id, "done")
            request_logger.info('request done')
            clear_old_speaker_files()
            return
    except Exception as e:
        request_logger.error(e)
    db.set_status(request_id, "failed")


if __name__ == "__main__":
    kafka = Kafka(f"{kafka_ip}:9092", "default", "earliest", on_message_callback=on_message_callback)
    logger = Logger(kafka).with_field("hostname", hostname)
    db = DatabaseManager(db_config, logger)
    logger.info("started")
    kafka.consume("requests")
