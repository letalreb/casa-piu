/**
 * Firebase Cloud Messaging Service for Push Notifications
 */
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

class NotificationService {
  private app: any;
  private messaging: any;

  constructor() {
    try {
      this.app = initializeApp(firebaseConfig);
      this.messaging = getMessaging(this.app);
    } catch (error) {
      console.error('Firebase initialization error:', error);
    }
  }

  async requestPermission() {
    try {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        console.log('Notification permission granted');
        return true;
      } else {
        console.log('Notification permission denied');
        return false;
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  }

  async getToken() {
    try {
      const vapidKey = import.meta.env.VITE_FIREBASE_VAPID_KEY;
      const token = await getToken(this.messaging, { vapidKey });
      console.log('FCM Token:', token);
      return token;
    } catch (error) {
      console.error('Error getting FCM token:', error);
      return null;
    }
  }

  onMessageReceived(callback: (payload: any) => void) {
    if (this.messaging) {
      onMessage(this.messaging, (payload) => {
        console.log('Message received:', payload);
        callback(payload);
      });
    }
  }

  async initializeNotifications() {
    const hasPermission = await this.requestPermission();
    if (hasPermission) {
      const token = await this.getToken();
      if (token) {
        // Save token to backend
        localStorage.setItem('fcm_token', token);
        return token;
      }
    }
    return null;
  }
}

export default new NotificationService();