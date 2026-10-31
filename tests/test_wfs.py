
import logging

from app.ingestion.wfs_client import WFSClient
from app.ingestion.pagination import fetch_all_features

logging.basicConfig(level=logging.INFO)

client = WFSClient()

try:
    features = fetch_all_features(client)

    print("\nWFS EXTRACTION SUCCESSFUL")
    print("-------------------------")
    print("Total features retrieved:", len(features))

    print("\nFirst five records:")

    for feature in features[:5]:
        properties = feature.get("properties", {})

        print(
            "Zone ID:", properties.get("brwid"),
            "| Land value:", properties.get("brw"),
            "| District:", properties.get("bezirk"),
        )

except Exception as error:
    print("WFS EXTRACTION FAILED:", error)
