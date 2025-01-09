import uuid
from functools import wraps

class RequestManager:
    def generate_request_id(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            request_id = str(uuid.uuid4())
            return f(request_id, *args, **kwargs)
        return decorated
