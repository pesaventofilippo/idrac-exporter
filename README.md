# idrac-exporter
A very basic Prometheus exporter that exports fan and power supply stats for Dell iDRACs.  

## Usage
The exporter is configured using environment variables.  
Every variable has a default value, except for the list of iDRACs to monitor.

| Variable            | Description                           | Default                |
|---------------------|---------------------------------------|------------------------|
| `PROMETHEUS_PORT`   | The port the exporter listens on      | `8000`                 |
| `PROMETHEUS_PREFIX` | The prefix for the Prometheus metrics | `"idrac"`              |

## Docker
The exporter is available as a Docker image on the [GitHub Container Registry](https://ghcr.io/pesaventofilippo/idrac-exporter).

To run the exporter using Docker, you can use the following command:
```bash
docker run -d -p 8000:8000 \
    -e IDRAC_HOSTS='[{"host": "192.168.1.100", "user": "root", "password": "calvin"}, {"host": "192.168.1.101", "user": "admin", "password": "password123"}]' \
    ghcr.io/pesaventofilippo/idrac-exporter
```

### docker-compose
You can also use `docker-compose` to run the exporter.
Here is an example `docker-compose.yml` file:
```yaml
services:
  idrac-exporter:
    image: ghcr.io/pesaventofilippo/idrac-exporter
    ports:
      - 8000:8000
    environment:
      IDRAC_HOSTS=[{"host": "192.168.1.100", "user": "root", "password": "calvin"}, {"host": "192.168.1.101", "user": "admin", "password": "password123"}]
```
