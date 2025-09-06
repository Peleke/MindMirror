import { Box } from "@/components/ui/box";
import { HStack } from "@/components/ui/hstack";
import { Icon } from "@/components/ui/icon";
import { Pressable } from "@/components/ui/pressable";
import { SafeAreaView } from "@/components/ui/safe-area-view";
import { ScrollView } from "@/components/ui/scroll-view";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { useRouter } from 'expo-router';
import { Heart, Lightbulb, Dumbbell } from "lucide-react-native";
import { useState } from 'react';
import { ActivityIndicator, Modal, Pressable as RNPressable, TextInput, Animated, Easing } from 'react-native';
import { UserGreeting } from '../../../src/components/journal/UserGreeting';
import { AffirmationDisplay } from '../../../src/components/journal/AffirmationDisplay';
import { useQuery, gql } from '@apollo/client'
import { HABIT_STATS, GET_TODAYS_TASKS } from '@/services/api/habits'
import Svg, { Circle as SvgCircle, G } from 'react-native-svg'
import { useQuery as useQuery2 } from '@apollo/client'
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
import { View } from 'react-native';
import { useMutation } from '@apollo/client';
import React from 'react';
import { useTodaysSchedulables } from '@/services/api/users'
import dayjs from 'dayjs'
import { useTodaysWorkouts } from '@/services/api/practices'
import { useDeletePracticeInstance } from '@/services/api/practices'
import { useMyUpcomingPractices, useDeferPractice } from '@/services/api/practices'
import { Swipeable } from 'react-native-gesture-handler'
import CalendarPicker from 'react-native-calendar-picker'
import { Text as RNText } from 'react-native'
import GlobalFab from '@/components/common/GlobalFab';
import { useThemeVariant } from '@/theme/ThemeContext';
import { useFocusEffect } from '@react-navigation/native';

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function MiniDashboard() {
  const { session, loading: authLoading } = useAuth()
  const { themeId } = useThemeVariant()
  const isClassic = themeId === 'classic'
  const hasSession = !!session?.access_token
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
  const { data: tasks, loading: tasksLoading, refetch: refetchMini } = useQuery(MINI_TASKS, { variables: { onDate }, fetchPolicy: 'cache-and-network', skip: authLoading || !hasSession })
  const firstHabit = (tasks?.todaysTasks || []).find((t: any) => t.__typename === 'HabitTask' && t.habitTemplateId)
  const habitId = firstHabit?.habitTemplateId || (global as any).__preferredHabitId || ''
  const habitTitle = firstHabit?.title || ''
  const { data: stats, loading: statsLoading, refetch: refetchStats } = useQuery(HABIT_STATS, { variables: { habitTemplateId: habitId, lookbackDays: 21 }, skip: authLoading || !hasSession || !habitId })

  // Meals mini-row queries
  const userId = session?.user?.id || ''
  const MEALS_QUERY = gql`
    query MealsMini($userId: String!, $start: String!, $end: String!, $limit: Int) {
      mealsByUserAndDateRange(userId: $userId, startDate: $start, endDate: $end, limit: $limit) {
        id_
        mealFoods { foodItem { calories protein carbohydrates fat } }
      }
    }
  `
  const WATER_QUERY = gql`
    query WaterMini($userId: String!, $date: String!) {
      totalWaterConsumptionByUserAndDate(userId: $userId, dateStr: $date)
    }
  `
  const mealsMini = useQuery2(MEALS_QUERY, { variables: { userId, start: onDate, end: onDate, limit: 50 }, skip: authLoading || !hasSession || !userId })
  const waterMini = useQuery2(WATER_QUERY, { variables: { userId, date: onDate }, skip: authLoading || !hasSession || !userId })

  // User goals
  const USER_GOALS = gql`
    query UserGoals($userId: String!) {
      userGoals(userId: $userId) {
        dailyCalorieGoal
        dailyWaterGoal
        dailyProteinGoal
        dailyCarbsGoal
        dailyFatGoal
      }
    }
  `
  const goalsQ = useQuery2(USER_GOALS, { variables: { userId }, skip: authLoading || !hasSession || !userId })

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

  // Ensure hooks order is stable: declare state before any conditional return
  const [chartsTab, setChartsTab] = useState<'habits' | 'meals' | 'all'>('all')

  if ((tasksLoading && !habitId) || (habitId && statsLoading)) {
    return (
      <VStack className="mt-2 items-center">
        <ActivityIndicator />
      </VStack>
    )
  }

  // Show zeroed dashboard even if no habitId selected yet

  // Meals aggregates
  const totalCalories = (mealsMini.data?.mealsByUserAndDateRange || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.calories || 0), 0), 0)
  const totalProtein = (mealsMini.data?.mealsByUserAndDateRange || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.protein || 0), 0), 0)
  const totalCarbs = (mealsMini.data?.mealsByUserAndDateRange || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.carbohydrates || 0), 0), 0)
  const totalFat = (mealsMini.data?.mealsByUserAndDateRange || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.fat || 0), 0), 0)
  const goalCal = goalsQ.data?.userGoals?.dailyCalorieGoal ?? 2000
  const dailyCalGoal = goalCal
  const calProgress = Math.max(0, Math.min(1, totalCalories / dailyCalGoal))
  // Macro goals (grams): use user goals if present; else default split: P=30%, C=50%, F=20% of calories
  const userP = goalsQ.data?.userGoals?.dailyProteinGoal
  const userC = goalsQ.data?.userGoals?.dailyCarbsGoal
  const userF = goalsQ.data?.userGoals?.dailyFatGoal
  const defaultProteinG = Math.round((dailyCalGoal * 0.30) / 4)
  const defaultCarbsG = Math.round((dailyCalGoal * 0.50) / 4)
  const defaultFatG = Math.round((dailyCalGoal * 0.20) / 9)
  const goalProteinG = Math.max(1, userP ?? defaultProteinG)
  const goalCarbsG = Math.max(1, userC ?? defaultCarbsG)
  const goalFatG = Math.max(1, userF ?? defaultFatG)
  const proteinProgress = Math.max(0, Math.min(1, totalProtein / goalProteinG))
  const carbsProgress = Math.max(0, Math.min(1, totalCarbs / goalCarbsG))
  const fatProgress = Math.max(0, Math.min(1, totalFat / goalFatG))
  const totalWaterMl = waterMini.data?.totalWaterConsumptionByUserAndDate || 0
  const waterOz = totalWaterMl / 29.5735
  const goalWaterMl = goalsQ.data?.userGoals?.dailyWaterGoal ?? 2000
  const dailyWaterGoalOz = goalWaterMl / 29.5735
  const waterProgress = Math.max(0, Math.min(1, waterOz / dailyWaterGoalOz))

  // Macro stacked bar helper
  const MacroStackBar = ({ p, c, f }: { p: number; c: number; f: number }) => {
    const sumRaw = p + c + f
    const hasData = sumRaw > 0
    const sum = Math.max(1, sumRaw)
    const pct = (x: number) => Math.round((x / sum) * 100)
    return (
      <VStack className="w-full items-center">
        {/* Percent labels */}
        <HStack className="w-11/12 items-center mb-0.5">
          <Box style={{ flex: hasData ? p / sum : 1/3, alignItems: 'center' }}>
            <Text className="text-2xs" style={{ color: '#16a34a', fontWeight: '700' }}>{hasData ? `${pct(p)}%` : '0%'}</Text>
          </Box>
          <Box style={{ flex: hasData ? c / sum : 1/3, alignItems: 'center' }}>
            <Text className="text-2xs" style={{ color: '#d97706', fontWeight: '700' }}>{hasData ? `${pct(c)}%` : '0%'}</Text>
          </Box>
          <Box style={{ flex: hasData ? f / sum : 1/3, alignItems: 'center' }}>
            <Text className="text-2xs" style={{ color: '#2563eb', fontWeight: '700' }}>{hasData ? `${pct(f)}%` : '0%'}</Text>
          </Box>
        </HStack>
        {/* Bar */}
        <HStack className="w-11/12 items-center" style={{ height: 10, borderRadius: 6, overflow: 'hidden' }}>
          {hasData ? (
            <>
              <Box style={{ flex: p / sum, backgroundColor: '#16a34a', height: '100%' }} />
              <Box style={{ flex: c / sum, backgroundColor: '#d97706', height: '100%' }} />
              <Box style={{ flex: f / sum, backgroundColor: '#2563eb', height: '100%' }} />
            </>
          ) : (
            <Box style={{ flex: 1, backgroundColor: '#e5e7eb', height: '100%' }} />
          )}
        </HStack>
        {/* Letters centered under segments by giving same flex distribution */}
        <HStack className="w-11/12 items-center mt-1">
          <Box style={{ flex: hasData ? p / sum : 1/3, alignItems: 'center' }}>
            <Text className="text-2xs" style={{ color: '#16a34a', fontWeight: '700' }}>P</Text>
          </Box>
          <Box style={{ flex: hasData ? c / sum : 1/3, alignItems: 'center' }}>
            <Text className="text-2xs" style={{ color: '#d97706', fontWeight: '700' }}>C</Text>
          </Box>
          <Box style={{ flex: hasData ? f / sum : 1/3, alignItems: 'center' }}>
            <Text className="text-2xs" style={{ color: '#2563eb', fontWeight: '700' }}>F</Text>
          </Box>
        </HStack>
      </VStack>
    )
  }

  const Donut = ({ size = 68, stroke = 8, progress = 0, color = '#1d4ed8', track = '#e5e7eb' }: { size?: number, stroke?: number, progress?: number, color?: string, track?: string }) => {
    const radius = (size - stroke) / 2
    const circumference = 2 * Math.PI * radius
    const dash = circumference * progress
    return (
      <Svg width={size} height={size}>
        <G rotation="-90" origin={`${size/2}, ${size/2}`}>
          <SvgCircle cx={size/2} cy={size/2} r={radius} stroke={track} strokeWidth={stroke} fill="transparent" />
          <SvgCircle cx={size/2} cy={size/2} r={radius} stroke={color} strokeWidth={stroke} strokeDasharray={`${dash} ${circumference}`} strokeLinecap="round" fill="transparent" />
        </G>
      </Svg>
    )
  }

  const AnimatedCircle = Animated.createAnimatedComponent(SvgCircle)
  const MacroDonut = ({ size = 44, stroke = 6, progress = 0, color = '#16a34a', track = '#e5e7eb', delay = 0 }: { size?: number, stroke?: number, progress?: number, color?: string, track?: string, delay?: number }) => {
    const radius = (size - stroke) / 2
    const circumference = 2 * Math.PI * radius
    const anim = React.useRef(new Animated.Value(0)).current
    React.useEffect(() => {
      anim.setValue(0)
      Animated.timing(anim, { toValue: Math.max(0, Math.min(1, progress)), duration: 700, delay, easing: Easing.out(Easing.quad), useNativeDriver: false }).start()
    }, [progress, delay])
    const dashoffset = Animated.multiply(circumference, Animated.subtract(1, anim))
    return (
      <Svg width={size} height={size}>
        <G rotation="-90" origin={`${size/2}, ${size/2}`}>
          <SvgCircle cx={size/2} cy={size/2} r={radius} stroke={track} strokeWidth={stroke} fill="transparent" />
          <AnimatedCircle
            cx={size/2}
            cy={size/2}
            r={radius}
            stroke={color}
            strokeWidth={stroke}
            strokeDasharray={`${circumference} ${circumference}`}
            strokeDashoffset={dashoffset as unknown as number}
            strokeLinecap="round"
            fill="transparent"
          />
        </G>
      </Svg>
    )
  }

  // Shrink visuals to match meals mini-row height
  const smallSize = 68
  const smallStroke = 8
  const smallRadius = (smallSize - smallStroke) / 2
  const smallCircumference = 2 * Math.PI * smallRadius
  const smallProgress = smallCircumference * (1 - adherence)

  // Expose a refresh function via global for quick hook-up
  ;(global as any).__refreshHomeMiniDashboard = async () => {
    try { await refetchMini(); } catch {}
    try { if (habitId) await refetchStats(); } catch {}
  }

  return (
    <VStack className="mt-2 px-4">
      <Box className={`p-3 rounded-2xl ${isClassic ? 'bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700' : 'bg-background-200 dark:bg-background-700 border border-border-300 dark:border-border-700'} shadow-brand`}>
        <HStack className="items-center">
          {/* Vertical H/M switcher */}
          <VStack className="mr-3 space-y-2">
            <Pressable onPress={() => setChartsTab('habits')} className={`w-8 h-8 rounded-md items-center justify-center border ${chartsTab==='habits' ? (isClassic ? 'bg-indigo-100 border-indigo-300' : 'bg-primary-200 border-primary-400') : 'bg-background-100 border-border-200'} ${chartsTab==='habits' ? 'dark:bg-background-700' : 'dark:bg-background-100'}`}>
              <Text className="text-xs font-semibold">H</Text>
            </Pressable>
            <Pressable onPress={() => setChartsTab('meals')} className={`w-8 h-8 rounded-md items-center justify-center border ${chartsTab==='meals' ? (isClassic ? 'bg-indigo-100 border-indigo-300' : 'bg-primary-200 border-primary-400') : 'bg-background-100 border-border-200'} ${chartsTab==='meals' ? 'dark:bg-background-700' : 'dark:bg-background-100'}`}>
              <Text className="text-xs font-semibold">M</Text>
            </Pressable>
            <Pressable onPress={() => setChartsTab('all')} className={`w-8 h-8 rounded-md items-center justify-center border ${chartsTab==='all' ? (isClassic ? 'bg-indigo-100 border-indigo-300' : 'bg-primary-200 border-primary-400') : 'bg-background-100 border-border-200'} ${chartsTab==='all' ? 'dark:bg-background-700' : 'dark:bg-background-100'}`}>
              <Text className="text-xs font-semibold">A</Text>
            </Pressable>
          </VStack>

          {/* Charts content */}
          {chartsTab === 'habits' ? (
          <Box className="flex-1">
          <HStack className="items-center justify-between">
            {/* Left: adherence ring + counts + header */}
            <VStack className="items-center" style={{ width: '33%' }}>
              <Box className="items-center justify-center">
                <Svg width={smallSize} height={smallSize}>
                  <G rotation="-90" origin={`${size/2}, ${size/2}`}>
                    <SvgCircle cx={smallSize/2} cy={smallSize/2} r={smallRadius} stroke="#e5e7eb" strokeWidth={smallStroke} fill="transparent" />
                    <SvgCircle
                      cx={smallSize/2}
                      cy={smallSize/2}
                      r={smallRadius}
                      stroke="#10b981"
                      strokeWidth={smallStroke}
                      strokeDasharray={`${smallCircumference} ${smallCircumference}`}
                      strokeDashoffset={smallProgress}
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
              <Text className="text-sm font-semibold text-typography-900 dark:text-white text-center" numberOfLines={1}>Adherence</Text>
            </VStack>
            {/* Middle: today's changes */}
            <VStack className="items-center justify-center" style={{ width: '33%' }}>
              <Box className="w-10/12 h-2 rounded-full bg-border-200" />
              <Text className="text-xs font-semibold text-typography-900 dark:text-white text-center mt-1">Today</Text>
            </VStack>
            {/* Right: current streak */}
            <VStack className="items-center justify-center" style={{ width: '33%' }}>
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">{streak}</Text>
              <Text className="text-sm font-semibold text-typography-900 dark:text-white text-center">Current streak</Text>
            </VStack>
          </HStack>
          </Box>
          ) : chartsTab === 'meals' ? (
          <Box className="flex-1">
        <HStack className="items-center justify-between">
          {/* Water */}
          <VStack className="items-center" style={{ width: '33%' }}>
            <Text className="text-xs font-semibold text-typography-700 dark:text-gray-200 mb-1">Water</Text>
            <MacroDonut size={60} stroke={7} progress={waterProgress} color="#06b6d4" track="#e5e7eb" delay={260} />
            <Text className="text-2xs text-typography-900 dark:text-white font-bold mt-1">{Math.round(waterOz)} oz</Text>
          </VStack>
          {/* Calories */}
          <VStack className="items-center" style={{ width: '33%' }}>
            <MacroDonut size={68} stroke={8} progress={calProgress} color="#1d4ed8" track="#e5e7eb" delay={200} />
            <Text className="text-sm font-bold text-typography-900 dark:text-white">{Math.round(totalCalories)}</Text>
            <Text className="text-2xs text-typography-600 dark:text-gray-300">/ {dailyCalGoal} kcal</Text>
          </VStack>
          {/* Macros */}
          <VStack className="items-center" style={{ width: '33%' }}>
            <Text className="text-xs font-semibold text-typography-700 dark:text-gray-200 mb-1">Macros</Text>
            <MacroStackBar p={totalProtein} c={totalCarbs} f={totalFat} />
          </VStack>
        </HStack>
          </Box>
          ) : (
          <Box className="flex-1">
        <HStack className="items-center justify-between">
          {/* All: Adherence left */}
          <VStack className="items-center justify-center" style={{ width: '33%' }}>
            <Text className="text-xs font-semibold text-typography-700 dark:text-gray-200 mb-1">Adherence</Text>
            <MacroDonut size={60} stroke={7} progress={adherence} color="#10b981" track="#e5e7eb" delay={0} />
            <Text className="text-2xs mt-1 font-semibold text-typography-900 dark:text-white">{Math.round(adherence * 100)}%</Text>
          </VStack>
          {/* All: Calories center */}
          <VStack className="items-center" style={{ width: '33%' }}>
            <MacroDonut size={68} stroke={8} progress={calProgress} color="#1d4ed8" track="#e5e7eb" delay={120} />
            <Text className="text-sm font-bold text-typography-900 dark:text-white">{Math.round(totalCalories)}</Text>
            <Text className="text-2xs text-typography-600 dark:text-gray-300">/ {dailyCalGoal} kcal</Text>
          </VStack>
          {/* All: Macros right */}
          <VStack className="items-center" style={{ width: '33%' }}>
            <Text className="text-xs font-semibold text-typography-700 dark:text-gray-200 mb-1">Macros</Text>
            <MacroStackBar p={totalProtein} c={totalCarbs} f={totalFat} />
          </VStack>
        </HStack>
          </Box>
          )}
        </HStack>
      </Box>
      {(() => {
        // Macro coach message (canned)
        const parts: { message: string, macro: string, deficit: number }[] = []
        const hasDeficit = (proteinProgress < 1) || (carbsProgress < 1) || (fatProgress < 1)
        
        if (proteinProgress >= 0.9) parts.push({ message: 'Protein on track!', macro: 'protein', deficit: goalProteinG - totalProtein })
        if (carbsProgress >= 0.9) parts.push({ message: 'Carbs on target!', macro: 'carbs', deficit: goalCarbsG - totalCarbs })
        if (fatProgress >= 0.9) parts.push({ message: 'Fats on pace!', macro: 'fats', deficit: goalFatG - totalFat })
        
        let msg = ''
        if (parts.length === 3) {
          msg = 'Fantastic job! You are hitting your macro targets for the day. Keep up the great work!'
        } else if (parts.length === 2) {
          const missingMacro = ['protein', 'carbs', 'fats'].find(macro => !parts.some(part => part.macro === macro))
          const a = parts[0]?.macro || 'protein'
          const b = parts[1]?.macro || (a === 'protein' ? 'carbs' : 'protein')
          if (missingMacro === 'protein') {
            const d = goalProteinG - totalProtein
            msg = `Great job with ${a} and ${b}! Just ${d}g of protein before everything is on target.`
          } else if (missingMacro === 'carbs') {
            const d = goalCarbsG - totalCarbs
            msg = `Great job with ${a} and ${b}! Just ${d}g of carbs before everything is on target.`
          } else if (missingMacro === 'fats') {
            const d = goalFatG - totalFat
            msg = `Great job with ${a} and ${b}! Just ${d}g of fats before everything is on target.`
          } else {
            msg = parts.map(part => part.message).join(' • ') + '. Keep it up.'
          }
        } else if (hasDeficit) {
          msg = "You're making steady progress! A balanced meal later will help you hit today's targets."
        } else if (parts.length > 0) {
          msg = parts.map(part => part.message).join(' • ') + '. Keep it up.'
        } else {
          msg = 'Nice start 🎉 Keep building toward your macro goals!'
        }
        
        return <AffirmationDisplay affirmation={msg} className="mt-2" />
      })()}
    </VStack>
  )
}

function TodaysWorkoutsRow({ showHeader = true }: { showHeader?: boolean }) {
  const { session } = useAuth()
  const router = useRouter()
  const hasSession = !!session?.access_token
  const onDate = dayjs().format('YYYY-MM-DD')
  const userId = session?.user?.id || ''
  const { data, loading } = useTodaysSchedulables({ userId, date: onDate }, !hasSession || !userId)
  const usersItems = (data?.schedulablesForUserOnDate || []).filter((s: any) => (s.service_id ?? 'practices') === 'practices')
  const { data: pData, loading: pLoading } = useTodaysWorkouts(onDate)
  const { data: upData } = useMyUpcomingPractices()
  const [deferPractice] = useDeferPractice()
  const todaysUpcoming = (upData?.my_upcoming_practices || []).filter((sp: any) => dayjs(sp.scheduled_date).format('YYYY-MM-DD') === onDate)
  // Map of today’s workouts by id for name/description enrichment
  const todaysMap: Record<string, any> = {}
  for (const w of (pData?.todaysWorkouts || [])) { todaysMap[w.id_] = w }
  const upcomingItems = todaysUpcoming.map((sp: any) => ({
    id_: sp.id_,
    name: (todaysMap[sp.practice_id]?.title || 'Workout'),
    description: todaysMap[sp.practice_id]?.description || '',
    date: onDate,
    service_id: 'practices',
    entity_id: sp.practice_id,
    practice_instance_id: sp.practice_instance_id,
    enrollment_id: sp.enrollment_id,
    __typename: 'Schedulable',
    completed: false,
    level: todaysMap[sp.practice_id]?.level || null,
  }))
  const practiceItems = (pData?.todaysWorkouts || []).map((w: any) => ({
    id_: w.id_,
    name: w.title || 'Workout',
    description: w.description || '',
    date: w.date,
    service_id: 'practices',
    entity_id: w.id_,
    completed: !!w.completedAt,
    __typename: 'Schedulable',
    level: w.level || null,
  }))
  const itemsMap: Record<string, any> = {}
  for (const it of [...usersItems, ...practiceItems, ...upcomingItems]) {
    const key = `${it.service_id}:${it.entity_id || it.id_}`
    itemsMap[key] = { ...(itemsMap[key] || {}), ...it }
  }
  const items = Object.values(itemsMap)
  const [localRemoved, setLocalRemoved] = React.useState<Record<string, boolean>>({})
  const [deletePractice] = useDeletePracticeInstance()
  if (!hasSession || !userId) return null
  return (
    <VStack className="mt-4" space="sm">
      {showHeader && (
        <HStack className="items-center justify-between">
          <Text className="text-lg font-semibold">Today’s Workouts</Text>
        </HStack>
      )}
      {loading && pLoading ? (
        <ActivityIndicator />
      ) : items.length === 0 ? (
        <Text className="text-typography-600">No workouts scheduled today</Text>
      ) : (
        <VStack space="xs">
          {items.filter((it: any) => !localRemoved[`${it.service_id}:${it.entity_id}`]).map((it: any) => {
            const key = `${it.service_id}:${it.entity_id}`
            const handleDelete = async () => {
              setLocalRemoved((prev) => ({ ...prev, [key]: true }))
              if ((it.service_id ?? 'practices') === 'practices') {
                try { await deletePractice({ variables: { id: it.entity_id } }) } catch { setLocalRemoved((prev) => ({ ...prev, [key]: false })) }
              }
            }
            const baseClasses = it.completed ? 'border-green-200 bg-green-50' : 'border-indigo-200 bg-indigo-50'
            return (
              <Swipeable
                key={key}
                renderRightActions={() => (
                  <HStack className="h-full items-center px-4 bg-red-600 rounded-lg">
                    <Text className="text-white font-semibold">Delete</Text>
                  </HStack>
                )}
                onSwipeableOpen={(dir) => { if (dir === 'right') handleDelete() }}
              >
                <HStack className={`items-center justify-between p-3 rounded-lg border ${baseClasses}`}>
                  <Pressable 
                    onPress={() => {
                      // For practice items: use practice instance ID directly
                      // For upcoming items: use practice_instance_id if available, otherwise entity_id (template ID)
                      const wid = it.practice_instance_id || it.id_
                      const eid = it.enrollment_id
                      router.push(eid ? `/(app)/workout/${wid}?enrollmentId=${eid}` : `/(app)/workout/${wid}`)
                    }}
                    className="flex-1"
                  >
                    <Box className="p-4 rounded-lg border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800 shadow">
                      <VStack space="sm">
                        <HStack space="sm" className="items-center">
                          <Icon as={Dumbbell} size="md" className="text-indigo-700 dark:text-indigo-300" />
                          <Text className="text-lg font-semibold text-typography-900 dark:text-white">{it.name || 'Workout'}</Text>
                          {!!it.level && (
                            <Box className="px-2 py-0.5 rounded-full bg-indigo-100 border border-indigo-200">
                              <Text className="text-xs text-indigo-700 font-semibold">{it.level}</Text>
                            </Box>
                          )}
                        </HStack>
                        {!!it.description && (
                          <Text className="text-typography-600 dark:text-gray-300">{it.description}</Text>
                        )}
                      </VStack>
                    </Box>
                  </Pressable>
                  {it.enrollment_id && (
                    <Pressable onPress={async () => { try { await deferPractice({ variables: { enrollmentId: it.enrollment_id, mode: 'push' } }) } catch {} }} className="ml-2 px-2 py-1 rounded border border-indigo-200 bg-white/60">
                      <Text className="text-xs text-indigo-700">Defer</Text>
                    </Pressable>
                  )}
                </HStack>
              </Swipeable>
            )
          })}
        </VStack>
      )}
    </VStack>
  )
}

function TodayChips({ onDate, tasks }: { onDate: string; tasks: any[] }) {
  const router = useRouter()
  const completedHabit = tasks.find((t: any) => t.__typename === 'HabitTask' && t.status === 'completed')
  const completedWorkout = tasks.find((t: any) => (t.__typename === 'Schedulable' && (t.service_id ?? 'practices') === 'practices' && t.completed))
  const chips: string[] = []
  if (completedHabit) chips.push('Habit ✓')
  if (completedWorkout) chips.push('Workout ✓')
  if ((tasks || []).length === 0) {
    return (
      <VStack className="space-y-2 items-center w-full px-4">
        <Text className="text-typography-600 dark:text-gray-300 italic">Keep going!</Text>
      </VStack>
    )
  }
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
  const { user, session, loading: authLoading } = useAuth();
  const { affirmation, isLoading: isAffirmationLoading } = useAffirmation();
  const { hasCompletedGratitude, hasCompletedReflection, isLoading: isStatusLoading } = useJournalStatus();
  // Tasks calendar state
  const [tasksAnchorDate, setTasksAnchorDate] = useState<Date>(new Date())
  const [showTasksDatePicker, setShowTasksDatePicker] = useState(false)
  const toUtcDateStr = (d: Date) => {
    const yy = d.getUTCFullYear()
    const mm = String(d.getUTCMonth() + 1).padStart(2, '0')
    const dd = String(d.getUTCDate()).padStart(2, '0')
    return `${yy}-${mm}-${dd}`
  }
  const tasksDayIso = toUtcDateStr(tasksAnchorDate)
  const tasksDisplayDate = dayjs(tasksAnchorDate).format('M/DD')
  const [homeTab, setHomeTab] = useState<'habits' | 'meals' | 'workouts'>('habits')
  const [showFab, setShowFab] = useState(false);
  const [showWaterModal, setShowWaterModal] = useState(false);
  const [waterAmount, setWaterAmount] = useState('');
  const [savingWater, setSavingWater] = useState(false);

  const CREATE_WATER = gql`
    mutation CreateWaterHome($input: WaterConsumptionCreateInput!) {
      createWaterConsumption(input: $input) { id_ }
    }
  `
  const [createWater] = useMutation(CREATE_WATER, {
    onCompleted: () => {
      setSavingWater(false);
      setShowWaterModal(false);
      show({
        placement: "top",
        render: ({ id }) => {
          const toastId = "toast-" + id;
          return (
            <Toast nativeID={toastId} action="success" variant="solid">
              <VStack space="xs">
                <ToastTitle>Water Saved</ToastTitle>
                <ToastDescription>
                  Your water consumption has been logged successfully.
                </ToastDescription>
              </VStack>
            </Toast>
          );
        },
      });
    },
    onError: (error) => {
      setSavingWater(false);
      show({
        placement: "top",
        render: ({ id }) => {
          const toastId = "toast-" + id;
          return (
            <Toast nativeID={toastId} action="error" variant="solid">
              <VStack space="xs">
                <ToastTitle>Error</ToastTitle>
                <ToastDescription>
                  Failed to log water: {error.message}
                </ToastDescription>
              </VStack>
            </Toast>
          );
        },
      });
    },
    update: (cache, { data }) => {
      if (data?.createWaterConsumption) {
        const newWaterConsumption = data.createWaterConsumption;
        cache.modify({
          fields: {
            totalWaterConsumptionByUserAndDate(existing) {
              return newWaterConsumption;
            },
          },
        });
      }
    },
  });

  // Move hooks above any conditional return to keep hook order stable
  const {
    submitEntry,
    isTransitioning: hookIsTransitioning,
    isSubmitting,
    error,
  } = useJournalFlow();

  // Today's meals (for Meals tab)
  const onDate = todayIsoDate()
  const userId = session?.user?.id || ''
  const MEALS_TODAY = gql`
    query MealsToday($userId: String!, $date: String!) {
      mealsByUserAndDateRange(userId: $userId, startDate: $date, endDate: $date, limit: 50) {
        id_
        name
        date
        notes
        mealFoods { id_ foodItem { calories } }
      }
    }
  `
  const { data: mealsData, loading: mealsLoading } = useQuery(MEALS_TODAY, { variables: { userId, date: onDate }, skip: !userId })
  const todaysMeals = mealsData?.mealsByUserAndDateRange || []

  // Now safe to early-return without changing hook order
  if (authLoading && !session) {
    return (
      <SafeAreaView className="h-full w-full">
        <VStack className="h-full w-full bg-background-0 items-center justify-center">
          <ActivityIndicator />
        </VStack>
      </SafeAreaView>
    )
  }

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

  // Focus-based refresh for dashboard charts
  useFocusEffect(React.useCallback(() => {
    const fn = (global as any).__refreshHomeMiniDashboard
    if (typeof fn === 'function') { fn() }
    return () => {}
  }, []))

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Home" />
        
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto">
          {/* Header Section */}
          <VStack className="px-6 py-6" space="md">
            <UserGreeting 
              userName={userName} 
              className="text-2xl font-semibold text-typography-900 dark:text-white"
              hideSubtext
            />
            
            {/* Mini dashboard: current habit stats + macro coach */}
            <MiniDashboard />
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
                  <Box className="p-4 bg-primary-50 dark:bg-background-800 rounded-lg border border-primary-200 dark:border-border-700 items-center">

                    <Text className="text-sm font-medium text-primary-900 dark:text-primary-100 text-center">
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
                  <Box className="p-4 bg-primary-50 dark:bg-background-800 rounded-lg border border-primary-200 dark:border-border-700 items-center">

                    <Text className="text-sm font-medium text-primary-900 dark:text-primary-100 text-center">
                      Evening Reflection
                    </Text>
                  </Box>
                </Pressable>
              )}
            </HStack>
          </VStack>
          
          {/* Divider */}
          <Box className="h-px bg-border-200 dark:bg-border-700 mx-6" />

          {/* Habits | Meals switcher */}
          <VStack className="px-6 py-4" space="md">
            <HStack className="items-center justify-between">
              <HStack className="items-center space-x-3">
                <Pressable onPress={() => setHomeTab('habits')} className={`px-3 py-2 rounded-md ${homeTab === 'habits' ? 'bg-primary-200 dark:bg-background-700 border-primary-400' : 'bg-background-100 dark:bg-background-100 border-border-200'} border`}>
                  <Text className="font-semibold">Habits</Text>
                </Pressable>
                <Pressable onPress={() => setHomeTab('meals')} className={`px-3 py-2 rounded-md ${homeTab === 'meals' ? 'bg-primary-200 dark:bg-background-700 border-primary-400' : 'bg-background-100 dark:bg-background-100 border-border-200'} border`}>
                  <Text className="font-semibold">Meals</Text>
                </Pressable>
              </HStack>
              <HStack className="items-center space-x-2">
                <Pressable onPress={() => { const prev = new Date(tasksAnchorDate); prev.setDate(prev.getDate() - 1); setTasksAnchorDate(prev) }} className="px-2 py-1 rounded-md border border-border-200">
                  <Text className="text-typography-900">‹</Text>
                </Pressable>
                <Pressable onPress={() => setShowTasksDatePicker(true)} className="px-3 py-1.5 rounded-md bg-background-50 border border-border-200">
                  <Text className="font-semibold">{tasksDisplayDate}</Text>
                </Pressable>
                <Pressable onPress={() => { const next = new Date(tasksAnchorDate); next.setDate(next.getDate() + 1); setTasksAnchorDate(next) }} className="px-2 py-1 rounded-md border border-border-200">
                  <Text className="text-typography-900">›</Text>
                </Pressable>
              </HStack>
            </HStack>
          </VStack>

          {/* Content: Habits or Meals */}
          {homeTab === 'habits' ? (
            <VStack className="px-6 py-2" space="md">
              <DailyTasksList forceNetwork={params?.reload === '1'} onDate={tasksDayIso} onAfterHabitResponse={() => { const fn = (global as any).__refreshHomeMiniDashboard; if (typeof fn === 'function') fn() }} />
            </VStack>
          ) : (
            <VStack className="px-6 py-2" space="md">
              {mealsLoading ? (
                <ActivityIndicator />
              ) : todaysMeals.length === 0 ? (
                <Text className="text-typography-600 dark:text-gray-300">No meals yet today.</Text>
              ) : (
                todaysMeals.map((m: any) => {
                  const kcal = Math.round((m.mealFoods || []).reduce((acc: number, mf: any) => acc + (mf.foodItem?.calories || 0), 0))
                  return (
                    <Pressable key={m.id_} onPress={() => router.push(`/meals/${m.id_}?from=/`)} className="mb-3">
                      <Box className="p-4 rounded-xl bg-background-0 border border-border-200 shadow-sm">
                        <HStack className="items-center justify-between">
                          <Text className="font-semibold text-typography-900 dark:text-white">{m.name}</Text>
                          <Box className="px-2 py-1 rounded-md" style={{ backgroundColor: '#eff6ff' }}>
                            <Text style={{ color: '#1d4ed8', fontWeight: '600' }}>{kcal} cal</Text>
                          </Box>
                        </HStack>
                        <Text className="text-typography-600 dark:text-gray-300 mt-1">{new Date(m.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
                        {m.notes ? <Text className="text-typography-600 dark:text-gray-300 mt-1">{m.notes}</Text> : null}
                      </Box>
                    </Pressable>
                  )
                })
              )}
            </VStack>
          )}
          
          {/* REMOVED: Old structured journal section */}
          
          </VStack>
        </ScrollView>
        
        {/* Transition Overlay */}
        <TransitionOverlay 
          isVisible={hookIsTransitioning}
          // Add the required onComplete prop back with an empty function.
          onComplete={() => {}}
          className="absolute inset-0"
        />
        {/* Global FAB */}
        <GlobalFab />
      </VStack>

    </SafeAreaView>
  );
} 