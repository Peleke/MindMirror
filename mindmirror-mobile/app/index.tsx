import { View, Text } from 'react-native'
import { LoadingScreen } from '@/components/common/Loading'
import { useAuthState } from '@/features/auth/hooks/useAuthState'

export default function Index() {
  const { loading } = useAuthState()

  console.log('Index render: loading =', loading)

  if (loading) {
    return <LoadingScreen text="Loading..." />
  }

  // Let useAuthState handle the navigation
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Redirecting...</Text>
    </View>
  )
} 