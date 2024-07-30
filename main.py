from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager

from routers.routes import api_router
from cron_jobs.round_end import round_end_logic
from cron_jobs.cleanup_images import cleanup_unused_images

origins = ["*"]


ascheduler = AsyncIOScheduler()


ascheduler.add_job(round_end_logic, CronTrigger(day_of_week="mon", hour=0, minute=30))
ascheduler.add_job(cleanup_unused_images, CronTrigger(day_of_week="mon", hour=0, minute=45))


@asynccontextmanager
async def lifespan(app: FastAPI):
    ascheduler.start()
    print("Scheduler started")
    yield
    ascheduler.shutdown()
    print("Scheduler shut down")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
