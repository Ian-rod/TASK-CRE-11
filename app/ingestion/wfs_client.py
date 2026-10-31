import logging
import requests
from app.config import settings
logger = logging.getLogger(__name__)

class WFSClient:
    def __init__(self):
        # get values from the config
        self.base_url = settings.wfs_base_url
        self.layer = settings.wfs_layer
        self.timeout = settings.wfs_timeout
        self.session = requests.Session()

    def fetch_page(self, start_index: int = 0, count: int | None = None) -> dict:
        """
        Fetch one page of GeoJSON features from the WFS service.
        """

        if count is None:
            count = settings.wfs_page_size

        if start_index < 0 or count <= 0:
            raise ValueError("start_index must be >= 0 and count must be > 0")

        params = {
            "service": "WFS",
            "version": settings.wfs_version,
            "request": "GetFeature",
            "typeNames": self.layer,
            "outputFormat": "application/json",
            "srsName": settings.source_crs,
            "startIndex": start_index,
            "count": count,
        }

        logger.info(
            "Requesting WFS features: start_index=%s, count=%s",
            start_index,
            count,
        )

        try:
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as exc:
            logger.error("WFS request failed: %s", exc)
            raise RuntimeError("Unable to retrieve features from WFS") from exc

        except ValueError as exc:
            logger.error("WFS returned an invalid JSON response")
            raise RuntimeError("WFS response was not valid JSON") from exc

        if data.get("type") != "FeatureCollection":
            raise RuntimeError(
                "Unexpected WFS response: expected a GeoJSON FeatureCollection"
            )

        features = data.get("features")

        if not isinstance(features, list):
            raise RuntimeError("WFS response does not contain a valid features list")

        logger.info("Retrieved %s features", len(features))

        return data