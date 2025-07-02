import { NavigatorScreenParams } from '@react-navigation/native'

// Auth Stack
export type AuthStackParamList = {
  Login: undefined
  Signup: undefined
  ForgotPassword: undefined
}

// Main App Stack
export type MainStackParamList = {
  Dashboard: undefined
  Journal: NavigatorScreenParams<JournalTabParamList>
  Chat: undefined
  Profile: undefined
}

// Journal Tabs
export type JournalTabParamList = {
  Recent: undefined
  Archive: undefined
  Review: undefined
}

// Dashboard Stack
export type DashboardStackParamList = {
  DashboardHome: undefined
  GratitudeForm: undefined
  ReflectionForm: undefined
  FreeformForm: undefined
}

// Root Navigator
export type RootStackParamList = {
  Auth: NavigatorScreenParams<AuthStackParamList>
  Main: NavigatorScreenParams<MainStackParamList>
}

// Navigation props
export type AuthScreenProps<T extends keyof AuthStackParamList> = {
  navigation: any
  route: { params: AuthStackParamList[T] }
}

export type MainScreenProps<T extends keyof MainStackParamList> = {
  navigation: any
  route: { params: MainStackParamList[T] }
}

export type JournalScreenProps<T extends keyof JournalTabParamList> = {
  navigation: any
  route: { params: JournalTabParamList[T] }
} 