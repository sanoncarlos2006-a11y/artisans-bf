from app.routes.auth import router as auth_router
from app.routes.businesses import router as businesses_router
from app.routes.health import router as health_router

__all__ = [
    "auth_router",
    "businesses_router",
    "health_router",
]
from app.routes.ai import router as ai_router
from app.routes.comments import router as comments_router
from app.routes.search import router as search_router
