import boto3
import os

class FileManager:
    def __init__(self, config):
        self.boto_session = boto3.session.Session(
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key'],
        )
        self.s3_client = self.boto_session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            region_name='ru-central1'
        )
        self.bucket_name = 'speakers'


    def save_file(self, file_path):
        if file_path.endswith('.wav'):
            try:
                with open(file_path, 'rb') as file_data:
                    self.s3_client.upload_fileobj(
                        file_data,
                        self.bucket_name,
                        os.path.basename(file_path),
                        ExtraArgs={'ContentType': 'audio/wav'}
                    )
                return True
            except Exception as e:
                print(f"Ошибка при загрузке файла: {e}")
                return False
        return False

    def get_file(self, filename):
        """Извлечь аудиофайл из бакета и отправить его пользователю"""
        try:
            s3_object = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
            return s3_object['Body'].read()
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            print(f"Ошибка при получении файла: {e}")
            return None