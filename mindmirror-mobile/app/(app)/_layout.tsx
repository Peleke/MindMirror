import { Drawer } from 'expo-router/drawer'
import { View, StyleSheet } from 'react-native'
import { colors } from '@/theme'
import { GestureHandlerRootView } from 'react-native-gesture-handler'

export default function AppLayout() {
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
              drawerLabel: 'Home',
              title: 'Home',
            }}
          />
          <Drawer.Screen
            name="journal-hub"
            options={{
              drawerLabel: 'Journal Hub',
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
            name="archive"
            options={{
              drawerLabel: 'Archive',
              title: 'Archive',
            }}
          />
          <Drawer.Screen
            name="insights"
            options={{
              drawerLabel: 'Insights',
              title: 'Insights',
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
      </View>
    </GestureHandlerRootView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
}) 