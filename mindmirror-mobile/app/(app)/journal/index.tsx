import { Box } from "@/components/ui/box";
import { HStack } from "@/components/ui/hstack";
import { Icon } from "@/components/ui/icon";
import { Pressable } from "@/components/ui/pressable";
import { SafeAreaView } from "@/components/ui/safe-area-view";
import { ScrollView } from "@/components/ui/scroll-view";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { useRouter } from 'expo-router';
import { Heart, Lightbulb } from "lucide-react-native";
import { useState } from 'react';
import { ActivityIndicator } from 'react-native';
import { UserGreeting } from '../../../src/components/journal/UserGreeting';
import { AffirmationDisplay } from '../../../src/components/journal/AffirmationDisplay';
import { useQuery, gql } from '@apollo/client'
import { HABIT_STATS, GET_TODAYS_TASKS } from '@/services/api/habits'
import Svg, { Circle as SvgCircle, G } from 'react-native-svg'
import { JournalEntryForm } from '../../../src/components/journal/JournalEntryForm';
import { TransitionOverlay } from '../../../src/components/journal/TransitionOverlay';
import { useJournalFlow } from '../../../src/hooks/useJournalFlow';
import { useToast } from '@/components/ui/toast';
import { Toast, ToastDescription, ToastTitle } from '@/components/ui/toast';
import { useAuth } from '@/features/auth/context/AuthContext';
import { useAffirmation } from '@/hooks/useAffirmation';
import { useJournalStatus } from '@/hooks/useJournalStatus';
import { CompletedJournalCard } from '@/components/journal/CompletedJournalCard';
import { AppBar } from '@/components/common/AppBar';
import DailyTasksList from '@/components/habits/DailyTasksList'
import { useLocalSearchParams } from 'expo-router'
import { getUserDisplayName } from '@/utils/user';

function todayIsoDate(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`
}

function MiniDashboard() {
  const onDate = todayIsoDate()
  const MINI_TASKS = gql`
    query MiniTodaysTasks($onDate: Date!) {
      todaysTasks(onDate: $onDate) {
        __typename
        ... on HabitTask {
          taskId
          habitTemplateId
          title
          status
        }
      }
    }
  `
  const { data: tasks, loading: tasksLoading } = useQuery(MINI_TASKS, { variables: { onDate }, fetchPolicy: 'cache-and-network' })
  const firstHabit = (tasks?.todaysTasks || []).find((t: any) => t.__typename === 'HabitTask' && t.habitTemplateId)
  const habitId = firstHabit?.habitTemplateId || (global as any).__preferredHabitId || ''
  const habitTitle = firstHabit?.title || ''
  const { data: stats, loading: statsLoading } = useQuery(HABIT_STATS, { variables: { habitTemplateId: habitId, lookbackDays: 21 }, skip: !habitId })

  // Debug logs
  // eslint-disable-next-line no-console
  console.log('[MiniDashboard] tasks loaded?', !tasksLoading, 'habitTask found?', !!firstHabit, 'habitId', habitId, 'title', habitTitle)
  // eslint-disable-next-line no-console
  console.log('[MiniDashboard] stats loading?', statsLoading, 'stats', stats?.habitStats)
  if (habitId) { (global as any).__preferredHabitId = habitId }

  const adherence = Math.max(0, Math.min(1, stats?.habitStats?.adherenceRate || 0))
  const streak = stats?.habitStats?.currentStreak || 0
  const presented = stats?.habitStats?.presentedCount ?? 0
  const completed = stats?.habitStats?.completedCount ?? 0
  const size = 110
  const stroke = 10
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const progress = circumference * (1 - adherence)

  if ((tasksLoading && !habitId) || (habitId && statsLoading)) {
    return (
      <VStack className="mt-2 items-center">
        <ActivityIndicator />
      </VStack>
    )
  }

  if (!habitId) {
    return null
  }

  return (
    <VStack className="mt-2 px-4">
      <Box className="p-4 rounded-2xl bg-background-50 dark:bg-background-100 border border-border-200 dark:border-border-700 shadow">
      <HStack className="items-end justify-between">
        {/* Left: adherence ring + counts + header */}
        <VStack className="items-center" style={{ width: '33%' }}>
          <Box className="items-center justify-center">
            <Svg width={size} height={size}>
              <G rotation="-90" origin={`${size/2}, ${size/2}`}>
                <SvgCircle cx={size/2} cy={size/2} r={radius} stroke="#e5e7eb" strokeWidth={stroke} fill="transparent" />
                <SvgCircle
                  cx={size/2}
                  cy={size/2}
                  r={radius}
                  stroke="#10b981"
                  strokeWidth={stroke}
                  strokeDasharray={`${circumference} ${circumference}`}
                  strokeDashoffset={progress}
                  strokeLinecap="round"
                  fill="transparent"
                />
              </G>
            </Svg>
            <VStack className="absolute items-center">
              <Text className="text-lg font-bold text-typography-900 dark:text-white">{Math.round(adherence * 100)}%</Text>
            </VStack>
          </Box>
          <Text className="text-typography-600 dark:text-gray-300 mt-1">{completed}/{presented}</Text>
          <Text className="text-sm font-semibold text-typography-900 dark:text-white text-center" numberOfLines={1}>{habitTitle || 'Adherence'}</Text>
        </VStack>
        {/* Middle: today's changes */}
        <VStack className="items-center" style={{ width: '33%' }}>
          <TodayChips onDate={onDate} tasks={tasks?.todaysTasks || []} />
          <Text className="text-sm font-semibold text-typography-900 dark:text-white text-center">Today's wins</Text>
        </VStack>
        {/* Right: current streak */}
        <VStack className="items-center justify-end" style={{ width: '33%' }}>
          <Text className="text-2xl font-bold text-typography-900 dark:text-white">{streak}</Text>
          <Text className="text-sm font-semibold text-typography-900 dark:text-white text-center">Current streak</Text>
        </VStack>
      </HStack>
      </Box>
    </VStack>
  )
}

function TodayChips({ onDate, tasks }: { onDate: string; tasks: any[] }) {
  const completedHabit = tasks.find((t: any) => t.__typename === 'HabitTask' && t.status === 'completed')
  const completedLesson = tasks.find((t: any) => t.__typename === 'LessonTask' && t.status === 'completed')
  const chips: string[] = []
  if (completedHabit) chips.push('Habit ✓')
  if (completedLesson) chips.push('Lesson ✓')
  if (chips.length === 0) return <Text className="text-typography-600 dark:text-gray-300 italic">Keep going</Text>
  return (
    <VStack className="space-y-1 mt-0.5 items-stretch w-full px-4">
      {chips.map((c) => (
        <Box key={c} className="px-3 py-1 rounded-md bg-indigo-50 dark:bg-gray-800 border border-indigo-300 dark:border-gray-600 shadow-sm">
          <Text className="text-xs font-semibold text-indigo-900 dark:text-gray-100 text-center">{c}</Text>
        </Box>
      ))}
    </VStack>
  )
}

const LoadingJournalCard = ({ type }: { type: 'Gratitude' | 'Reflection' }) => {
  const isGratitude = type === 'Gratitude';
  const bgColor = isGratitude ? 'bg-blue-50 dark:bg-blue-950' : 'bg-indigo-50 dark:bg-indigo-950';
  const borderColor = isGratitude ? 'border-blue-200 dark:border-blue-800' : 'border-indigo-200 dark:border-indigo-800';
  const textColor = isGratitude ? 'text-blue-900 dark:text-blue-100' : 'text-indigo-900 dark:text-indigo-100';
  const spinnerColor = isGratitude ? '#2563eb' : '#4f46e5';
  
  return (
    <Box className={`flex-1 p-4 ${bgColor} rounded-lg border ${borderColor} items-center`}>
      <ActivityIndicator 
        size="small" 
        color={spinnerColor} 
        style={{ marginBottom: 8 }}
      />
      <Text className={`text-sm font-medium ${textColor} text-center`}>
        Loading {type}...
      </Text>
    </Box>
  );
};

export default function JournalScreen() {
  const params = useLocalSearchParams<{ reload?: string }>()
  const router = useRouter();
  const { show } = useToast();
  const { user } = useAuth();
  const { affirmation, isLoading: isAffirmationLoading } = useAffirmation();
  const { hasCompletedGratitude, hasCompletedReflection, isLoading: isStatusLoading } = useJournalStatus();
  
  const {
    submitEntry,
    isTransitioning: hookIsTransitioning,
    isSubmitting,
    error,
  } = useJournalFlow();

  const handleSaveAndChat = async (entry: string) => {
    // Call submitEntry with the 'andChat' flag
    await submitEntry(entry, { andChat: true });
  };

  const handleSave = async (entry: string) => {
    // Call submitEntry without the 'andChat' flag
    const { success } = await submitEntry(entry, { andChat: false });
    if (success) {
      // Use the 'show' function with the correct component structure for the toast.
      show({
        placement: "top",
        render: ({ id }) => {
          const toastId = "toast-" + id;
          return (
            <Toast nativeID={toastId} action="success" variant="solid">
              <VStack space="xs">
                <ToastTitle>Entry Saved</ToastTitle>
                <ToastDescription>
                  Your journal entry has been saved successfully.
                </ToastDescription>
              </VStack>
            </Toast>
          );
        },
      });
      // Here you might want to clear the form, which would require
      // lifting the form's state up to this screen component.
      // For now, we'll leave it as is.
    }
  };

  const handleGratitudePress = () => {
    router.push('/journal/gratitude');
  };

  const handleReflectionPress = () => {
    router.push('/journal/reflection');
  };

  const userName = getUserDisplayName(user);

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Journal" />
        
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto">
          {/* Header Section */}
          <VStack className="px-6 py-6" space="md">
            <UserGreeting 
              userName={userName} 
              className="text-2xl font-semibold text-typography-900 dark:text-white"
              hideSubtext
            />
            
            {/* Mini dashboard: current habit stats */}
            <MiniDashboard />
            <AffirmationDisplay 
              affirmation={isAffirmationLoading ? "Loading..." : affirmation}
            />
          </VStack>

          {/* Structured Journal Options */}
          <VStack className="px-6 pb-6" space="md">
            <HStack className="space-x-4">
              {isStatusLoading ? (
                <LoadingJournalCard type="Gratitude" />
              ) : hasCompletedGratitude ? (
                <CompletedJournalCard journalType="Gratitude" />
              ) : (
                <Pressable
                  onPress={handleGratitudePress}
                  className="flex-1"
                >
                  <Box className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800 items-center">
                    <Icon 
                      as={Heart}
                      size="lg"
                      className="text-blue-600 dark:text-blue-400 mb-2"
                    />
                    <Text className="text-sm font-medium text-blue-900 dark:text-blue-100 text-center">
                      Morning Gratitude
                    </Text>
                  </Box>
                </Pressable>
              )}
              
              {isStatusLoading ? (
                <LoadingJournalCard type="Reflection" />
              ) : hasCompletedReflection ? (
                <CompletedJournalCard journalType="Reflection" />
              ) : (
                <Pressable
                  onPress={handleReflectionPress}
                  className="flex-1"
                >
                  <Box className="p-4 bg-indigo-50 dark:bg-indigo-950 rounded-lg border border-indigo-200 dark:border-indigo-800 items-center">
                    <Icon 
                      as={Lightbulb}
                      size="lg"
                      className="text-indigo-600 dark:text-indigo-400 mb-2"
                    />
                    <Text className="text-sm font-medium text-indigo-900 dark:text-indigo-100 text-center">
                      Evening Reflection
                    </Text>
                  </Box>
                </Pressable>
              )}
            </HStack>
          </VStack>
          
          {/* Divider */}
          <Box className="h-px bg-border-200 dark:bg-border-700 mx-6" />

          {/* Today's Tasks */}
          <VStack className="px-6 py-6" space="md">
            <DailyTasksList forceNetwork={params?.reload === '1'} />
          </VStack>
          </VStack>
          
          {/* REMOVED: Old structured journal section */}
          
        </ScrollView>
        
        {/* Transition Overlay */}
        <TransitionOverlay 
          isVisible={hookIsTransitioning}
          // Add the required onComplete prop back with an empty function.
          onComplete={() => {}}
          className="absolute inset-0"
        />
      </VStack>
    </SafeAreaView>
  );
} 