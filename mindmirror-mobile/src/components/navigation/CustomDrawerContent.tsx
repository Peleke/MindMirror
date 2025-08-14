import React from 'react'
import { View } from 'react-native'
import { DrawerContentScrollView, DrawerItem } from '@react-navigation/drawer'

type Props = React.ComponentProps<typeof DrawerContentScrollView>

export default function CustomDrawerContent(props: Props) {
  const { navigation } = props as any

  return (
    <DrawerContentScrollView {...props} contentContainerStyle={{ flex: 1, paddingTop: 0 }}>
      <View style={{ flexGrow: 1 }}>
        <DrawerItem label="Home" onPress={() => navigation.navigate('journal')} />
        <DrawerItem label="Journal Hub" onPress={() => navigation.navigate('journal-hub')} />
        <DrawerItem label="Chat" onPress={() => navigation.navigate('chat')} />
        <DrawerItem label="Archive" onPress={() => navigation.navigate('archive')} />
        <DrawerItem label="Insights" onPress={() => navigation.navigate('insights')} />
        <DrawerItem label="Marketplace" onPress={() => navigation.navigate('marketplace')} />
      </View>
      <View style={{ borderTopWidth: 1, borderColor: '#e5e7eb' }} />
      <View>
        <DrawerItem label="Profile" onPress={() => navigation.navigate('profile')} />
      </View>
    </DrawerContentScrollView>
  )
}


