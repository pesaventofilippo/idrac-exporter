import aiohttp
import urllib3


class IDRAC:
    def __init__(self, host: str='127.0.0.1', user: str='root', password: str='calvin'):
        self.host = host
        self.auth = aiohttp.BasicAuth(user, password)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    async def _query_redfish(self, session: aiohttp.ClientSession, endpoint: str) -> dict:
        url = f"https://{self.host}/redfish/v1/{endpoint}"
        try:
            async with session.get(url, auth=self.auth, ssl=False, timeout=10) as response:
                return await response.json()
        except Exception:
            return None

    async def get_thermal_data(self, session: aiohttp.ClientSession) -> dict[str, dict[str, int]]:
        data = await self._query_redfish(session, "Chassis/System.Embedded.1/Thermal")
        if data is None:
            return None

        fans = {f["Name"]: f["Reading"] for f in data["Fans"]}
        temperatures = {t["Name"]: t["ReadingCelsius"] for t in data["Temperatures"]}
        temperatures = {k.replace(" Temp", ""): v for k, v in temperatures.items()}

        return {
            "fans": fans,
            "temperatures": temperatures
        }

    async def get_power_data(self, session: aiohttp.ClientSession) -> dict[str, dict[int, int]]:
        data = await self._query_redfish(session, "Chassis/System.Embedded.1/Power")
        if data is None:
            return None

        power = {i: p["PowerConsumedWatts"] for i, p in enumerate(data["PowerControl"])}
        voltage = {i: p["LineInputVoltage"] for i, p in enumerate(data["PowerSupplies"])}
        voltage = {k: v if v is not None else 0 for k, v in voltage.items()}

        return {
            "power": power,
            "voltage": voltage
        }
