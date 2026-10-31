#Settings class for the the application 
import os

from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    wfs_base_url: str = os.getenv(
        "WFS_BASE_URL",
        "https://gdi.berlin.de/services/wfs/brw2026"  #used this instead of https://gdi.berlin.de/services/wfs/boris
    )

    wfs_layer: str = os.getenv(
        "WFS_LAYER",
        "brw2026:brw2026_vector"
    )

    wfs_version: str = os.getenv("WFS_VERSION", "2.0.0")

    wfs_page_size: int = int(os.getenv("WFS_PAGE_SIZE", "250"))

    wfs_timeout: int = int(os.getenv("WFS_TIMEOUT", "30"))

    source_crs: str = os.getenv("SOURCE_CRS", "EPSG:25833")

    target_crs: str = os.getenv("TARGET_CRS", "EPSG:25832")

    db_uri: str = os.getenv("DB_URI", "")

    db_schema: str = os.getenv("DB_SCHEMA", "iris_staging")

    db_table: str = os.getenv("DB_TABLE", "")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
