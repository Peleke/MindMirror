import React from 'react'
import { View } from 'react-native'
import { DrawerContentScrollView, DrawerItem } from '@react-navigation/drawer'

// Make children optional so this component can be used as a drawerContent renderer without explicit children
type Props = Omit<React.ComponentProps<typeof DrawerContentScrollView>, 'children'> & { children?: React.ReactNode }

export default function CustomDrawerContent(props: Props) {
  const { navigation } = props as any

  return (
    <DrawerContentScrollView {...props} contentContainerStyle={{ flex: 1, paddingTop: 0 }}>
      <View style={{ flexGrow: 1 }}>
        {/* Order: Home, Programs & Resources, Journal Archive, Journal Hub, Chat, Marketplace */}
        <DrawerItem label="Home" onPress={() => navigation.navigate('journal')} />
        <DrawerItem label="Programs & Resources" onPress={() => navigation.navigate('programs')} />
        <DrawerItem label="Journal Archive" onPress={() => navigation.navigate('archive')} />
        <DrawerItem label="Journal Hub" onPress={() => navigation.navigate('journal-hub')} />
        <DrawerItem label="Chat" onPress={() => navigation.navigate('chat')} />
        <DrawerItem label="Marketplace" onPress={() => navigation.navigate('marketplace')} />
        <DrawerItem label="Meals" onPress={() => navigation.navigate('meals')} />
        <DrawerItem label="Workouts" onPress={() => navigation.navigate('workout')} />
      </View>
      <View style={{ borderTopWidth: 1, borderColor: '#e5e7eb' }} />
      <View>
        <DrawerItem label="Profile" onPress={() => navigation.navigate('profile')} />
      </View>
    </DrawerContentScrollView>
  )
}


