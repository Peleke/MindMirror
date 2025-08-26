import { Drawer } from 'expo-router/drawer'
import { View, StyleSheet } from 'react-native'
import { colors } from '@/theme'
import { GestureHandlerRootView } from 'react-native-gesture-handler'
import CustomDrawerContent from '@/components/navigation/CustomDrawerContent'

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
          drawerContent={(props) => <CustomDrawerContent {...props} />}
          // Ensure profile is last visually by declaring it last
        >
          <Drawer.Screen name="journal" options={{ drawerLabel: 'Home', title: 'Home' }} />
          <Drawer.Screen name="programs" options={{ drawerLabel: 'Programs & Resources', title: 'Programs & Resources' }} />
          <Drawer.Screen name="meals" options={{ drawerLabel: 'Meals', title: 'Meals' }} />
          <Drawer.Screen name="journal-hub" options={{ drawerLabel: 'Journal Hub', title: 'Journal' }} />
          <Drawer.Screen name="archive" options={{ drawerLabel: 'Journal Archive', title: 'Archive' }} />
          <Drawer.Screen name="chat" options={{ drawerLabel: 'Chat', title: 'Chat' }} />
          <Drawer.Screen name="marketplace" options={{ drawerLabel: 'Marketplace', title: 'Marketplace' }} />
          <Drawer.Screen
            name="insights"
            options={{
              drawerLabel: 'Insights',
              title: 'Insights',
            }}
          />
          <Drawer.Screen name="workouts" options={{ drawerLabel: 'Workouts', title: 'Workouts' }} />
          <Drawer.Screen name="profile" options={{ drawerLabel: 'Profile', title: 'Profile' }} />
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