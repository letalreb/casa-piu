# Casa&Più - Family Expense Management App

This is a complete full-stack application for managing family expenses related to real estate and vehicles.

## Tech Stack
- Frontend: Ionic + React + Capacitor
- Backend: FastAPI (Python 3.12) + Uvicorn
- Database: PostgreSQL (Supabase)
- Authentication: OAuth2 Google (via Supabase Auth)
- Push notifications: Firebase Cloud Messaging
- AI suggestions: OpenAI/Claude API integration
- Hosting: Backend (Render.com), DB/Auth (Supabase), Frontend (Firebase Hosting)

## Project Structure
```
/
├── backend/          # FastAPI backend
├── frontend/         # Ionic React frontend
├── docs/            # Documentation
└── deploy/          # Deployment scripts
```

## Features
- Property and vehicle management
- Automatic IMU calculations and F24 PDF generation
- Intelligent reminders for payments and deadlines
- OCR bill parsing and expense tracking
- AI-powered saving suggestions
- Push notifications
- Google OAuth authentication

## Development Guidelines
- Use TypeScript for frontend
- Follow REST API conventions
- Implement proper error handling
- Use environment variables for configuration
- Write clear, documented code
- Follow Italian business requirements (IMU, F24)