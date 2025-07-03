import { View, Text } from 'react-native'
import { LoadingScreen } from '@/components/common/Loading'
import { useAuth } from '@/features/auth/context/AuthContext'

export default function Index() {
  const { loading } = useAuth()

  console.log('Index render: loading =', loading)

  if (loading) {
    return <LoadingScreen text="Loading..." />
  }

  // AuthStateHandler in root layout will handle navigation
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Redirecting...</Text>
    </View>
  )
} 