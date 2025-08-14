"""
Task scheduler for background jobs
Handles weekly ATP rankings updates with retry logic
"""

import logging
from datetime import datetime, timedelta
from utils.logging_config import log_job_execution
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from tasks.scrapers.atp_scraper import scrape_and_update_rankings

# Configure logging
logger = logging.getLogger('scraping')

scheduler = None

def weekly_rankings_job():
    """Weekly job with detailed logging"""
    logger.info("🕒 SCHEDULED JOB TRIGGERED: Weekly Rankings Update")
    
    success = scrape_and_update_rankings()
    
    if not success:
        logger.warning("⚠️  Initial attempt failed - scheduling retry in 24 hours")
        schedule_retry()
        log_job_execution("Weekly ATP Update", False, "Scheduled retry in 24h")
    else:
        logger.info("✅ Weekly rankings update completed successfully")
        log_job_execution("Weekly ATP Update", True, "All systems normal")

def schedule_retry():
    """
    Schedule a retry attempt 24 hours later if the main job fails
    """
    retry_time = datetime.now() + timedelta(hours=24)
    
    scheduler.add_job(
        func=retry_rankings_job,
        trigger=DateTrigger(run_date=retry_time),
        id='rankings_retry',
        replace_existing=True  # Replace any existing retry job
    )
    
    logger.info(f"Retry job scheduled for {retry_time}")

def retry_rankings_job():
    """Retry job with logging"""
    logger.info("🔄 RETRY JOB TRIGGERED: Second attempt at rankings update")
    
    success = scrape_and_update_rankings()
    
    if success:
        logger.info("✅ Retry attempt successful")
        log_job_execution("ATP Update Retry", True, "Recovered from initial failure")
    else:
        logger.error("❌ Retry attempt failed - MANUAL INTERVENTION REQUIRED")
        log_job_execution("ATP Update Retry", False, "CRITICAL: Both attempts failed")

def start_scheduler():
    """Start scheduler with logging"""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running - skipping initialization")
        return scheduler
    
    scheduler = BackgroundScheduler()
    
    # Schedule weekly job
    scheduler.add_job(
        func=weekly_rankings_job,
        trigger=CronTrigger(
            day_of_week='mon',
            hour=23,
            minute=0,
            timezone='GMT'
        ),
        id='weekly_rankings',
        name='Weekly ATP Rankings Update'
    )
    
    # Infinite Loop is hidden here
    scheduler.start()
    logger.info("📅 SCHEDULER STARTED: ATP rankings job scheduled for Mondays 11 PM GMT")
    
    return scheduler


def stop_scheduler():
    """
    Stop the background scheduler
    """
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler stopped")

def get_scheduled_jobs():
    """
    Get list of currently scheduled jobs (useful for debugging)
    """
    if scheduler is not None:
        return scheduler.get_jobs()
    return []

# Manual trigger function for testing
def trigger_manual_update():
    """
    Manually trigger rankings update (useful for testing)
    """
    logger.info("Manual rankings update triggered")
    return scrape_and_update_rankings()