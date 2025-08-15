import React, { useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { AppBar } from '@/components/common/AppBar'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { Tabs, TabsBar, TabsTab, TabsContent } from '@/components/common/Tabs'
import { useQuery, gql } from '@apollo/client'

const STEP_QUERY = gql`
  query StepById($programId: String!, $stepId: String!) {
    programTemplateSteps(programId: $programId) {
      id
      sequenceIndex
      durationDays
      habit { id title shortDescription }
    }
  }
`

export default function ProgramStepDetailScreen() {
  const params = useLocalSearchParams<{ slug: string; id: string }>()
  const router = useRouter()
  const programId = '' // resolve via parent if cached; left as placeholder
  const { data } = useQuery(STEP_QUERY, { variables: { programId, stepId: params.id }, skip: !programId })
  const step = (data?.programTemplateSteps || []).find((s: any) => String(s.id) === String(params.id))
  const [tab, setTab] = useState<'detail' | 'stats'>('detail')

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title={step ? `Step ${step.sequenceIndex + 1}` : 'Step'} showBackButton onBackPress={() => router.back()} />
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            <Tabs>
              <TabsBar>
                <TabsTab active={tab==='detail'} onPress={() => setTab('detail')}>Detail</TabsTab>
                <TabsTab active={tab==='stats'} onPress={() => setTab('stats')}>Stats</TabsTab>
              </TabsBar>
              <TabsContent hidden={tab!=='detail'}>
                <VStack space="sm">
                  <Text className="text-xl font-bold text-typography-900 dark:text-white">{step?.habit?.title || 'Habit'}</Text>
                  {step?.habit?.shortDescription ? (
                    <Text className="text-typography-600 dark:text-gray-300">{step.habit.shortDescription}</Text>
                  ) : null}
                  <Box className="h-px bg-border-200 dark:bg-border-700" />
                  <Text className="text-typography-700 dark:text-gray-300">Linked journal entries and lessons will appear here.</Text>
                </VStack>
              </TabsContent>
              <TabsContent hidden={tab!=='stats'}>
                <Text className="text-typography-700 dark:text-gray-300">Adherence, streaks, and counts will display here.</Text>
              </TabsContent>
            </Tabs>
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


