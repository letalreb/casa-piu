"""
Notification service for push notifications via Firebase
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Firebase Cloud Messaging service for push notifications"""
    
    def __init__(self):
        self.app = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
            
            if not firebase_key_path or not os.path.exists(firebase_key_path):
                logger.warning("Firebase credentials not found, notifications disabled")
                return
            
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_key_path)
                self.app = firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized")
            else:
                self.app = firebase_admin.get_app()
                
        except Exception as e:
            logger.error(f"Firebase initialization error: {str(e)}")
    
    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Dict[str, Any] = None
    ) -> bool:
        """Send push notification to a single device"""
        if not self.app:
            logger.warning("Firebase not initialized, skipping notification")
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        channel_id="casapiu_reminders",
                        priority=messaging.Priority.HIGH,
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            badge=1,
                            sound="default",
                        )
                    )
                )
            )
            
            response = messaging.send(message)
            logger.info(f"Notification sent successfully: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    async def send_bulk_notifications(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send push notifications to multiple devices"""
        if not self.app:
            logger.warning("Firebase not initialized, skipping notifications")
            return {"success": 0, "failure": len(tokens)}
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        channel_id="casapiu_reminders",
                        priority=messaging.Priority.HIGH,
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            badge=1,
                            sound="default",
                        )
                    )
                )
            )
            
            response = messaging.send_multicast(message)
            logger.info(f"Bulk notifications sent: {response.success_count} success, {response.failure_count} failed")
            
            return {
                "success": response.success_count,
                "failure": response.failure_count,
                "responses": response.responses
            }
            
        except Exception as e:
            logger.error(f"Failed to send bulk notifications: {str(e)}")
            return {"success": 0, "failure": len(tokens)}
    
    async def send_imu_reminder(self, token: str, asset_name: str, due_date: str, amount: float):
        """Send IMU payment reminder"""
        return await self.send_notification(
            token=token,
            title="🏠 Promemoria IMU",
            body=f"Pagamento IMU per {asset_name} in scadenza il {due_date}. Importo: €{amount:.2f}",
            data={
                "type": "imu_reminder",
                "asset_name": asset_name,
                "due_date": due_date,
                "amount": str(amount)
            }
        )
    
    async def send_vehicle_reminder(self, token: str, vehicle_name: str, reminder_type: str, due_date: str):
        """Send vehicle-related reminder (bollo, assicurazione, revisione)"""
        reminder_titles = {
            "bollo": "🚗 Promemoria Bollo Auto",
            "assicurazione": "🛡️ Promemoria Assicurazione",
            "revisione": "🔧 Promemoria Revisione"
        }
        
        return await self.send_notification(
            token=token,
            title=reminder_titles.get(reminder_type, "🚗 Promemoria Veicolo"),
            body=f"{reminder_type.capitalize()} per {vehicle_name} in scadenza il {due_date}",
            data={
                "type": f"{reminder_type}_reminder",
                "vehicle_name": vehicle_name,
                "due_date": due_date
            }
        )
    
    async def send_bill_reminder(self, token: str, bill_description: str, amount: float, due_date: str):
        """Send bill payment reminder"""
        return await self.send_notification(
            token=token,
            title="💡 Promemoria Bolletta",
            body=f"{bill_description} in scadenza il {due_date}. Importo: €{amount:.2f}",
            data={
                "type": "bill_reminder",
                "description": bill_description,
                "amount": str(amount),
                "due_date": due_date
            }
        )