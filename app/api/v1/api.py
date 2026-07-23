from fastapi import APIRouter

from app.api.v1.endpoints import admin, appointments, auth, salons, services, staff, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(salons.router, prefix="/salons", tags=["salons"])
api_router.include_router(staff.router, prefix="/staff", tags=["staff"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
