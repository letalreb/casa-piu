/**
 * API Service for Casa&Più Backend
 */
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async verifyToken(token: string) {
    return this.api.post('/auth/verify-token', { token });
  }

  async register(userData: any) {
    return this.api.post('/auth/register', userData);
  }

  async getProfile() {
    return this.api.get('/auth/profile');
  }

  async updateProfile(data: any) {
    return this.api.put('/auth/profile', data);
  }

  // Assets
  async getAssets(type?: string, page = 1, perPage = 10) {
    return this.api.get('/assets/', {
      params: { asset_type: type, page, per_page: perPage },
    });
  }

  async getAsset(id: number) {
    return this.api.get(`/assets/${id}`);
  }

  async createAsset(assetData: any) {
    return this.api.post('/assets/', assetData);
  }

  async updateAsset(id: number, assetData: any) {
    return this.api.put(`/assets/${id}`, assetData);
  }

  async deleteAsset(id: number) {
    return this.api.delete(`/assets/${id}`);
  }

  // Expenses
  async getExpenses(page = 1, perPage = 10) {
    return this.api.get('/expenses/', {
      params: { page, per_page: perPage },
    });
  }

  async getExpense(id: number) {
    return this.api.get(`/expenses/${id}`);
  }

  async createExpense(expenseData: any) {
    return this.api.post('/expenses/', expenseData);
  }

  async updateExpense(id: number, expenseData: any) {
    return this.api.put(`/expenses/${id}`, expenseData);
  }

  async deleteExpense(id: number) {
    return this.api.delete(`/expenses/${id}`);
  }

  // Reminders
  async getReminders(page = 1, perPage = 10) {
    return this.api.get('/reminders/', {
      params: { page, per_page: perPage },
    });
  }

  async createReminder(reminderData: any) {
    return this.api.post('/reminders/', reminderData);
  }

  async runReminders() {
    return this.api.post('/reminders/run');
  }

  // Automations
  async getAutomation(assetId: number) {
    return this.api.get(`/automations/${assetId}`);
  }

  async createAutomation(automationData: any) {
    return this.api.post('/automations/', automationData);
  }

  async updateAutomation(id: number, automationData: any) {
    return this.api.put(`/automations/${id}`, automationData);
  }

  // IMU & F24
  async calculateIMU(data: any) {
    return this.api.post('/f24/calculate-imu', data);
  }

  async generateF24(assetId: number, paymentType: string) {
    return this.api.post('/f24/generate', {
      asset_id: assetId,
      payment_type: paymentType,
    });
  }

  // AI Suggestions
  async getAISuggestions(assetId?: number, periodMonths = 6) {
    return this.api.post('/suggestions/ai', {
      asset_id: assetId,
      period_months: periodMonths,
    });
  }

  // Documents
  async uploadDocument(assetId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('asset_id', assetId.toString());

    return this.api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  async parseDocument(documentId: number) {
    return this.api.post(`/documents/${documentId}/parse`);
  }
}

export default new ApiService();