import React, { useMemo, useState, useCallback } from 'react'
import { SafeAreaView, View, Text, FlatList, ActivityIndicator, Pressable, Modal } from 'react-native'
import { gql, useQuery } from '@apollo/client'
import { useAuth } from '@/features/auth/context/AuthContext'
import { AppBar } from '@/components/common/AppBar'
import CalendarPicker from 'react-native-calendar-picker'

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

const LIST_FOOD_ITEMS = gql`
  query FoodItemsForUser($userId: String!, $search: String, $limit: Int) {
    foodItemsForUserWithPublic(userId: $userId, searchTerm: $search, limit: $limit) {
      id_
      name
      servingSize
      servingUnit
      calories
      protein
      carbohydrates
      fat
    }
  }
`

export default function MealsScreen() {
  const { session } = useAuth()
  const userId = session?.user?.id || ''

  const [showArchive, setShowArchive] = useState(false)
  const [anchorDate, setAnchorDate] = useState<Date>(new Date())
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [showFabSheet, setShowFabSheet] = useState(false)

  const { startIso, endIso } = useMemo(() => {
    const end = anchorDate
    const start = new Date(end)
    start.setDate(end.getDate() - (showArchive ? 180 : 14))
    const toIso = (d: Date) => d.toISOString().slice(0, 10)
    return { startIso: toIso(start), endIso: toIso(end) }
  }, [anchorDate, showArchive])

  const mealsQuery = useQuery(LIST_MEALS, {
    skip: !userId,
    variables: { userId, start: startIso, end: endIso, limit: 50 },
    fetchPolicy: 'cache-and-network',
  })

  const foodsQuery = useQuery(LIST_FOOD_ITEMS, {
    skip: !userId,
    variables: { userId, search: null, limit: 20 },
    fetchPolicy: 'cache-and-network',
  })

  const onOpenCalendar = useCallback(() => {
    setShowDatePicker(true)
  }, [])

  const onFabPress = useCallback(() => {
    setShowFabSheet(true)
  }, [])

  const meals = mealsQuery.data?.mealsByUserAndDateRange ?? []
  const foodItems = foodsQuery.data?.foodItemsForUserWithPublic ?? []

  const loading = mealsQuery.loading || foodsQuery.loading
  const error = mealsQuery.error || foodsQuery.error

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <AppBar title="Meals" />

      {/* Controls row: calendar + Today/Archive */}
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

      {/* Content */}
      <View style={{ flex: 1, paddingHorizontal: 12 }}>
        {loading && (
          <View style={{ paddingTop: 24 }}>
            <ActivityIndicator />
          </View>
        )}
        {error && !loading && (
          <View style={{ paddingTop: 24 }}>
            <Text style={{ color: '#c00' }}>Failed to load meals. {String(error)}</Text>
          </View>
        )}
        {!loading && !error && meals.length === 0 && (
          <View style={{ paddingTop: 48, alignItems: 'center' }}>
            <Text style={{ fontSize: 18, fontWeight: '600', marginBottom: 6 }}>No Meals Found</Text>
            <Text style={{ color: '#666' }}>Log your first meal to get started.</Text>
          </View>
        )}

        {/* Meals List */}
        {!loading && !error && meals.length > 0 && (
          <FlatList
            data={meals}
            keyExtractor={(item) => item.id_}
            renderItem={({ item }) => (
              <View style={{ paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#eee' }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <Text style={{ fontWeight: '600' }}>{item.name}</Text>
                  <Text style={{ color: '#555' }}>{Math.round((item.mealFoods || []).reduce((acc: number, mf: any) => acc + (mf.foodItem?.calories || 0), 0))} cal</Text>
                </View>
                <Text style={{ color: '#666' }}>{item.type} • {new Date(item.date).toLocaleString()}</Text>
                {item.notes ? <Text style={{ marginTop: 4 }}>{item.notes}</Text> : null}
                {(item.mealFoods?.length ?? 0) > 0 && (
                  <View style={{ marginTop: 6 }}>
                    {item.mealFoods.map((mf: any) => (
                      <Text key={mf.id_} style={{ color: '#444' }}>
                        {mf.quantity} {mf.servingUnit} — {mf.foodItem?.name}
                      </Text>
                    ))}
                  </View>
                )}
              </View>
            )}
          />
        )}

        {/* Food Items (short list) */}
        {!loading && !error && (
          <View style={{ marginTop: 16 }}>
            <Text style={{ fontSize: 16, fontWeight: '600', marginBottom: 8 }}>Food Items</Text>
            {foodItems.length === 0 ? (
              <Text style={{ color: '#666' }}>No food items yet.</Text>
            ) : (
              <FlatList
                data={foodItems}
                keyExtractor={(item) => item.id_}
                renderItem={({ item }) => (
                  <View style={{ paddingVertical: 6 }}>
                    <Text style={{ fontWeight: '500' }}>{item.name}</Text>
                    <Text style={{ color: '#666' }}>{item.servingSize}{item.servingUnit} • {Math.round(item.calories)} kcal</Text>
                  </View>
                )}
              />
            )}
          </View>
        )}
      </View>

      {/* Date picker modal (react-native-calendar-picker) */}
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
            <Pressable onPress={() => { setShowFabSheet(false); (global as any).expoRouter?.push?.('/(app)/meals/create') }} style={{ paddingVertical: 12 }}>
              <Text style={{ fontSize: 16, fontWeight: '600' }}>Create New Meal</Text>
            </Pressable>
            <View style={{ height: 8 }} />
            <Pressable onPress={() => setShowFabSheet(false)} style={{ paddingVertical: 12 }}>
              <Text style={{ fontSize: 16, color: '#666' }}>Cancel</Text>
            </Pressable>
          </View>
        </Pressable>
      </Modal>

      {/* Floating Action Button */}
      <Pressable onPress={onFabPress} style={{ position: 'absolute', right: 16, bottom: 24, width: 56, height: 56, borderRadius: 28, backgroundColor: '#1d4ed8', justifyContent: 'center', alignItems: 'center', elevation: 6, zIndex: 50, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } }}>
        <Text style={{ color: '#fff', fontSize: 28, marginTop: -2 }}>＋</Text>
      </Pressable>
    </SafeAreaView>
  )
} 