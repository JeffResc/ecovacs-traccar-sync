# ecovacs-traccar-sync

Sync GPS location and battery data from [Ecovacs](https://www.ecovacs.com/) robot vacuums to a [Traccar](https://www.traccar.org/) GPS tracking server in real time using the [OsmAnd protocol](https://www.traccar.org/osmand/).

## How It Works

The application connects to the Ecovacs cloud API via MQTT, subscribes to GPS position and battery events from your robot vacuum, and forwards each position update to your Traccar server. This lets you track your robot's location and battery level alongside other devices in Traccar.

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- An Ecovacs account with a registered robot vacuum
- A running [Traccar](https://www.traccar.org/) server with the OsmAnd protocol enabled (default port 5055)

## Configuration

The following environment variables are required:

| Variable | Description | Example |
|---|---|---|
| `ECOVACS_EMAIL` | Ecovacs account email | `user@example.com` |
| `ECOVACS_PASSWORD` | Ecovacs account password | `mypassword` |
| `COUNTRY_CODE` | 2-letter country code | `US` |
| `TRACCAR_URL` | Traccar OsmAnd endpoint URL | `http://localhost:5055` |

## Usage

### Local

```bash
uv sync
python main.py
```

### Docker

```bash
docker build -t ecovacs-traccar-sync .

docker run \
  -e ECOVACS_EMAIL="user@example.com" \
  -e ECOVACS_PASSWORD="mypassword" \
  -e COUNTRY_CODE="US" \
  -e TRACCAR_URL="http://traccar:5055" \
  ecovacs-traccar-sync
```

A pre-built image is available at `ghcr.io/jeffresc/ecovacs-traccar-sync`.

### Kubernetes (Helm)

A Helm chart is included in the `chart/` directory.

```bash
# Create a secret with your Ecovacs credentials
kubectl create secret generic ecovacs-credentials \
  --from-literal=ECOVACS_EMAIL=user@example.com \
  --from-literal=ECOVACS_PASSWORD=mypassword

# Install the chart
helm install ecovacs-traccar-sync chart/ \
  --set env.countryCode="US" \
  --set env.traccarUrl="http://traccar:5055"
```

See [`chart/values.yaml`](chart/values.yaml) for all configurable values.

## License

[MIT](LICENSE)
