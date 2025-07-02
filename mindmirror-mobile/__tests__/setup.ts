import '@testing-library/jest-native/extend-expect'

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
)

// Mock expo-constants
jest.mock('expo-constants', () => ({
  expoConfig: {
    extra: {
      supabaseUrl: 'https://test.supabase.co',
      supabaseAnonKey: 'test-key',
    },
  },
}))

// Mock expo-device
jest.mock('expo-device', () => ({
  isDevice: true,
  brand: 'test',
  manufacturer: 'test',
  modelName: 'test',
  modelId: 'test',
  designName: 'test',
  productName: 'test',
  deviceYearClass: 2020,
  totalMemory: 4096,
  supportedCpuArchitectures: ['arm64'],
  osName: 'iOS',
  osVersion: '15.0',
  osBuildId: 'test',
  osInternalBuildId: 'test',
  deviceName: 'test',
  deviceType: 1,
}))

// Mock expo-haptics
jest.mock('expo-haptics', () => ({
  impactAsync: jest.fn(),
  notificationAsync: jest.fn(),
  selectionAsync: jest.fn(),
}))

// Mock react-native-reanimated
jest.mock('react-native-reanimated', () => {
  const Reanimated = require('react-native-reanimated/mock')
  Reanimated.default.call = () => {}
  return Reanimated
})

// Mock react-native-gesture-handler
jest.mock('react-native-gesture-handler', () => {
  const View = require('react-native/Libraries/Components/View/View')
  const Text = require('react-native/Libraries/Text/Text')
  const ScrollView = require('react-native/Libraries/Components/ScrollView/ScrollView')
  const TouchableOpacity = require('react-native/Libraries/Components/Touchable/TouchableOpacity')
  
  return {
    Swipeable: View,
    DrawerLayout: View,
    State: {},
    ScrollView,
    Slider: View,
    Switch: View,
    TextInput: require('react-native/Libraries/Components/TextInput/TextInput'),
    ToolbarAndroid: View,
    ViewPagerAndroid: View,
    DrawerLayoutAndroid: View,
    TouchableHighlight: TouchableOpacity,
    TouchableNativeFeedback: TouchableOpacity,
    TouchableOpacity,
    TouchableWithoutFeedback: TouchableOpacity,
    TouchableBounce: TouchableOpacity,
    Touchable: TouchableOpacity,
    FlatList: require('react-native/Libraries/Lists/FlatList'),
    gestureHandlerRootHOC: jest.fn((component) => component),
    Directions: {},
    State: {},
  }
})

// Global test utilities
global.console = {
  ...console,
  // Uncomment to ignore a specific log level
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  // error: jest.fn(),
} 