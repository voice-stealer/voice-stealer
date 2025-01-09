import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt


class DatabaseManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def connect(self):
        try:
            self.connection = psycopg2.connect(self.db_config)
            print("Database connection successful.")
        except Exception as error:
            print(f"Error connecting to database: {error}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def create_user_account(self, name, password):
        self.connect()
        """Create a user account in the database."""
        try:
            hashed_password = self.hash_password(password)
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (name, password)
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (name, hashed_password)
                )
                user_id = cursor.fetchone()[0]
                self.connection.commit()
            self.disconnect()
            return user_id
        except Exception as error:
            print(f"Error creating user account: {error}")
            self.disconnect()
            return None

    def authenticate_user(self, name, password):
       self.connect()
       """Authenticate a user based on name and password."""
       try:
           with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
               cursor.execute(
                   "SELECT password FROM users WHERE name = %s;",
                   (name,)
               )
               user_record = cursor.fetchone()
               if user_record and bcrypt.checkpw(password.encode('utf-8'), user_record['password'].encode('utf-8')):
                   return True
               else:
                   return False
       except Exception as error:
           print(f"Error during user authentication: {error}")
           return False
       finally:
           self.disconnect()

    def create_request(self, request_id, username, speaker_name):
        self.connect()
        """
        Create new request
        """
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """INSERT INTO requests (id, user_id, speaker_id, status) VALUES
                    (%s,
                        (SELECT u.id FROM users AS u WHERE u.name = %s LIMIT 1),
                        (SELECT s.id FROM speakers AS s WHERE s.name = %s LIMIT 1),
                    'pending')""",
                    (request_id, username, speaker_name),
                )
                self.connection.commit()
        except Exception as error:
            print(f"Error creating request: {error}")
        self.disconnect()


    def fetch_status(self, request_id):
        self.connect()
        """Fetch the status of a given task"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT status FROM requests WHERE id = %s", (request_id,)
                )
                status = cursor.fetchone()
            self.disconnect()
            return status['status']
        except Exception as error:
            print(f"Error fetching status: {error}")
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
            print(f"Error fetching tasks: {error}")
            self.disconnect()
            return []

    def fetch_speakers_for_user_by_name(self, username):
        self.connect()
        """Fetch all speaker names for a given user name"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT s.name FROM speakers s
                    JOIN users u ON s.user_id = u.id
                    WHERE u.name = %s
                    """,
                    (username,)
                )
                speakers = cursor.fetchall()
            self.disconnect()
            return [speaker['name'] for speaker in speakers]
        except Exception as error:
            print(f"Error fetching speakers: {error}")
            self.disconnect()
            return []

    def save_speaker_for_user(self, username, speaker_name):
       self.connect()
       """Save a speaker name for a given user name"""
       try:
           with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
               cursor.execute("SELECT id FROM users WHERE name = %s", (username,))
               user_record = cursor.fetchone()

               if not user_record:
                   print("User not found.")
                   return False

               user_id = user_record['id']

               cursor.execute(
                   """
                   INSERT INTO speakers (name, user_id)
                   VALUES (%s, %s)
                   ON CONFLICT (name, user_id) DO UPDATE SET name = EXCLUDED.name
                   """,
                   (speaker_name, user_id)
               )
               self.connection.commit()
           self.disconnect()
           return True
       except Exception as error:
           print(f"Error saving speaker: {error}")
           self.disconnect()
           return False

