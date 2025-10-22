import React, { useState } from 'react';
import {
  IonContent,
  IonPage,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonImg,
  IonText,
  IonSpinner,
  useIonToast,
} from '@ionic/react';
import { useHistory } from 'react-router-dom';
import authService from '../services/auth';
import apiService from '../services/api';
import './Login.css';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [present] = useIonToast();
  const history = useHistory();

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      await authService.signInWithGoogle();
      
      // Get session token
      const token = await authService.getAccessToken();
      if (token) {
        localStorage.setItem('auth_token', token);
        
        // Verify token with backend
        await apiService.verifyToken(token);
        
        present({
          message: 'Login effettuato con successo!',
          duration: 2000,
          color: 'success',
        });
        
        history.push('/dashboard');
      }
    } catch (error: any) {
      console.error('Login error:', error);
      present({
        message: error.message || 'Errore durante il login',
        duration: 3000,
        color: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <IonPage>
      <IonContent className="login-content" fullscreen>
        <div className="login-container">
          <IonCard className="login-card">
            <IonCardHeader>
              <div className="logo-container">
                <IonImg
                  src="/assets/logo.svg"
                  alt="Casa&Più Logo"
                  className="logo"
                />
              </div>
              <IonCardTitle className="app-title">Casa&Più</IonCardTitle>
              <IonText color="medium">
                <p className="app-subtitle">
                  Gestione familiare di immobili e veicoli
                </p>
              </IonText>
            </IonCardHeader>

            <IonCardContent>
              <div className="login-actions">
                <IonButton
                  expand="block"
                  size="large"
                  onClick={handleGoogleLogin}
                  disabled={loading}
                  className="google-login-button"
                >
                  {loading ? (
                    <IonSpinner name="crescent" />
                  ) : (
                    <>
                      <img
                        src="/assets/google-icon.svg"
                        alt="Google"
                        className="google-icon"
                      />
                      Accedi con Google
                    </>
                  )}
                </IonButton>

                <IonText color="medium">
                  <p className="terms-text">
                    Accedendo accetti i{' '}
                    <a href="/terms">Termini di Servizio</a> e la{' '}
                    <a href="/privacy">Privacy Policy</a>
                  </p>
                </IonText>
              </div>
            </IonCardContent>
          </IonCard>

          <div className="features-container">
            <div className="feature">
              <ion-icon name="home-outline" size="large"></ion-icon>
              <h3>Gestione Immobili</h3>
              <p>Calcolo IMU automatico e generazione F24</p>
            </div>
            <div className="feature">
              <ion-icon name="car-outline" size="large"></ion-icon>
              <h3>Gestione Veicoli</h3>
              <p>Promemoria per bollo, assicurazione e revisione</p>
            </div>
            <div className="feature">
              <ion-icon name="notifications-outline" size="large"></ion-icon>
              <h3>Promemoria Intelligenti</h3>
              <p>Non perdere mai una scadenza importante</p>
            </div>
            <div className="feature">
              <ion-icon name="bulb-outline" size="large"></ion-icon>
              <h3>Suggerimenti AI</h3>
              <p>Consigli personalizzati per risparmiare</p>
            </div>
          </div>
        </div>
      </IonContent>
    </IonPage>
  );
};

export default Login;