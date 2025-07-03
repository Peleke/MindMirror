import { Drawer } from 'expo-router/drawer'
import { View, TouchableOpacity, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { colors, spacing } from '@/theme'
import { useRouter } from 'expo-router'
import { GestureHandlerRootView } from 'react-native-gesture-handler'

export default function AppLayout() {
  const router = useRouter()

  const handleChatPress = () => {
    router.push('/(app)/chat')
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <View style={styles.container}>
        <Drawer
          screenOptions={{
            headerShown: false,
            drawerActiveTintColor: colors.primary[600],
            drawerInactiveTintColor: colors.text.tertiary,
            drawerStyle: {
              backgroundColor: colors.background.primary,
            },
          }}
        >
          <Drawer.Screen
            name="journal"
            options={{
              drawerLabel: 'Journal',
              title: 'Journal',
            }}
          />
          <Drawer.Screen
            name="chat"
            options={{
              drawerLabel: 'Chat',
              title: 'Chat',
            }}
          />
          <Drawer.Screen
            name="profile"
            options={{
              drawerLabel: 'Profile',
              title: 'Profile',
            }}
          />
        </Drawer>

        {/* Floating Action Button */}
        <TouchableOpacity
          style={styles.fab}
          onPress={handleChatPress}
          activeOpacity={0.8}
        >
          <Ionicons name="chatbubble" size={24} color={colors.text.inverse} />
        </TouchableOpacity>
      </View>
    </GestureHandlerRootView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  fab: {
    position: 'absolute',
    bottom: 80, // Above the tab bar
    right: spacing.lg,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.primary[600],
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8, // Android shadow
    shadowColor: colors.primary[600],
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
}) 