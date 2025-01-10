import math

from prometheus_client import start_http_server, Histogram

latency = Histogram(
    "model_latency",
    "Model latency",
    buckets=[10, 20, 30, 40, 50, 60, 90, 120, 180, math.inf],
)

def serve(host, port):
    start_http_server(addr=host, port=port)