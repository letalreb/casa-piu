#!/bin/bash

# Casa&Più Deployment Script

set -e

echo "🚀 Starting Casa&Più Deployment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
print_status "Checking required tools..."

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker."
    exit 1
fi

if ! command -v firebase &> /dev/null; then
    print_error "Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Backend Deployment
print_status "Deploying backend to Render.com..."
print_status "Please ensure you have:"
print_status "  1. Created a Render account at https://render.com"
print_status "  2. Connected your GitHub repository"
print_status "  3. Created a new Web Service from the Render dashboard"
print_status "  4. Set environment variables in Render dashboard"
print_status ""
print_status "Backend will be automatically deployed when you push to main branch"

# Frontend Build
print_status "Building frontend..."
cd frontend
npm run build

if [ $? -eq 0 ]; then
    print_success "Frontend built successfully!"
else
    print_error "Frontend build failed!"
    exit 1
fi

# Firebase Deployment
print_status "Deploying frontend to Firebase..."
firebase login
firebase use --add

firebase deploy --only hosting

if [ $? -eq 0 ]; then
    print_success "Frontend deployed successfully!"
else
    print_error "Frontend deployment failed!"
    exit 1
fi

cd ..

# Database Setup
print_status "Database setup instructions:"
print_status "  1. Go to Supabase Dashboard: https://app.supabase.com"
print_status "  2. Create a new project"
print_status "  3. Run the SQL migrations in supabase/migrations/"
print_status "  4. Enable Google OAuth in Authentication > Providers"
print_status "  5. Copy your connection string and update Render environment variables"

print_success "Deployment completed!"
print_status ""
print_status "Next steps:"
print_status "  1. Configure Supabase database and authentication"
print_status "  2. Add Firebase service account key to Render"
print_status "  3. Set all environment variables in Render dashboard"
print_status "  4. Configure Firebase Cloud Messaging"
print_status "  5. Test the application end-to-end"
print_status ""
print_success "Happy deploying! 🎉"