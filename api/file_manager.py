import boto3
import io
from flask import send_file

from db_manager import DatabaseManager

class FileManager:
    def __init__(self, s3_config, db: DatabaseManager):
        self.boto_session = boto3.session.Session(
            aws_access_key_id=s3_config['aws_access_key_id'],
            aws_secret_access_key=s3_config['aws_secret_access_key']
        )
        self.s3_client = self.boto_session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            region_name='ru-central1'
        )
        self.bucket_name = 'speakers'
        self.db = db

    def save_file_for_user(self, username, file):
        """Сохранить аудиофайл в бакет"""
        if file and file.filename.endswith('.wav'):
            path = f"{username}/{file.filename}"
            try:
                self.s3_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    path,
                    ExtraArgs={'ContentType': file.content_type}
                )
                if self.db.save_speaker_for_user(username, file.filename):
                    return True
                else:
                    # remove from s3
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=path)
                    return False
            except Exception as e:
                print(f"Ошибка при загрузке файла: {e}")
                return False

    def get_file(self, filename):
        """Извлечь аудиофайл из бакета и отправить его пользователю"""
        try:
            s3_object = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
            return send_file(
                io.BytesIO(s3_object['Body'].read()),
                mimetype=s3_object.get('ContentType', 'application/octet-stream'),
                as_attachment=True,
                download_name=filename
            )
        except self.s3_client.exceptions.NoSuchKey:
            print(f"Ошибка: нет такого файла '{filename}'")
            return None
        except Exception as e:
            print(f"Ошибка при получении файла: {e}")
            return None
