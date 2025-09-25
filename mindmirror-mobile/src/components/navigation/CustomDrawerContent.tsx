import React, { useState } from 'react'
import { View, Modal } from 'react-native'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { DrawerContentScrollView, DrawerItem, DrawerContentComponentProps } from '@react-navigation/drawer'
import { useAuth } from '@/features/auth/context/AuthContext'
import { useUserById, useMyPendingCoachingRequests } from '@/services/api/users'
import { Icon } from '@/components/ui/icon'
import { ChevronDownIcon, ChevronRightIcon, InboxIcon } from 'lucide-react-native'
import { HStack } from '@/components/ui/hstack'
import { Text } from '@/components/ui/text'
import { Box } from '@/components/ui/box'
import { Pressable } from '@/components/ui/pressable'
import InboxDrawer from '@/components/inbox/InboxDrawer'
import { isCoachInPractices } from '@/constants/roles'
import { ThemeVariants, useThemeVariant } from '@/theme/ThemeContext'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

function ThemeSelectModal({ visible, onClose }: { visible: boolean; onClose: () => void }) {
  const { themeId, setThemeId } = useThemeVariant()
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable className="flex-1 bg-black/40 justify-end" onPress={onClose}>
        <Box className="bg-background-0 p-4 border-t border-border-200">
          <Text className="text-base font-semibold mb-2">Select Theme</Text>
          <Box className="pb-2">
            {ThemeVariants.map((t) => (
              <Pressable key={t.id} onPress={() => { setThemeId(t.id); onClose(); }} className={`px-3 py-3 rounded-md mb-2 border ${themeId === t.id ? 'bg-primary-50 border-primary-200' : 'bg-background-50 border-border-200'}`}>
                <Text className="text-typography-900">{t.label}</Text>
              </Pressable>
            ))}
          </Box>
        </Box>
      </Pressable>
    </Modal>
  )
}

export default function CustomDrawerContent(props: DrawerContentComponentProps) {
  const { navigation } = props
  const { user } = useAuth()
  const [showInbox, setShowInbox] = useState(false)
  const [expandedPrograms, setExpandedPrograms] = useState(false)
  const [showThemeModal, setShowThemeModal] = useState(false)
  const { themeId } = useThemeVariant()
  const insets = useSafeAreaInsets()
  
  // Get user details to check for coach role
  const { data: userData } = useUserById(user?.id || '')
  const { data: inboxData } = useMyPendingCoachingRequests()
  
  const isCoach = isCoachInPractices(userData?.userById?.roles || [])
  
  const pendingRequestsCount = inboxData?.myPendingCoachingRequests?.length || 0

  const handleProgramsPress = () => {
    // Toggle the expanded state
    setExpandedPrograms(!expandedPrograms)
  }

  return (
    <View style={{ flex: 1, paddingTop: insets.top }}>
      <DrawerContentScrollView {...props} contentContainerStyle={{ flex: 1, paddingTop: 0 }}>
        <View style={{ flexGrow: 1 }}>
          {/* Main Navigation */}
          <DrawerItem label="Home" onPress={() => {
            navigation.navigate('journal')
            navigation.closeDrawer()
          }} />
          
          {/* Programs & Resources with Sub-items */}
          <Pressable onPress={handleProgramsPress}>
            <HStack className="items-center justify-between px-4 py-3">
              <Text className="text-base font-medium text-typography-700">Programs & Resources</Text>
              <Icon 
                as={expandedPrograms ? ChevronDownIcon : ChevronRightIcon} 
                size="sm" 
                className="text-typography-500" 
              />
            </HStack>
          </Pressable>
          
          {expandedPrograms && (
            <View className="ml-4 border-l border-border-200 pl-2">
              <DrawerItem 
                label="  Overview" 
                onPress={() => {
                  navigation.navigate('programs')
                  navigation.closeDrawer()
                }} 
                labelStyle={{ fontSize: 14, color: '#6B7280' }}
              />
              <DrawerItem 
                label="  Workouts" 
                onPress={() => {
                  navigation.navigate('workout')
                  navigation.closeDrawer()
                }} 
                labelStyle={{ fontSize: 14, color: '#6B7280' }}
              />
              <DrawerItem 
                label="  Meals" 
                onPress={() => {
                  navigation.navigate('meals')
                  navigation.closeDrawer()
                }} 
                labelStyle={{ fontSize: 14, color: '#6B7280' }}
              />
            </View>
          )}
          
          {/* Inbox with notification badge */}
          <Pressable onPress={() => setShowInbox(true)}>
            <HStack className="items-center justify-between px-4 py-3">
              <HStack className="items-center" space="sm">
                <Icon as={InboxIcon} size="sm" className="text-typography-700" />
                <Text className="text-base font-medium text-typography-700">Inbox</Text>
              </HStack>
              {pendingRequestsCount > 0 && (
                <Box className="bg-red-500 rounded-full w-5 h-5 items-center justify-center">
                  <Text className="text-white text-xs font-bold">
                    {pendingRequestsCount > 9 ? '9+' : pendingRequestsCount}
                  </Text>
                </Box>
              )}
            </HStack>
          </Pressable>
          
          <DrawerItem label="Journal Archive" onPress={() => {
            navigation.navigate('archive')
            navigation.closeDrawer()
          }} />
          <DrawerItem label="Journal Hub" onPress={() => {
            navigation.navigate('journal-hub')
            navigation.closeDrawer()
          }} />
          {/* <DrawerItem label="Chat" onPress={() => {
            navigation.navigate('chat')
            navigation.closeDrawer()
          }} /> */}
          <DrawerItem label="Marketplace" onPress={() => {
            navigation.navigate('marketplace')
            navigation.closeDrawer()
          }} />
          {/* <DrawerItem label="Insights" onPress={() => {
            navigation.navigate('insights')
            navigation.closeDrawer()
          }} /> */}
        </View>
        
        <View style={{ paddingBottom: Math.max(20, insets.bottom) }}>
          {/* Coach-only Clients section */}
          <DrawerItem label="Profile" onPress={() => {
            navigation.navigate('profile')
            navigation.closeDrawer()
          }} />
          {isCoach && (
            <DrawerItem label="Clients" onPress={() => {
              navigation.navigate('clients')
              navigation.closeDrawer()
            }} />
          )}
          <DrawerItem label={`Theme (${themeId})`} onPress={() => setShowThemeModal(true)} />
        </View>
      </DrawerContentScrollView>
      
      {/* Inbox Drawer */}
      <InboxDrawer isOpen={showInbox} onClose={() => setShowInbox(false)} />
      <ThemeSelectModal visible={showThemeModal} onClose={() => setShowThemeModal(false)} />
    </View>
  )
}


