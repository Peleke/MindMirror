# MindMirror Mobile App

A React Native mobile application for personal reflection, journaling, and AI-powered insights. Built with TypeScript, functional programming principles, and modern React Native architecture.

## 🚀 Features

- **Authentication**: Secure login/signup with Supabase
- **Dashboard**: AI-generated affirmations and insights
- **Journaling**: Multiple journal types (gratitude, reflection, freeform)
- **AI Chat**: Intelligent conversation with your personal AI assistant
- **Profile Management**: User settings and preferences
- **Modern UI/UX**: Beautiful, accessible interface with animations

## 🏗️ Architecture

- **Domain-Driven Design**: Feature-based folder structure
- **Functional Programming**: Using fp-ts for error handling and data flow
- **TypeScript**: Full type safety throughout the application
- **GraphQL**: Apollo Client for efficient data fetching
- **State Management**: React hooks and context for state management
- **Testing**: Jest and React Native Testing Library

## 📱 Tech Stack

- **React Native** with Expo
- **TypeScript** for type safety
- **Apollo Client** for GraphQL
- **Supabase** for authentication and backend
- **React Navigation** for routing
- **fp-ts** for functional programming utilities
- **React Native Reanimated** for animations
- **Jest** for testing

## 🛠️ Setup

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Expo CLI
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mindmirror-mobile
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Setup**
   ```bash
   cp env.example .env
   ```
   
   Update `.env` with your configuration:
   ```env
   EXPO_PUBLIC_SUPABASE_URL=your-supabase-url
   EXPO_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   EXPO_PUBLIC_GATEWAY_URL=http://localhost:4000/graphql
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

5. **Run on device/simulator**
   ```bash
   # iOS
   npm run ios
   
   # Android
   npm run android
   ```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Base components (Button, Input, Card, etc.)
│   ├── dashboard/      # Dashboard-specific components
│   ├── forms/          # Form components
│   ├── journal/        # Journal-specific components
│   └── navigation/     # Navigation components
├── features/           # Feature modules
│   ├── auth/          # Authentication feature
│   ├── chat/          # Chat feature
│   ├── dashboard/     # Dashboard feature
│   ├── journal/       # Journal feature
│   └── profile/       # Profile feature
├── hooks/             # Custom React hooks
├── navigation/        # Navigation configuration
├── services/          # API and external services
│   ├── api/          # GraphQL client and queries
│   ├── storage/      # Local storage utilities
│   └── supabase/     # Supabase client
├── theme/            # Design system (colors, typography, spacing)
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
    ├── date/         # Date utilities
    ├── fp/           # Functional programming utilities
    ├── string/       # String utilities
    └── validation/   # Validation utilities
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Test Structure
- Unit tests for utilities and hooks
- Component tests with React Native Testing Library
- Integration tests for API calls
- E2E tests for critical user flows

## 📦 Building

### Development Build
```bash
npx expo run:ios
npx expo run:android
```

### Production Build
```bash
# iOS
eas build --platform ios

# Android
eas build --platform android
```

## 🔧 Development

### Code Style
- ESLint for code linting
- Prettier for code formatting
- TypeScript strict mode enabled
- Functional programming principles

### Git Workflow
1. Create feature branch from `main`
2. Make changes with proper TypeScript types
3. Add tests for new functionality
4. Run linting and tests
5. Submit pull request

### Common Commands
```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check

# Start development server
npm start
```

## 🚀 Deployment

### EAS Build
```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Login to Expo
eas login

# Configure build
eas build:configure

# Build for production
eas build --platform all
```

### App Store Deployment
```bash
# Submit to App Store
eas submit --platform ios

# Submit to Google Play
eas submit --platform android
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review existing issues and discussions

## 🔮 Roadmap

- [ ] Offline support
- [ ] Push notifications
- [ ] Advanced analytics
- [ ] Social features
- [ ] Export functionality
- [ ] Dark mode
- [ ] Accessibility improvements
