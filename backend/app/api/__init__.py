from .routes_detect import router as detect_router
from .routes_records import router as records_router
from .routes_stats import router as stats_router

__all__ = ["detect_router", "records_router", "stats_router"]

