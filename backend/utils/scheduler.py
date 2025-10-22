"""
Scheduler service for automated reminders and tasks
"""
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Reminder, User, Asset, Expense
from utils.notifier import NotificationService
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """Background scheduler for automated reminders and tasks"""
    
    def __init__(self):
        self.scheduler = None
        self.notification_service = NotificationService()
        self.setup_scheduler()
    
    def setup_scheduler(self):
        """Setup APScheduler with Redis jobstore"""
        try:
            # Configure jobstore (use in-memory if Redis not available)
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                jobstores = {
                    'default': RedisJobStore(
                        host=redis_url.split('@')[1].split(':')[0] if '@' in redis_url else 'localhost',
                        port=int(redis_url.split(':')[-1]) if ':' in redis_url else 6379,
                        db=0
                    )
                }
            else:
                jobstores = {'default': 'memory'}
            
            executors = {
                'default': ThreadPoolExecutor(max_workers=4),
            }
            
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='Europe/Rome'
            )
            
            logger.info("Scheduler configured successfully")
            
        except Exception as e:
            logger.error(f"Scheduler setup error: {str(e)}")
    
    async def start(self):
        """Start the scheduler"""
        if self.scheduler:
            self.scheduler.start()
            
            # Schedule recurring jobs
            await self.schedule_recurring_jobs()
            
            logger.info("Scheduler started")
    
    async def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    async def schedule_recurring_jobs(self):
        """Schedule all recurring jobs"""
        try:
            # Daily reminder check at 9:00 AM
            self.scheduler.add_job(
                func=self.check_reminders,
                trigger="cron",
                hour=9,
                minute=0,
                id="daily_reminder_check",
                replace_existing=True
            )
            
            # IMU reminder check (run twice yearly)
            self.scheduler.add_job(
                func=self.check_imu_reminders,
                trigger="cron",
                month="6,12",
                day=1,
                hour=9,
                minute=0,
                id="imu_reminder_check",
                replace_existing=True
            )
            
            # Weekly vehicle reminder check
            self.scheduler.add_job(
                func=self.check_vehicle_reminders,
                trigger="cron",
                day_of_week="mon",
                hour=10,
                minute=0,
                id="vehicle_reminder_check",
                replace_existing=True
            )
            
            logger.info("Recurring jobs scheduled")
            
        except Exception as e:
            logger.error(f"Failed to schedule recurring jobs: {str(e)}")
    
    async def check_reminders(self):
        """Check and send due reminders"""
        try:
            db = SessionLocal()
            
            # Get reminders due today or overdue
            tomorrow = datetime.now() + timedelta(days=1)
            due_reminders = db.query(Reminder).filter(
                Reminder.date <= tomorrow,
                Reminder.notified == False
            ).all()
            
            for reminder in due_reminders:
                await self.send_reminder_notification(reminder, db)
                reminder.notified = True
            
            db.commit()
            db.close()
            
            logger.info(f"Processed {len(due_reminders)} reminders")
            
        except Exception as e:
            logger.error(f"Reminder check failed: {str(e)}")
    
    async def check_imu_reminders(self):
        """Check for IMU payment reminders"""
        try:
            db = SessionLocal()
            
            # Get properties with IMU automation enabled
            current_month = datetime.now().month
            is_first_payment = current_month == 6
            is_second_payment = current_month == 12
            
            if is_first_payment or is_second_payment:
                properties = db.query(Asset).join(Asset.automations).filter(
                    Asset.type == "property",
                    Asset.automations.any(imu_calc=True)
                ).all()
                
                for property_asset in properties:
                    await self.create_imu_reminder(property_asset, is_first_payment, db)
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"IMU reminder check failed: {str(e)}")
    
    async def check_vehicle_reminders(self):
        """Check for vehicle-related reminders"""
        try:
            db = SessionLocal()
            
            # This would typically check external APIs or predefined schedules
            # For now, we'll create placeholder reminders
            vehicles = db.query(Asset).filter(Asset.type == "vehicle").all()
            
            for vehicle in vehicles:
                # Create reminders based on vehicle registration date, etc.
                pass
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Vehicle reminder check failed: {str(e)}")
    
    async def send_reminder_notification(self, reminder: Reminder, db: Session):
        """Send notification for a specific reminder"""
        try:
            asset = reminder.asset
            user = asset.owner
            
            # For now, we'll use a placeholder FCM token
            # In production, this would be stored in the user profile
            fcm_token = "placeholder_token"
            
            if reminder.type == "imu":
                await self.notification_service.send_imu_reminder(
                    token=fcm_token,
                    asset_name=asset.name,
                    due_date=reminder.date.strftime("%d/%m/%Y"),
                    amount=0  # Calculate from asset details
                )
            elif reminder.type in ["bollo", "assicurazione", "revisione"]:
                await self.notification_service.send_vehicle_reminder(
                    token=fcm_token,
                    vehicle_name=asset.name,
                    reminder_type=reminder.type,
                    due_date=reminder.date.strftime("%d/%m/%Y")
                )
            
            logger.info(f"Sent {reminder.type} reminder for asset {asset.name}")
            
        except Exception as e:
            logger.error(f"Failed to send reminder notification: {str(e)}")
    
    async def create_imu_reminder(self, property_asset: Asset, is_first_payment: bool, db: Session):
        """Create IMU reminder for a property"""
        try:
            due_date = datetime(datetime.now().year, 6 if is_first_payment else 12, 16)
            reminder_date = due_date - timedelta(days=15)  # 15 days before
            
            # Check if reminder already exists
            existing = db.query(Reminder).filter(
                Reminder.asset_id == property_asset.id,
                Reminder.type == "imu",
                Reminder.date == reminder_date
            ).first()
            
            if not existing:
                reminder = Reminder(
                    asset_id=property_asset.id,
                    type="imu",
                    date=reminder_date,
                    message=f"Promemoria pagamento IMU {'primo' if is_first_payment else 'secondo'} acconto per {property_asset.name}",
                    notified=False
                )
                db.add(reminder)
                logger.info(f"Created IMU reminder for {property_asset.name}")
        
        except Exception as e:
            logger.error(f"Failed to create IMU reminder: {str(e)}")
    
    def add_custom_reminder(self, run_date: datetime, func, *args, **kwargs):
        """Add a custom one-time reminder"""
        if self.scheduler:
            self.scheduler.add_job(
                func=func,
                trigger="date",
                run_date=run_date,
                args=args,
                kwargs=kwargs
            )