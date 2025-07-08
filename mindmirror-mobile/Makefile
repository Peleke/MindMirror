# =============================================================================
# MindMirror Mobile - Development & Deployment Makefile
# =============================================================================

.PHONY: help local staging production clean install

# Default target
help:
	@echo "MindMirror Mobile Development & Deployment Commands"
	@echo "=================================================="
	@echo ""
	@echo "Environment Commands:"
	@echo "  make local      - Start with local environment"
	@echo "  make staging    - Start with staging environment"
	@echo "  make production - Start with production environment"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make start      - Start Expo development server"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	npm install

# Local Development
local:
	@echo "🚀 Starting MindMirror Mobile in LOCAL mode..."
	@echo "   - Supabase: Local/Development project"
	@echo "   - Gateway: http://localhost:4000/graphql"
	@echo "   - Debug: Enabled"
	@if [ -f env.local ]; then \
		echo "📋 Loading local environment..."; \
		cp env.local .env; \
	else \
		echo "❌ env.local not found. Please create it from env.example"; \
		exit 1; \
	fi
	@echo "🔧 Starting Expo development server..."
	npx expo start

# Staging Environment
staging:
	@echo "🚀 Starting MindMirror Mobile in STAGING mode..."
	@echo "   - Supabase: Live project"
	@echo "   - Gateway: Live staging URL"
	@echo "   - Debug: Disabled"
	@if [ -f env.staging ]; then \
		echo "📋 Loading staging environment..."; \
		cp env.staging .env; \
	else \
		echo "❌ env.staging not found. Please create it from env.example"; \
		exit 1; \
	fi
	@echo "🔧 Starting Expo development server..."
	npx expo start

# Production Environment
production:
	@echo "🚀 Starting MindMirror Mobile in PRODUCTION mode..."
	@echo "   - Supabase: Live production project"
	@echo "   - Gateway: Live production URL"
	@echo "   - Debug: Disabled"
	@if [ -f env.production ]; then \
		echo "📋 Loading production environment..."; \
		cp env.production .env; \
	else \
		echo "❌ env.production not found. Please create it from env.example"; \
		exit 1; \
	fi
	@echo "🔧 Starting Expo development server..."
	npx expo start

# Start Expo development server
start:
	@echo "🔧 Starting Expo development server..."
	npx expo start

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf node_modules
	rm -rf .expo
	rm -rf dist
	rm -f .env

# Build for production
build-android:
	@echo "🔨 Building Android APK..."
	npx expo build:android

build-ios:
	@echo "🔨 Building iOS app..."
	npx expo build:ios

# Environment setup
setup-local:
	@echo "🔧 Setting up local environment..."
	@if [ ! -f env.local ]; then \
		cp env.example env.local; \
		echo "✅ Created env.local from template"; \
		echo "📝 Please edit env.local with your local configuration"; \
	else \
		echo "✅ env.local already exists"; \
	fi

setup-staging:
	@echo "🔧 Setting up staging environment..."
	@if [ ! -f env.staging ]; then \
		cp env.example env.staging; \
		echo "✅ Created env.staging from template"; \
		echo "📝 Please edit env.staging with your staging configuration"; \
	else \
		echo "✅ env.staging already exists"; \
	fi

setup-production:
	@echo "🔧 Setting up production environment..."
	@if [ ! -f env.production ]; then \
		cp env.example env.production; \
		echo "✅ Created env.production from template"; \
		echo "📝 Please edit env.production with your production configuration"; \
	else \
		echo "✅ env.production already exists"; \
	fi

# Setup all environments
setup-all: setup-local setup-staging setup-production
	@echo "✅ All environment files created!"
	@echo "📝 Please edit each file with appropriate configuration" 