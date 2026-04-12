# GraphHopper Routing

PeakMoto uses a self-hosted GraphHopper instance for turn-by-turn routing with curvature-based motorcycle profiles.

## Why not Docker?

GraphHopper with the DACH dataset (~4GB OSM + elevation) needs 20GB+ of RAM at build time and has a ~32min cold start. Running it as a **native systemd service** avoids Docker's memory overhead and gives us better control over JVM heap settings.

## Running natively

Copy `config.yml` to the server and run GraphHopper directly. Example systemd service:

```ini
[Unit]
Description=GraphHopper Routing Engine
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/peakmoto-server/graphhopper
ExecStart=/usr/bin/java -Xmx20g -Xms10g -jar graphhopper-web-11.0.jar server config.yml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Install the GraphHopper jar to `/opt/peakmoto-server/graphhopper/graphhopper-web-11.0.jar` and download the DACH OSM extract:

```bash
wget https://download.geofabrik.de/europe/dach-latest.osm.pbf \
  -O /opt/peakmoto-server/graphhopper/dach-latest.osm.pbf
```

## Traefik routing

Since GraphHopper is not in the Docker network, Traefik uses a **file provider** rule to route `routing.peakmoto.app` → `http://<host-ip>:8989`. See your Traefik dynamic config.

## Custom Profiles

PeakMoto exposes four motorcycle profiles with increasing curvature preference:

| Profile | Description | distance_influence |
|---|---|---|
| `motorcycle_fast` | Shortest route, highways OK | 90 |
| `motorcycle_balanced` | Mix of highways and country roads, mild curve preference | 70 |
| `motorcycle_curvy` | Prefers curvy secondary/tertiary roads, hates straight highways | 40 |
| `motorcycle_twisty` | Extreme curve preference, accepts big detours | 30 |

The curvy and twisty profiles use **curvature-coupled road class rules** so the same profile works regionally:

- In NRW (Paderborn), straight B-roads are penalized → routes prefer L/K-Straßen
- In the Black Forest, the curvy B500 passes the curvature threshold → used
- In the Alps, curvy pass roads (B107 Großglockner, B179 Fernpass) are rewarded

## Landmarks (LM)

Only `motorcycle_fast`, `motorcycle_balanced`, and legacy `motorcycle` have Landmark preparation. `motorcycle_curvy` and `motorcycle_twisty` use on-the-fly routing (~200-400ms per query, still fast enough). This was necessary because the aggressive curvature weights in twisty caused Integer overflow during LM precomputation.

App queries for curvy/twisty must pass `lm.disable=true`.

## Rebuild

Any change to `priority` or `speed` rules in `custom_model` requires a full graph rebuild:

```bash
systemctl stop graphhopper
rm -rf /opt/peakmoto-server/graphhopper/graph-cache
systemctl start graphhopper
# Wait ~28 minutes for full rebuild (OSM import + urban density + subnetwork prep)
```
