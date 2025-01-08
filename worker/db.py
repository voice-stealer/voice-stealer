import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self, db_config, logger):
        self.db_config = db_config
        self.connection = None
        self.logger = logger

    def connect(self):
        try:
            self.connection = psycopg2.connect(self.db_config)
            self.logger.info("Database connection successful.")
        except Exception as error:
            self.logger.error(f"Error connecting to database: {error}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed.")

    def create_request(self, request_id, user_name, speaker_name):
        self.connect()
        """
        Create new request
        """
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                """EXEC this sql

                insert into requests (id, user_id, speaker_id, status)
                values ('id',
                (select u.id from users as u where u.name = 'name' limit 1),
                (select s.id from speakers as s where s.name = 'speaker' limit 1),
                'pending');

                """
                cursor.execute(
                    """INSERT INTO requests (id, user_id, speaker_id, status) VALUES
                    (%s,
                        (SELECT u.id FROM users AS u WHERE u.name = %s LIMIT 1),
                        (SELECT s.id FROM speakers AS s WHERE s.name = %s LIMIT 1),
                    'pending')""",
                    (request_id, user_name, speaker_name),
                )
                self.connection.commit()
        except Exception as error:
            self.logger.error(f"Error creating request: {error}")
        self.disconnect()


    def fetch_status(self, request_id):
        self.connect()
        """Fetch the status of a given request"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT status FROM requests WHERE id = %s", (request_id,)
                )
                status = cursor.fetchone()
            self.disconnect()
            return status['status']
        except Exception as error:
            self.logger.error(f"Error fetching status: {error}")
            self.disconnect()
            return None

    def set_status(self, request_id, status):
        self.connect()
        """Set status to request"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "UPDATE requests SET status = %s WHERE id = %s", (status, request_id,)
                )
                self.connection.commit()
            self.disconnect()
        except Exception as error:
            self.logger.error(f"Error fetching status: {error}")
            self.disconnect()
            return None

    def fetch_tasks(self, user_id):
        self.connect()
        """Fetch all tasks and their statuses for a given user"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT task_id, status FROM tasks WHERE user_id = %s", (user_id,)
                )
                tasks = cursor.fetchall()
            self.disconnect()
            return tasks
        except Exception as error:
            self.logger.error(f"Error fetching tasks: {error}")
            self.disconnect()
            return []

    def fetch_user_audios(self, user_id):
        self.connect()
        """Fetch all audio records for a given user"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT audio_id, audio_path FROM audios WHERE user_id = %s", (user_id,)
                )
                audios = cursor.fetchall()
            self.disconnect()
            return audios
        except Exception as error:
            self.logger.error(f"Error fetching audios: {error}")
            self.disconnect()
            return []