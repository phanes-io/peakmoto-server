# PeakMoto Server

Self-hosted backend stack for [PeakMoto](https://github.com/phanes-io/peakmoto) – the free motorcycle navigation app.

## Services

| Service | Subdomain | Purpose | Runs as |
|---|---|---|---|
| **GraphHopper** | `routing.peakmoto.app` | Curvature-aware motorcycle routing (DACH) | systemd native |
| **Photon** | `photon.peakmoto.app` | Autocomplete geocoder | Docker |
| **TileServer-GL** | `tiles.peakmoto.app` | Custom map tiles | Docker |
| **Feedback Proxy** | `feedback.peakmoto.app` | Anonymous route feedback → Telegram | Docker |
| **Watchtower** | – | Auto-update containers | Docker |

Traefik (external) handles TLS + routing via Cloudflare DNS challenge.

## Directory Layout

```
.
├── docker-compose.yml     # Photon + TileServer + Feedback + Watchtower
├── feedback/              # FastAPI proxy to Telegram
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── docker-compose.yml # Standalone compose for just this service
│   └── README.md
├── graphhopper/           # Native systemd service config
│   ├── config.yml         # Custom motorcycle profiles
│   └── README.md
├── photon/                # Komoot Photon build
│   ├── Dockerfile
│   └── import-dach.sh
└── styles/                # Custom map styles
    └── peakmoto-dark.json
```

## Quick Start

### Docker services (Photon, Tileserver, Feedback, Watchtower)

```bash
# Feedback needs Telegram credentials
cp feedback/.env.example feedback/.env
# Edit feedback/.env with your bot token + chat ID

docker compose up -d
```

### GraphHopper (native)

See [graphhopper/README.md](graphhopper/README.md) for setup. Runs as systemd service because of RAM requirements (20GB+ for DACH graph).

## Architecture

PeakMoto follows a **client-first architecture** — most compute happens on the user's device (maps, GPS, navigation logic). The server provides:

- **Routing** (GraphHopper with DACH OSM extract + custom motorcycle profiles)
- **Geocoding** (Photon, self-hosted for privacy + speed)
- **Tile hosting** (offline-cacheable map tiles)
- **Anonymous feedback collection** (Telegram-based, no DB)

No user accounts, no user tracking, no analytics. See [PeakMoto Privacy Policy](https://github.com/phanes-io/peakmoto/blob/main/PRIVACY.md).

## Routing Profiles

The motorcycle routing is **curvature-aware**: gerade Bundesstraßen werden bestraft, kurvige Landstraßen belohnt. The same rules work across DACH — the B500 in Schwarzwald is treated differently from the B1 in Paderborn because of OSM's curvature metric per edge.

Four profiles exposed:
- `motorcycle_fast` – shortest route
- `motorcycle_balanced` – mix with mild curve preference
- `motorcycle_curvy` – prefers curvy country roads
- `motorcycle_twisty` – maximum curvature, big detours accepted

See [graphhopper/config.yml](graphhopper/config.yml) for the full rules.

## License

AGPL-3.0 – See [LICENSE](LICENSE)
