# PeakMoto Server

Self-hosted backend stack for [PeakMoto](https://github.com/phanes-io/peakmoto) – the free motorcycle navigation app.

## Services

| Service | Purpose | Port |
|---|---|---|
| BRouter | Motorcycle routing engine | 17777 |
| TileServer-GL | Vector tile serving | 8080 |
| Traefik | Reverse proxy + TLS | 80/443 |
| Uptime Kuma | Status monitoring | 3001 |
| Watchtower | Auto-update containers | – |

## Quick Start

```bash
docker compose up -d
```

## Architecture

The server is intentionally minimal. PeakMoto follows a client-first architecture where compute-heavy tasks run on the user's device. The server provides:

- Tile hosting (raw vector tiles, rendered client-side)
- BRouter as online routing fallback (app can route offline)
- Status monitoring

## License

AGPL-3.0 – See [LICENSE](LICENSE)
