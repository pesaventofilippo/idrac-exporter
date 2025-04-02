import os
import json


class EnvironmentConfig:
    def __init__(self):
        self.PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8000"))
        self.PROMETHEUS_PREFIX = os.getenv("PROMETHEUS_PREFIX", "idrac")

        hosts_json = os.getenv("IDRAC_HOSTS", "[]")
        try:
            self.IDRAC_HOSTS = json.loads(hosts_json)
        except json.JSONDecodeError:
            self.IDRAC_HOSTS = []


env = EnvironmentConfig()
