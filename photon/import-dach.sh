#!/bin/sh
set -e
echo "Importing DACH data from Photon planet dump (streaming + filtering)..."
echo "This will download ~25GB and filter to DE,AT,CH only."
echo "Estimated time: 1-2 hours depending on bandwidth."

cd /photon

wget -O - https://download1.graphhopper.com/public/photon-dump-planet-1.0-latest.jsonl.zst \
  | zstd -d \
  | java -Xmx6g -jar photon.jar import -import-file - -country-codes DE,AT,CH

echo "Import complete!"
