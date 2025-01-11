from prometheus_client import start_http_server, Counter, Gauge

requests = Counter(
    "api_requests",
    "API requests",
    ["handler"]
)

user_feedback = Gauge(
    "user_feedback",
    "User feedback",
    ["verdict"]
)

def serve(host, port):
    start_http_server(addr=host, port=port)