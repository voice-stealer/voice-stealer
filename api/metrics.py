from prometheus_client import start_http_server, Counter

requests = Counter(
    "api_requests",
    "API requests",
    ["handler"]
)

def serve(host, port):
    start_http_server(addr=host, port=port)