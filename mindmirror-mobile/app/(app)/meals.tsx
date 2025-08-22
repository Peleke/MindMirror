import React, { useMemo, useState, useCallback } from 'react'
import { SafeAreaView, View, Text, FlatList, ActivityIndicator, Pressable, Modal, ScrollView, Dimensions } from 'react-native'
import { gql, useQuery } from '@apollo/client'
import { useAuth } from '@/features/auth/context/AuthContext'
import { AppBar } from '@/components/common/AppBar'
import CalendarPicker from 'react-native-calendar-picker'
import { useRouter } from 'expo-router'
import Svg, { Circle } from 'react-native-svg'

const LIST_MEALS = gql`
  query MealsByUser($userId: String!, $start: String!, $end: String!, $limit: Int) {
    mealsByUserAndDateRange(userId: $userId, startDate: $start, endDate: $end, limit: $limit) {
      id_
      name
      type
      date
      notes
      mealFoods {
        id_
        quantity
        servingUnit
        foodItem { id_ name calories protein carbohydrates fat }
      }
    }
  }
`

const TOTAL_WATER = gql`
  query TotalWater($userId: String!, $date: String!) {
    totalWaterConsumptionByUserAndDate(userId: $userId, dateStr: $date)
  }
`

export default function MealsScreen() {
  const { session } = useAuth()
  const userId = session?.user?.id || ''
  const router = useRouter()

  const [showArchive, setShowArchive] = useState(false)
  const [anchorDate, setAnchorDate] = useState<Date>(new Date())
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [showFabSheet, setShowFabSheet] = useState(false)

  const { startIso, endIso, dayIso } = useMemo(() => {
    const end = anchorDate
    const start = new Date(end)
    start.setDate(end.getDate() - (showArchive ? 180 : 14))
    const toIso = (d: Date) => d.toISOString().slice(0, 10)
    return { startIso: toIso(start), endIso: toIso(end), dayIso: toIso(end) }
  }, [anchorDate, showArchive])

  const mealsQuery = useQuery(LIST_MEALS, {
    skip: !userId,
    variables: { userId, start: startIso, end: endIso, limit: 50 },
    fetchPolicy: 'cache-and-network',
  })

  const waterQuery = useQuery(TOTAL_WATER, {
    skip: !userId,
    variables: { userId, date: dayIso },
    fetchPolicy: 'cache-and-network',
  })

  const onOpenCalendar = useCallback(() => setShowDatePicker(true), [])
  const onFabPress = useCallback(() => setShowFabSheet(true), [])

  const meals = mealsQuery.data?.mealsByUserAndDateRange ?? []

  const loading = mealsQuery.loading || waterQuery.loading
  const error = mealsQuery.error || waterQuery.error

  const screenWidth = Dimensions.get('window').width

  const totalCalories = useMemo(() => {
    return (meals || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.calories || 0), 0), 0)
  }, [meals])

  const totalProtein = useMemo(() => {
    return (meals || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.protein || 0), 0), 0)
  }, [meals])
  const totalCarbs = useMemo(() => {
    return (meals || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.carbohydrates || 0), 0), 0)
  }, [meals])
  const totalFat = useMemo(() => {
    return (meals || []).reduce((acc: number, m: any) => acc + (m.mealFoods || []).reduce((a: number, mf: any) => a + (mf.foodItem?.fat || 0), 0), 0)
  }, [meals])

  const dailyCalGoal = 2000
  const calProgress = Math.max(0, Math.min(1, totalCalories / dailyCalGoal))

  const totalWaterMl = waterQuery.data?.totalWaterConsumptionByUserAndDate ?? 0
  const waterOz = totalWaterMl / 29.5735
  const dailyWaterGoalOz = 64
  const waterProgress = Math.max(0, Math.min(1, waterOz / dailyWaterGoalOz))

  const Donut = ({ size = 120, stroke = 10, progress = 0, color = '#1d4ed8', track = '#e5e7eb' }: { size?: number, stroke?: number, progress?: number, color?: string, track?: string }) => {
    const radius = (size - stroke) / 2
    const circumference = 2 * Math.PI * radius
    const dash = circumference * progress
    return (
      <Svg width={size} height={size}>
        <Circle cx={size / 2} cy={size / 2} r={radius} stroke={track} strokeWidth={stroke} fill="none" />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={`${dash}, ${circumference}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </Svg>
    )
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <AppBar title="Meals" />

      {/* Controls row */}
      <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 12, marginTop: 8, marginBottom: 8 }}>
        <Pressable onPress={onOpenCalendar} style={{ paddingVertical: 6, paddingHorizontal: 12, borderRadius: 12, backgroundColor: '#eef2ff' }}>
          <Text style={{ fontWeight: '600' }}>Calendar</Text>
        </Pressable>
        <View style={{ flexDirection: 'row' }}>
          <Pressable onPress={() => setShowArchive(false)} style={{ paddingVertical: 6, paddingHorizontal: 12, borderRadius: 12, backgroundColor: showArchive ? '#eee' : '#cde4ff', marginRight: 8 }}>
            <Text style={{ fontWeight: '600' }}>Today</Text>
          </Pressable>
          <Pressable onPress={() => setShowArchive(true)} style={{ paddingVertical: 6, paddingHorizontal: 12, borderRadius: 12, backgroundColor: showArchive ? '#cde4ff' : '#eee' }}>
            <Text style={{ fontWeight: '600' }}>Archive</Text>
          </Pressable>
        </View>
      </View>

      {/* Top charts - simple pager */}
      <ScrollView horizontal pagingEnabled showsHorizontalScrollIndicator={false} style={{ maxHeight: 200 }}>
        {/* Calories donut */}
        <View style={{ width: screenWidth, padding: 16 }}>
          <View style={{ alignItems: 'center', justifyContent: 'center' }}>
            <Donut size={120} stroke={10} progress={calProgress} color="#1d4ed8" track="#e5e7eb" />
            <View style={{ position: 'absolute', alignItems: 'center' }}>
              <Text style={{ fontSize: 22, fontWeight: '700', color: '#1d4ed8' }}>{Math.round(totalCalories)}</Text>
              <Text style={{ color: '#666' }}>cal</Text>
            </View>
            <Text style={{ marginTop: 8, color: '#666' }}>out of {dailyCalGoal}</Text>
          </View>
        </View>
        {/* Macros summary with stacked bar */}
        <View style={{ width: screenWidth, padding: 16 }}>
          <View style={{ marginBottom: 10, alignItems: 'center' }}>
            <Text style={{ color: '#666' }}>Macronutrients</Text>
          </View>
          <View style={{ flexDirection: 'row', marginBottom: 8, justifyContent: 'space-evenly' }}>
            <Text style={{ color: '#16a34a', fontWeight: '700' }}>{Math.round(totalProtein)}g P</Text>
            <Text style={{ color: '#d97706', fontWeight: '700' }}>{Math.round(totalCarbs)}g C</Text>
            <Text style={{ color: '#2563eb', fontWeight: '700' }}>{Math.round(totalFat)}g F</Text>
          </View>
          <View style={{ height: 14, borderRadius: 7, backgroundColor: '#e5e7eb', overflow: 'hidden' }}>
            {(() => {
              const calsP = totalProtein * 4
              const calsC = totalCarbs * 4
              const calsF = totalFat * 9
              const total = Math.max(1, calsP + calsC + calsF)
              return (
                <View style={{ flexDirection: 'row', width: '100%', height: '100%' }}>
                  <View style={{ flex: calsP / total, backgroundColor: '#16a34a' }} />
                  <View style={{ flex: calsC / total, backgroundColor: '#d97706' }} />
                  <View style={{ flex: calsF / total, backgroundColor: '#2563eb' }} />
                </View>
              )
            })()}
          </View>
        </View>
        {/* Water donut */}
        <View style={{ width: screenWidth, padding: 16 }}>
          <View style={{ alignItems: 'center' }}>
            <Text style={{ color: '#666' }}>Water</Text>
            <Donut size={100} stroke={8} progress={waterProgress} color="#1d4ed8" track="#e5e7eb" />
            <View style={{ position: 'absolute', top: 58, alignItems: 'center' }}>
              <Text style={{ color: '#1d4ed8', fontWeight: '700' }}>{Math.round(waterOz)}</Text>
              <Text style={{ color: '#666' }}>oz</Text>
            </View>
            <Text style={{ marginTop: 8, color: '#666' }}>out of {dailyWaterGoalOz} oz</Text>
          </View>
        </View>
      </ScrollView>

      {/* Content */}
      <View style={{ flex: 1, paddingHorizontal: 12 }}>
        {loading && (
          <View style={{ paddingTop: 24 }}>
            <ActivityIndicator />
          </View>
        )}
        {error && !loading && (
          <View style={{ paddingTop: 24 }}>
            <Text style={{ color: '#c00' }}>Failed to load data. {String(error)}</Text>
          </View>
        )}

        {/* Meals list with card styling */}
        {!loading && !error && (
          <View style={{ marginTop: 12 }}>
            <Text style={{ fontSize: 16, fontWeight: '600', marginBottom: 8 }}>Meals</Text>
            {meals.length === 0 ? (
              <Text style={{ color: '#666' }}>No meals yet.</Text>
            ) : (
              <FlatList
                data={meals}
                keyExtractor={(item) => item.id_}
                renderItem={({ item }) => {
                  const kcal = Math.round((item.mealFoods || []).reduce((acc: number, mf: any) => acc + (mf.foodItem?.calories || 0), 0))
                  return (
                    <View style={{ marginBottom: 12, borderRadius: 12, borderWidth: 1, borderColor: '#e5e7eb', backgroundColor: '#fff', shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}>
                      <View style={{ padding: 12, borderBottomWidth: 1, borderBottomColor: '#f1f5f9', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text style={{ fontWeight: '700' }}>{item.name}</Text>
                        <View style={{ paddingVertical: 4, paddingHorizontal: 10, backgroundColor: '#eff6ff', borderRadius: 12 }}>
                          <Text style={{ color: '#1d4ed8', fontWeight: '600' }}>{kcal} cal</Text>
                        </View>
                      </View>
                      <View style={{ padding: 12 }}>
                        <Text style={{ color: '#666', marginBottom: 4 }}>{item.type} • {new Date(item.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
                        {item.notes ? <Text style={{ color: '#666', marginBottom: 6 }}>{item.notes}</Text> : null}
                        {(item.mealFoods?.length ?? 0) > 0 && (
                          <View style={{ marginTop: 4 }}>
                            {item.mealFoods.map((mf: any) => (
                              <Text key={mf.id_} style={{ color: '#444' }}>
                                {mf.quantity} {mf.servingUnit} — {mf.foodItem?.name}
                              </Text>
                            ))}
                          </View>
                        )}
                      </View>
                    </View>
                  )
                }}
              />
            )}
          </View>
        )}
      </View>

      {/* Date picker modal */}
      <Modal visible={showDatePicker} transparent animationType="fade" onRequestClose={() => setShowDatePicker(false)}>
        <Pressable style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'center', alignItems: 'center' }} onPress={() => setShowDatePicker(false)}>
          <View style={{ backgroundColor: '#fff', padding: 20, borderRadius: 12, width: '94%' }}>
            <Text style={{ fontWeight: '600', marginBottom: 12 }}>Pick a date</Text>
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
              <Pressable onPress={() => setShowDatePicker(false)} style={{ paddingVertical: 10, paddingHorizontal: 14, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
                <Text style={{ color: '#fff', fontWeight: '600' }}>Done</Text>
              </Pressable>
            </View>
          </View>
        </Pressable>
      </Modal>

      {/* FAB options modal */}
      <Modal visible={showFabSheet} transparent animationType="fade" onRequestClose={() => setShowFabSheet(false)}>
        <Pressable style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'flex-end' }} onPress={() => setShowFabSheet(false)}>
          <View style={{ backgroundColor: '#fff', padding: 16, borderTopLeftRadius: 12, borderTopRightRadius: 12 }}>
            <Pressable onPress={() => { setShowFabSheet(false); router.push('/meals/create') }} style={{ paddingVertical: 12 }}>
              <Text style={{ fontSize: 16, fontWeight: '600' }}>Create New Meal</Text>
            </Pressable>
            <View style={{ height: 8 }} />
            <Pressable onPress={() => setShowFabSheet(false)} style={{ paddingVertical: 12 }}>
              <Text style={{ fontSize: 16, color: '#666' }}>Cancel</Text>
            </Pressable>
          </View>
        </Pressable>
      </Modal>

      {/* FAB */}
      <Pressable onPress={onFabPress} style={{ position: 'absolute', right: 16, bottom: 24, width: 56, height: 56, borderRadius: 28, backgroundColor: '#1d4ed8', justifyContent: 'center', alignItems: 'center', elevation: 6, zIndex: 50, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } }}>
        <Text style={{ color: '#fff', fontSize: 28, marginTop: -2 }}>＋</Text>
      </Pressable>
    </SafeAreaView>
  )
} 