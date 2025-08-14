import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { AppBar } from '@/components/common/AppBar'
import DailyTasksList from '@/components/habits/DailyTasksList'

export default function TasksScreen() {
  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Today" />
        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
          <VStack className="p-6" space="md">
            <DailyTasksList />
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


