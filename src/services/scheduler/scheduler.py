from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from .jobs.check_active_alarms import job_check_active_alarms


def create_and_start_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Create scheduler, add jobs and start it"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=job_check_active_alarms,
        trigger="interval",
        kwargs={"bot": bot},
        seconds=60
    )
    return scheduler
