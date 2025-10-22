import React, { useState, useEffect } from 'react';
import {
  IonContent,
  IonHeader,
  IonPage,
  IonTitle,
  IonToolbar,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonGrid,
  IonRow,
  IonCol,
  IonButton,
  IonIcon,
  IonRefresher,
  IonRefresherContent,
  RefresherEventDetail,
  useIonToast,
  IonSpinner,
  IonText,
  IonChip,
  IonBadge,
} from '@ionic/react';
import {
  homeOutline,
  carOutline,
  walletOutline,
  notificationsOutline,
  addCircleOutline,
  cashOutline,
  calendarOutline,
} from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import apiService from '../services/api';
import './Dashboard.css';

interface DashboardStats {
  totalAssets: number;
  properties: number;
  vehicles: number;
  pendingExpenses: number;
  upcomingReminders: number;
  monthlyTotal: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalAssets: 0,
    properties: 0,
    vehicles: 0,
    pendingExpenses: 0,
    upcomingReminders: 0,
    monthlyTotal: 0,
  });
  const [loading, setLoading] = useState(true);
  const [upcomingReminders, setUpcomingReminders] = useState<any[]>([]);
  const [recentExpenses, setRecentExpenses] = useState<any[]>([]);
  const [present] = useIonToast();
  const history = useHistory();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load assets
      const assetsResponse = await apiService.getAssets();
      const assets = assetsResponse.data?.data?.items || [];
      const properties = assets.filter((a: any) => a.type === 'property');
      const vehicles = assets.filter((a: any) => a.type === 'vehicle');

      // Load expenses
      const expensesResponse = await apiService.getExpenses();
      const expenses = expensesResponse.data?.data?.items || [];
      const pendingExpenses = expenses.filter(
        (e: any) => e.status === 'pending'
      );

      // Load reminders
      const remindersResponse = await apiService.getReminders();
      const reminders = remindersResponse.data?.data?.items || [];

      // Calculate monthly total
      const currentMonth = new Date().getMonth();
      const monthlyExpenses = expenses.filter((e: any) => {
        const expenseMonth = new Date(e.created_at).getMonth();
        return expenseMonth === currentMonth;
      });
      const monthlyTotal = monthlyExpenses.reduce(
        (sum: number, e: any) => sum + parseFloat(e.amount),
        0
      );

      setStats({
        totalAssets: assets.length,
        properties: properties.length,
        vehicles: vehicles.length,
        pendingExpenses: pendingExpenses.length,
        upcomingReminders: reminders.length,
        monthlyTotal,
      });

      setUpcomingReminders(reminders.slice(0, 5));
      setRecentExpenses(expenses.slice(0, 5));
    } catch (error: any) {
      console.error('Error loading dashboard data:', error);
      present({
        message: 'Errore nel caricamento dei dati',
        duration: 2000,
        color: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async (event: CustomEvent<RefresherEventDetail>) => {
    await loadDashboardData();
    event.detail.complete();
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar color="primary">
          <IonTitle>Dashboard</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonRefresher slot="fixed" onIonRefresh={handleRefresh}>
          <IonRefresherContent></IonRefresherContent>
        </IonRefresher>

        {loading ? (
          <div className="loading-container">
            <IonSpinner name="crescent" />
          </div>
        ) : (
          <div className="dashboard-container">
            {/* Stats Cards */}
            <IonGrid>
              <IonRow>
                <IonCol size="6" sizeMd="3">
                  <IonCard className="stat-card" button onClick={() => history.push('/assets?type=property')}>
                    <IonCardContent>
                      <IonIcon icon={homeOutline} className="stat-icon" />
                      <h2>{stats.properties}</h2>
                      <p>Immobili</p>
                    </IonCardContent>
                  </IonCard>
                </IonCol>
                <IonCol size="6" sizeMd="3">
                  <IonCard className="stat-card" button onClick={() => history.push('/assets?type=vehicle')}>
                    <IonCardContent>
                      <IonIcon icon={carOutline} className="stat-icon" />
                      <h2>{stats.vehicles}</h2>
                      <p>Veicoli</p>
                    </IonCardContent>
                  </IonCard>
                </IonCol>
                <IonCol size="6" sizeMd="3">
                  <IonCard className="stat-card" button onClick={() => history.push('/expenses')}>
                    <IonCardContent>
                      <IonIcon icon={walletOutline} className="stat-icon" />
                      <h2>{stats.pendingExpenses}</h2>
                      <p>Spese in sospeso</p>
                    </IonCardContent>
                  </IonCard>
                </IonCol>
                <IonCol size="6" sizeMd="3">
                  <IonCard className="stat-card" button onClick={() => history.push('/reminders')}>
                    <IonCardContent>
                      <IonIcon icon={notificationsOutline} className="stat-icon" />
                      <h2>{stats.upcomingReminders}</h2>
                      <p>Promemoria</p>
                    </IonCardContent>
                  </IonCard>
                </IonCol>
              </IonRow>
            </IonGrid>

            {/* Monthly Summary */}
            <IonCard className="summary-card">
              <IonCardHeader>
                <IonCardTitle>Riepilogo Mensile</IonCardTitle>
              </IonCardHeader>
              <IonCardContent>
                <div className="monthly-summary">
                  <IonIcon icon={cashOutline} className="summary-icon" />
                  <div className="summary-amount">
                    <IonText color="primary">
                      <h1>€ {stats.monthlyTotal.toFixed(2)}</h1>
                    </IonText>
                    <p>Spese totali questo mese</p>
                  </div>
                </div>
              </IonCardContent>
            </IonCard>

            {/* Upcoming Reminders */}
            <IonCard>
              <IonCardHeader>
                <IonCardTitle>
                  Prossimi Promemoria
                  <IonBadge color="danger" className="title-badge">
                    {upcomingReminders.length}
                  </IonBadge>
                </IonCardTitle>
              </IonCardHeader>
              <IonCardContent>
                {upcomingReminders.length > 0 ? (
                  <div className="reminders-list">
                    {upcomingReminders.map((reminder: any, index: number) => (
                      <div key={index} className="reminder-item">
                        <IonIcon icon={calendarOutline} />
                        <div className="reminder-details">
                          <strong>{reminder.message}</strong>
                          <p>
                            {new Date(reminder.date).toLocaleDateString('it-IT')}
                          </p>
                        </div>
                        <IonChip color="warning">
                          {reminder.type.toUpperCase()}
                        </IonChip>
                      </div>
                    ))}
                  </div>
                ) : (
                  <IonText color="medium">
                    <p>Nessun promemoria in arrivo</p>
                  </IonText>
                )}
                <IonButton
                  expand="block"
                  fill="outline"
                  routerLink="/reminders"
                  className="view-all-button"
                >
                  Vedi tutti
                </IonButton>
              </IonCardContent>
            </IonCard>

            {/* Recent Expenses */}
            <IonCard>
              <IonCardHeader>
                <IonCardTitle>Spese Recenti</IonCardTitle>
              </IonCardHeader>
              <IonCardContent>
                {recentExpenses.length > 0 ? (
                  <div className="expenses-list">
                    {recentExpenses.map((expense: any, index: number) => (
                      <div key={index} className="expense-item">
                        <div className="expense-info">
                          <strong>{expense.category}</strong>
                          <p>{expense.description || 'Nessuna descrizione'}</p>
                        </div>
                        <div className="expense-amount">
                          <IonText color="danger">
                            <strong>€ {parseFloat(expense.amount).toFixed(2)}</strong>
                          </IonText>
                          <IonChip
                            color={
                              expense.status === 'paid'
                                ? 'success'
                                : expense.status === 'overdue'
                                ? 'danger'
                                : 'warning'
                            }
                          >
                            {expense.status}
                          </IonChip>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <IonText color="medium">
                    <p>Nessuna spesa registrata</p>
                  </IonText>
                )}
                <IonButton
                  expand="block"
                  fill="outline"
                  routerLink="/expenses"
                  className="view-all-button"
                >
                  Vedi tutte
                </IonButton>
              </IonCardContent>
            </IonCard>

            {/* Quick Actions */}
            <IonCard className="quick-actions-card">
              <IonCardHeader>
                <IonCardTitle>Azioni Rapide</IonCardTitle>
              </IonCardHeader>
              <IonCardContent>
                <IonGrid>
                  <IonRow>
                    <IonCol>
                      <IonButton
                        expand="block"
                        color="primary"
                        routerLink="/assets/add"
                      >
                        <IonIcon slot="start" icon={addCircleOutline} />
                        Aggiungi Bene
                      </IonButton>
                    </IonCol>
                    <IonCol>
                      <IonButton
                        expand="block"
                        color="secondary"
                        routerLink="/expenses/add"
                      >
                        <IonIcon slot="start" icon={walletOutline} />
                        Nuova Spesa
                      </IonButton>
                    </IonCol>
                  </IonRow>
                </IonGrid>
              </IonCardContent>
            </IonCard>
          </div>
        )}
      </IonContent>
    </IonPage>
  );
};

export default Dashboard;