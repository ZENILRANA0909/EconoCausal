import random
from typing import List, Dict

SIMULATED_EVENT_TEMPLATES = [
    {
        "source_ip": "192.168.1.50",
        "destination_ip": "203.0.113.55",
        "source_port": 51823,
        "destination_port": 4444,
        "protocol": "TCP",
        "is_dns": False,
        "dns_query": "",
        "http_destination": "",
    },
    {
        "source_ip": "192.168.1.50",
        "destination_ip": "8.8.8.8",
        "source_port": 51900,
        "destination_port": 53,
        "protocol": "UDP",
        "is_dns": True,
        "dns_query": "update.firmware-vendor-demo.net",
        "http_destination": "",
    },
    {
        "source_ip": "192.168.1.50",
        "destination_ip": "198.51.100.20",
        "source_port": 51930,
        "destination_port": 80,
        "protocol": "TCP",
        "is_dns": False,
        "dns_query": "",
        "http_destination": "http://telemetry.demo-iot-vendor.net/report",
    },
    {
        "source_ip": "192.168.1.50",
        "destination_ip": "192.168.1.1",
        "source_port": 23,
        "destination_port": 23,
        "protocol": "TCP",
        "is_dns": False,
        "dns_query": "",
        "http_destination": "",
    },
    {
        "source_ip": "192.168.1.50",
        "destination_ip": "192.168.1.1",
        "source_port": 51999,
        "destination_port": 21,
        "protocol": "TCP",
        "is_dns": False,
        "dns_query": "",
        "http_destination": "",
    },
]


def generate_demo_network_events() -> List[Dict]:
    events = [dict(item) for item in SIMULATED_EVENT_TEMPLATES]
    random.shuffle(events)
    return events
