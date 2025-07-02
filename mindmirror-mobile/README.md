# MindMirror Mobile

A production-grade React Native application for mindful journaling and self-reflection, built with functional programming patterns and modern UI/UX practices.

## 🚀 Features

- **Authentication**: Secure login/signup with Supabase
- **Dashboard**: Personalized welcome with AI-generated affirmations
- **Journaling**: Multiple journal types (Gratitude, Reflection, Freeform)
- **Chat**: AI-powered conversation interface
- **Profile**: User settings and tradition selection
- **Modern UI**: Beautiful animations, micro-interactions, and responsive design

## 🏗️ Architecture

- **Functional Programming**: Built with fp-ts for type-safe functional programming
- **Domain-Driven Design**: Feature-based organization with clear separation of concerns
- **Type Safety**: Full TypeScript implementation with strict type checking
- **Modern Navigation**: React Navigation with drawer, stack, and tab navigation
- **State Management**: Apollo Client for server state, React Context for local state

## 📱 Tech Stack

- **React Native** with Expo
- **TypeScript** for type safety
- **fp-ts** for functional programming
- **Apollo Client** for GraphQL
- **Supabase** for authentication and backend
- **React Navigation** for routing
- **React Native Reanimated** for animations
- **Zod** for validation
- **React Hook Form** for form management

## 🛠️ Setup

### Prerequisites

- Node.js 18+ 
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

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your configuration:
   ```env
   EXPO_PUBLIC_SUPABASE_URL=your_supabase_url
   EXPO_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
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
│   ├── common/         # Base components (Button, Input, etc.)
│   ├── forms/          # Form components
│   ├── dashboard/      # Dashboard-specific components
│   ├── journal/        # Journal-specific components
│   └── navigation/     # Navigation components
├── features/           # Domain-driven features
│   ├── auth/          # Authentication feature
│   ├── dashboard/     # Dashboard feature
│   ├── journal/       # Journal feature
│   ├── chat/          # Chat feature
│   └── profile/       # Profile feature
├── navigation/         # Navigation configuration
├── hooks/             # Reusable hooks
├── services/          # API and external services
├── utils/             # Utility functions
│   └── fp/            # Functional programming utilities
├── theme/             # Design system
├── types/             # TypeScript types
└── assets/            # Static assets
```

## 🎨 Design System

The app uses a comprehensive design system with:

- **Color Palette**: Semantic colors with light/dark variants
- **Typography**: Platform-specific fonts with responsive sizing
- **Spacing**: Consistent spacing scale
- **Shadows**: Platform-optimized elevation system
- **Animations**: Smooth micro-interactions and transitions

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 📦 Building

### Development
```bash
npm start
```

### Production
```bash
# Build for iOS
expo build:ios

# Build for Android
expo build:android
```

## 🔧 Development

### Code Quality

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Type check
npm run type-check
```

### Functional Programming

The app uses fp-ts for functional programming patterns:

- **Option**: Safe handling of nullable values
- **Either**: Error handling and API responses
- **TaskEither**: Async operations with error handling

Example usage:
```typescript
import { pipe } from 'fp-ts/function'
import * as O from 'fp-ts/Option'
import * as TE from 'fp-ts/TaskEither'

// Safe navigation
const userName = pipe(
  user,
  O.fromNullable,
  O.chain(user => O.fromNullable(user.name)),
  O.getOrElse(() => 'Anonymous')
)

// API call with error handling
const fetchUser = pipe(
  TE.tryCatch(
    () => api.getUser(id),
    error => new Error(`Failed to fetch user: ${error}`)
  ),
  TE.map(user => user.name)
)
```

## 🚀 Deployment

### Expo Application Services (EAS)

1. **Install EAS CLI**
   ```bash
   npm install -g @expo/eas-cli
   ```

2. **Login to Expo**
   ```bash
   eas login
   ```

3. **Configure EAS**
   ```bash
   eas build:configure
   ```

4. **Build for production**
   ```bash
   eas build --platform all
   ```

5. **Submit to stores**
   ```bash
   eas submit --platform ios
   eas submit --platform android
   ```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions, please open an issue in the repository.
