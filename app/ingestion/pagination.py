# get te records page by page
import logging

from app.config import settings
from app.ingestion.wfs_client import WFSClient

logger = logging.getLogger(__name__)

def fetch_all_features(client: WFSClient) -> list[dict]:
    """
    Retrieve all available WFS features using pagination.

    Returns a list containing all GeoJSON features.
    """

    all_features = []
    start_index = 0
    page_size = settings.wfs_page_size

    total_features = None

    while True:
        logger.info(
            "Fetching page starting at index %s",
            start_index,
        )

        response = client.fetch_page(
            start_index=start_index,
            count=page_size,
        )

        features = response["features"]

        # Read the total number of matching features.
        if total_features is None:
            total = response.get(
                "numberMatched",
                response.get("totalFeatures"),
            )

            try:
                total_features = int(total) if total is not None else None
            except (ValueError, TypeError):
                total_features = None

        received = len(features)

        # Stop if the service has no more features.
        if received == 0:
            if total_features is not None and len(all_features) < total_features:
                raise RuntimeError(
                    "WFS pagination ended before all expected features "
                    f"were retrieved. Expected {total_features}, "
                    f"received {len(all_features)}."
                )
            break

        all_features.extend(features)

        logger.info(
            "Retrieved %s features. Total collected: %s",
            received,
            len(all_features),
        )

        # Stop once we have retrieved all matching features.
        if total_features is not None:
            if len(all_features) >= total_features:
                break

        # Without a known total, a short page indicates the end.
        elif received < page_size:
            break

        # Move to the next page based on the received
        start_index += received

    logger.info(
        "Pagination complete. Total features retrieved: %s",
        len(all_features),
    )

    return all_features