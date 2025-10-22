import React from 'react';
import {
  IonContent,
  IonPage,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonText,
} from '@ionic/react';
import './Login.css';

const LoginSimple: React.FC = () => {
  return (
    <IonPage>
      <IonContent className="login-content" fullscreen>
        <div className="login-container">
          <IonCard className="login-card">
            <IonCardHeader>
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
                  routerLink="/dashboard"
                  className="google-login-button"
                >
                  Accedi con Google
                </IonButton>

                <IonText color="medium">
                  <p className="terms-text">
                    Accedendo accetti i Termini di Servizio e la Privacy Policy
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

export default LoginSimple;
