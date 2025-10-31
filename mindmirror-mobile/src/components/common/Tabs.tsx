import React from 'react'
import { HStack } from '@/components/ui/hstack'
import { VStack } from '@/components/ui/vstack'
import { Pressable } from '@/components/ui/pressable'
import { Text } from '@/components/ui/text'

export function Tabs({ children }: { children: React.ReactNode }) {
  return <VStack space="sm">{children}</VStack>
}

export function TabsBar({ children }: { children: React.ReactNode }) {
  return (
    <HStack className="w-full border-b border-border-200 dark:border-border-700" space="none">
      {children}
    </HStack>
  )
}

export function TabsTab({ active, onPress, children }: { active: boolean; onPress: () => void; children: React.ReactNode }) {
  return (
    <Pressable
      className={`flex-1 py-2 border-b-2 ${active ? 'border-primary-600' : 'border-transparent'}`}
      onPress={onPress}
    >
      <Text className={`text-center ${active ? 'text-typography-900 dark:text-white' : 'text-typography-700 dark:text-gray-300'}`}>
        {children}
      </Text>
    </Pressable>
  )
}

export function TabsContent({ hidden, children }: { hidden?: boolean; children: React.ReactNode }) {
  if (hidden) return null
  return <VStack className="pt-3" space="sm">{children}</VStack>
}


