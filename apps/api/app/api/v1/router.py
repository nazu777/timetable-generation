from fastapi import APIRouter

from app.api.v1.timetables import router as timetables_router

api_router = APIRouter()
api_router.include_router(timetables_router, tags=["timetables"])
