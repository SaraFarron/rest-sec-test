from app.routers.buildings import router as buildings_router
from app.routers.activities import router as activities_router
from app.routers.organizations import router as organizations_router

__all__ = ["buildings_router", "activities_router", "organizations_router"]
