import aiohttp
import asyncio
from modules.utils import env
from modules.idrac import IDRAC
import prometheus_client as prom
from http.server import HTTPServer, BaseHTTPRequestHandler

idracs = [
    IDRAC(i["host"], i["user"], i["password"])
    for i in env.IDRAC_HOSTS
]

metrics = {
    "fan_speed": prom.Gauge("fan_speed", "Fan speed in RPM", ["host", "fan"],
                            namespace=env.PROMETHEUS_PREFIX, unit="rpm"),
    "sensor_temperature": prom.Gauge("sensor_temperature", "Temperature in Celsius", ["host", "sensor"],
                                     namespace=env.PROMETHEUS_PREFIX, unit="celsius"),
    "power": prom.Gauge("power", "Power consumption in Watts", ["host", "psu"],
                        namespace=env.PROMETHEUS_PREFIX, unit="watts"),
    "voltage": prom.Gauge("voltage", "Voltage in Volts", ["host", "psu"],
                          namespace=env.PROMETHEUS_PREFIX, unit="volts"),
}


async def fetch_data(idrac: IDRAC, session: aiohttp.ClientSession) -> tuple[str, dict]:
    thermal = await idrac.get_thermal_data(session)
    power = await idrac.get_power_data(session)
    return idrac.host, {
        "thermal": thermal,
        "power": power
    }


async def update_metrics():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(idrac, session) for idrac in idracs]
        results = await asyncio.gather(*tasks)

    for host, data in results:
        if data["thermal"]:
            for fan, speed in data["thermal"]["fans"].items():
                if speed is None:
                    continue
                metrics["fan_speed"].labels(host=host, fan=fan).set(speed)
            for sensor, temperature in data["thermal"]["temperatures"].items():
                if temperature is None:
                    continue
                metrics["sensor_temperature"].labels(host=host, sensor=sensor).set(temperature)

        if data["power"]:
            for i, power in data["power"]["power"].items():
                metrics["power"].labels(host=host, psu=i).set(power)
            for i, voltage in data["power"]["voltage"].items():
                metrics["voltage"].labels(host=host, psu=i).set(voltage)


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            asyncio.run(update_metrics())

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(prom.generate_latest())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    # Disable logging
    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    prom.disable_created_metrics()
    prom.REGISTRY.unregister(prom.PROCESS_COLLECTOR)
    prom.REGISTRY.unregister(prom.PLATFORM_COLLECTOR)
    prom.REGISTRY.unregister(prom.GC_COLLECTOR)

    server = HTTPServer(("0.0.0.0", env.PROMETHEUS_PORT), MetricsHandler)
    server.serve_forever()
