import 'react-native-gesture-handler/jestSetup'

// Mock expo-constants
jest.mock('expo-constants', () => ({
  expoConfig: {
    extra: {
      gatewayUrl: 'http://localhost:4000/graphql',
      supabaseUrl: 'test-supabase-url',
      supabaseAnonKey: 'test-supabase-anon-key',
    },
  },
}))

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
)

// Mock react-native-reanimated
jest.mock('react-native-reanimated', () => {
  const Reanimated = require('react-native-reanimated/mock')
  Reanimated.default.call = () => {}
  return Reanimated
})

// Mock react-native-gesture-handler
jest.mock('react-native-gesture-handler', () => ({
  GestureHandlerRootView: ({ children }) => children,
  PanGestureHandler: ({ children }) => children,
  TapGestureHandler: ({ children }) => children,
  State: {},
  Directions: {},
  gestureHandlerRootHOC: (component) => component,
}))

// Mock @react-navigation/native
jest.mock('@react-navigation/native', () => ({
  NavigationContainer: ({ children }) => children,
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
  }),
  useRoute: () => ({
    params: {},
  }),
}))

// Mock @react-navigation/stack
jest.mock('@react-navigation/stack', () => ({
  createStackNavigator: () => ({
    Navigator: ({ children }) => children,
    Screen: ({ children }) => children,
  }),
}))

// Mock @react-navigation/bottom-tabs
jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }) => children,
    Screen: ({ children }) => children,
  }),
}))

// Mock react-native-safe-area-context
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaProvider: ({ children }) => children,
  SafeAreaView: ({ children }) => children,
  useSafeAreaInsets: () => ({ top: 0, right: 0, bottom: 0, left: 0 }),
}))

// Mock @apollo/client
jest.mock('@apollo/client', () => ({
  ApolloProvider: ({ children }) => children,
  ApolloClient: jest.fn(),
  InMemoryCache: jest.fn(),
  createHttpLink: jest.fn(),
  from: jest.fn(),
}))

// Mock @supabase/supabase-js
jest.mock('@supabase/supabase-js', () => ({
  createClient: jest.fn(() => ({
    auth: {
      getSession: jest.fn(() => Promise.resolve({ data: { session: null } })),
      onAuthStateChange: jest.fn(() => ({ data: { subscription: { unsubscribe: jest.fn() } } })),
    },
  })),
}))

// Mock UI components - simplified approach that works with Jest
jest.mock('@/components/ui/text', () => ({
  Text: 'Text',
}))

jest.mock('@/components/ui/box', () => ({
  Box: 'Box',
}))

jest.mock('@/components/ui/vstack', () => ({
  VStack: 'VStack',
}))

jest.mock('@/components/ui/hstack', () => ({
  HStack: 'HStack',
}))

jest.mock('@/components/ui/pressable', () => ({
  Pressable: 'Pressable',
}))

jest.mock('@/components/ui/icon', () => ({
  Icon: 'Icon',
}))

jest.mock('@/components/ui/button', () => ({
  Button: 'Button',
  ButtonText: 'ButtonText',
}))

jest.mock('@/components/ui/textarea', () => ({
  Textarea: 'Textarea',
  TextareaInput: 'TextareaInput',
}))

jest.mock('@/components/ui/input', () => ({
  Input: 'Input',
  InputField: 'InputField',
}))

jest.mock('@/components/ui/heading', () => ({
  Heading: 'Heading',
}))

jest.mock('@/components/ui/scroll-view', () => ({
  ScrollView: 'ScrollView',
}))

jest.mock('@/components/ui/safe-area-view', () => ({
  SafeAreaView: 'SafeAreaView',
}))

// Mock lucide-react-native
jest.mock('lucide-react-native', () => ({
  Heart: 'Heart',
  Lightbulb: 'Lightbulb',
  PenTool: 'PenTool',
  Sparkles: 'Sparkles',
  Send: 'Send',
  MessageCircle: 'MessageCircle',
  ChevronRightIcon: 'ChevronRightIcon',
  ChevronLeftIcon: 'ChevronLeftIcon',
  MenuIcon: 'MenuIcon',
  // Workout timer bar icons
  Clock: 'Clock',
  TrendingUp: 'TrendingUp',
  Dumbbell: 'Dumbbell',
  Play: 'Play',
  Pause: 'Pause',
}))

// Global test setup
global.console = {
  ...console,
  // Uncomment to ignore a specific log level
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  // error: jest.fn(),
} 