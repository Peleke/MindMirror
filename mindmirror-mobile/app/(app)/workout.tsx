import React, { useMemo, useState, useCallback } from 'react'
import { View, Text as RNText, ActivityIndicator, Pressable as RNPressable, Modal } from 'react-native'
import { useRouter } from 'expo-router'
import { Fab, FabLabel } from '@/components/ui/fab'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import CalendarPicker from 'react-native-calendar-picker'
import { useWorkouts } from '@/services/api/practices'

export default function WorkoutsScreen() {
  const router = useRouter()

  const [anchorDate, setAnchorDate] = useState<Date>(new Date())
  const [showDatePicker, setShowDatePicker] = useState(false)

  const toUtcDateStr = useCallback((d: Date) => {
    const yy = d.getUTCFullYear()
    const mm = String(d.getUTCMonth() + 1).padStart(2, '0')
    const dd = String(d.getUTCDate()).padStart(2, '0')
    return `${yy}-${mm}-${dd}`
  }, [])

  const dayIso = useMemo(() => toUtcDateStr(anchorDate), [anchorDate, toUtcDateStr])
  const { data, loading, error, refetch } = useWorkouts({ dates: [dayIso] })
  const workouts = data?.workouts || []

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Workouts" />

        <VStack className="px-6 py-3" space="md">
          {/* Controls */}
          <HStack className="items-center justify-between">
            <HStack className="space-x-2">
              <RNPressable onPress={() => setShowDatePicker(true)} style={{ paddingVertical: 6, paddingHorizontal: 12, borderRadius: 12, backgroundColor: '#eef2ff', borderWidth: 1, borderColor: '#c7d2fe' }}>
                <RNText style={{ fontWeight: '600' }}>Calendar</RNText>
              </RNPressable>
              <RNPressable onPress={() => { const d = new Date(); setAnchorDate(d); refetch({ dates: [toUtcDateStr(d)] }).catch(() => {}) }} style={{ paddingVertical: 6, paddingHorizontal: 12, borderRadius: 12, backgroundColor: '#e0f2fe', borderWidth: 1, borderColor: '#bae6fd' }}>
                <RNText style={{ fontWeight: '600' }}>Today</RNText>
              </RNPressable>
            </HStack>
          </HStack>

          {/* Stats panel placeholder (for future D3 charts) */}
          <Box className="rounded-xl border border-border-200 bg-white dark:bg-background-0 p-4">
            <Text className="font-semibold text-typography-900 dark:text-white">Training Stats</Text>
            <Text className="text-typography-600 dark:text-gray-300">Charts coming soon</Text>
            <Box className="mt-3 h-24 rounded-md bg-background-100 border border-border-200" />
          </Box>

          {/* Workouts list */}
          {loading ? (
            <ActivityIndicator />
          ) : error ? (
            <Text className="text-red-600 dark:text-red-400">Failed to load workouts</Text>
          ) : workouts.length === 0 ? (
            <Text className="text-typography-600 dark:text-gray-300">No workouts for this day.</Text>
          ) : (
            <VStack space="sm">
              {workouts.map((w: any) => {
                const completed = !!(w.completedAt || w.completed_at)
                return (
                  <RNPressable key={w.id_} onPress={() => router.push(`/(app)/workout/${w.id_}`)}>
                    <Box className={`p-4 rounded-xl border ${completed ? 'border-green-200 bg-green-50' : 'border-border-200 bg-background-50'}`}>
                      <HStack className="items-center justify-between">
                        <Text className={`font-semibold ${completed ? 'text-green-700' : 'text-typography-900 dark:text-white'}`}>{w.title || 'Workout'}</Text>
                        <Text className="text-typography-600 dark:text-gray-300">{w.date}</Text>
                      </HStack>
                    </Box>
                  </RNPressable>
                )
              })}
            </VStack>
          )}
        </VStack>

        <RNPressable onPress={() => router.push('/(app)/workout-create')} style={{ position: 'absolute', right: 16, bottom: 24, width: 56, height: 56, borderRadius: 28, backgroundColor: '#1d4ed8', justifyContent: 'center', alignItems: 'center', elevation: 6, zIndex: 50, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } }}>
          <RNText style={{ color: '#fff', fontSize: 28, marginTop: -2 }}>＋</RNText>
        </RNPressable>
      </VStack>

      {/* Date picker modal */}
      <Modal visible={showDatePicker} transparent animationType="fade" onRequestClose={() => setShowDatePicker(false)}>
        <RNPressable style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'center', alignItems: 'center' }} onPress={() => setShowDatePicker(false)}>
          <View style={{ backgroundColor: '#fff', padding: 20, borderRadius: 12, width: '94%' }}>
            <RNText style={{ fontWeight: '600', marginBottom: 12 }}>Pick a date</RNText>
            <CalendarPicker
              selectedStartDate={anchorDate}
              onDateChange={(d: Date) => setAnchorDate(new Date(d))}
              startFromMonday={true}
              todayBackgroundColor="#f2e6ff"
              selectedDayColor="#1d4ed8"
              selectedDayTextColor="#ffffff"
              headerWrapperStyle={{ paddingHorizontal: 16 }}
              monthYearHeaderWrapperStyle={{ paddingHorizontal: 16 }}
              dayLabelsWrapper={{ paddingHorizontal: 16 }}
              previousTitle={'‹'}
              nextTitle={'›'}
            />
            <View style={{ alignItems: 'flex-end', marginTop: 12 }}>
              <RNPressable onPress={() => { setShowDatePicker(false); refetch({ dates: [toUtcDateStr(anchorDate)] }).catch(() => {}) }} style={{ paddingVertical: 10, paddingHorizontal: 14, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
                <RNText style={{ color: '#fff', fontWeight: '600' }}>Done</RNText>
              </RNPressable>
            </View>
          </View>
        </RNPressable>
      </Modal>
    </SafeAreaView>
  )
} 