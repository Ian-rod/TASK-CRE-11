
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def fetch_all_feature_collection(client) -> dict:
    """
    Retrieve all WFS features while preserving collection metadata.
    """
    all_features = []
    start_index = 0
    page_size = settings.wfs_page_size
    total_features = None
    first_response = None

    while True:
        logger.info("Fetching WFS page at index %s", start_index)

        response = client.fetch_page(
            start_index=start_index,
            count=page_size,
        )

        if first_response is None:
            first_response = response

            total = response.get(
                "numberMatched",
                response.get("totalFeatures"),
            )

            try:
                total_features = int(total) if total is not None else None
            except (ValueError, TypeError):
                total_features = None

        features = response["features"]
        received = len(features)

        if received == 0:
            if (
                total_features is not None
                and len(all_features) < total_features
            ):
                raise RuntimeError(
                    f"Incomplete WFS response: expected {total_features}, "
                    f"received {len(all_features)}."
                )
            break

        all_features.extend(features)

        logger.info(
            "Page received: %s | Total collected: %s",
            received,
            len(all_features),
        )

        if total_features is not None:
            if len(all_features) >= total_features:
                break
        elif received < page_size:
            break

        start_index += received

    if first_response is None:
        raise RuntimeError("WFS returned no response.")

    if (
        total_features is not None
        and len(all_features) != total_features
    ):
        raise RuntimeError(
            f"WFS feature count mismatch: expected {total_features}, "
            f"received {len(all_features)}."
        )

    logger.info("WFS extraction complete: %s features", len(all_features))

    return {
        "type": "FeatureCollection",
        "crs": first_response.get("crs"),
        "features": all_features,
    }


def fetch_all_features(client) -> list[dict]:
    """
    Backwards-compatible helper returning only the features.
    """
    collection = fetch_all_feature_collection(client)
    return collection["features"]
