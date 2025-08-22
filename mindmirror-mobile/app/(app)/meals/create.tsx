import React, { useEffect, useMemo, useState } from 'react'
import { SafeAreaView, View, Text, TextInput, Pressable, Modal, FlatList, KeyboardAvoidingView, ScrollView, Platform } from 'react-native'
import { gql, useMutation, useLazyQuery } from '@apollo/client'
import { AppBar } from '@/components/common/AppBar'
import { useRouter } from 'expo-router'
import { useAuth } from '@/features/auth/context/AuthContext'

const CREATE_MEAL = gql`
  mutation CreateMeal($input: MealCreateInput!) {
    create_meal(input: $input) {
      id_
      name
      type
      date
      notes
    }
  }
`

const SEARCH_FOOD_ITEMS = gql`
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

const CREATE_FOOD_ITEM = gql`
  mutation CreateFoodItem($input: FoodItemCreateInput!) {
    create_food_item(input: $input) {
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

const mealTypes = ['BREAKFAST','LUNCH','DINNER','SNACK'] as const

type MealType = typeof mealTypes[number]

type SelectedFood = {
  foodItem: {
    id_: string
    name: string
    servingUnit: string
    servingSize?: number
    calories?: number
    protein?: number
    carbohydrates?: number
    fat?: number
  }
  quantity: number
  servingUnit: string
}

export default function CreateMealScreen() {
  const [name, setName] = useState('')
  const [notes, setNotes] = useState('')
  const [mealType, setMealType] = useState<MealType>('BREAKFAST')
  const [dt, setDt] = useState<Date>(new Date())
  const [selectedFoods, setSelectedFoods] = useState<SelectedFood[]>([])

  const [showFoodModal, setShowFoodModal] = useState(false)
  const [search, setSearch] = useState('')
  const [selectedForQuantity, setSelectedForQuantity] = useState<any | null>(null)
  const [quantity, setQuantity] = useState<string>('1')
  const [servingUnit, setServingUnit] = useState<string>('')
  const [creatingNew, setCreatingNew] = useState(false)
  const [newFood, setNewFood] = useState({
    name: '',
    serving_size: '',
    serving_unit: 'g',
    calories: '',
    protein: '',
    carbohydrates: '',
    fat: '',
    saturated_fat: '',
    monounsaturated_fat: '',
    polyunsaturated_fat: '',
    trans_fat: '',
    cholesterol: '',
    fiber: '',
    sugar: '',
    sodium: '',
    potassium: '',
    calcium: '',
    iron: '',
    vitamin_d: '',
    zinc: '',
    notes: '',
  })

  const router = useRouter()
  const { session } = useAuth()
  const userId = session?.user?.id || ''

  const [createMeal, { loading: creatingMeal }] = useMutation(CREATE_MEAL)
  const [createFoodItem, { loading: creatingFood }] = useMutation(CREATE_FOOD_ITEM)
  const [runSearch, { data: searchData, loading: searching }] = useLazyQuery(SEARCH_FOOD_ITEMS)

  useEffect(() => {
    const h = setTimeout(() => {
      if (showFoodModal) {
        runSearch({ variables: { userId, search, limit: 15 } })
      }
    }, 250)
    return () => clearTimeout(h)
  }, [search, showFoodModal, runSearch, userId])

  const searchResults = searchData?.foodItemsForUserWithPublic ?? []

  const input = useMemo(() => ({
    user_id: userId,
    name,
    type: mealType,
    date: dt.toISOString(),
    notes: notes || null,
    meal_foods_data: selectedFoods.map(sf => ({
      food_item_id: sf.foodItem.id_,
      quantity: sf.quantity,
      serving_unit: sf.servingUnit || sf.foodItem.servingUnit,
    })),
  }), [userId, name, mealType, dt, notes, selectedFoods])

  const canSubmit = name.trim().length > 0 && !!userId

  const onSubmit = async () => {
    if (!canSubmit) return
    try {
      await createMeal({ variables: { input } })
      router.back()
    } catch (e) {
      console.error('Create meal failed', e)
    }
  }

  const openQuantityFor = (item: any) => {
    setSelectedForQuantity(item)
    setQuantity('1')
    setServingUnit(item.servingUnit || 'g')
  }

  const addSelectedFood = () => {
    if (!selectedForQuantity) return
    const qty = parseFloat(quantity)
    if (!isFinite(qty) || qty <= 0) return
    const unit = (servingUnit || selectedForQuantity.servingUnit || 'g').trim()
    setSelectedFoods((prev) => [
      ...prev,
      { foodItem: selectedForQuantity, quantity: qty, servingUnit: unit },
    ])
    setSelectedForQuantity(null)
    setQuantity('1')
  }

  const removeSelectedFoodAt = (idx: number) => {
    setSelectedFoods(prev => prev.filter((_, i) => i !== idx))
  }

  const saveNewFoodItem = async () => {
    if (!userId) return
    const payload: any = {
      user_id: userId,
      name: newFood.name.trim(),
      serving_size: parseFloat(newFood.serving_size) || 0,
      serving_unit: newFood.serving_unit.trim() || 'g',
      calories: parseFloat(newFood.calories) || 0,
    }
    if (newFood.protein) payload.protein = parseFloat(newFood.protein)
    if (newFood.carbohydrates) payload.carbohydrates = parseFloat(newFood.carbohydrates)
    if (newFood.fat) payload.fat = parseFloat(newFood.fat)
    if (newFood.saturated_fat) payload.saturated_fat = parseFloat(newFood.saturated_fat)
    if (newFood.monounsaturated_fat) payload.monounsaturated_fat = parseFloat(newFood.monounsaturated_fat)
    if (newFood.polyunsaturated_fat) payload.polyunsaturated_fat = parseFloat(newFood.polyunsaturated_fat)
    if (newFood.trans_fat) payload.trans_fat = parseFloat(newFood.trans_fat)
    if (newFood.cholesterol) payload.cholesterol = parseFloat(newFood.cholesterol)
    if (newFood.fiber) payload.fiber = parseFloat(newFood.fiber)
    if (newFood.sugar) payload.sugar = parseFloat(newFood.sugar)
    if (newFood.sodium) payload.sodium = parseFloat(newFood.sodium)
    if (newFood.potassium) payload.potassium = parseFloat(newFood.potassium)
    if (newFood.calcium) payload.calcium = parseFloat(newFood.calcium)
    if (newFood.iron) payload.iron = parseFloat(newFood.iron)
    if (newFood.vitamin_d) payload.vitamin_d = parseFloat(newFood.vitamin_d)
    if (newFood.zinc) payload.zinc = parseFloat(newFood.zinc)
    if (newFood.notes?.trim()) payload.notes = newFood.notes.trim()

    try {
      const res = await createFoodItem({ variables: { input: payload } })
      const created = res.data?.create_food_item
      if (created) {
        // Pre-add with default quantity 1
        setSelectedFoods(prev => [...prev, { foodItem: created, quantity: 1, servingUnit: created.servingUnit || payload.serving_unit }])
        setCreatingNew(false)
        setNewFood({ name: '', serving_size: '', serving_unit: 'g', calories: '', protein: '', carbohydrates: '', fat: '', saturated_fat: '', monounsaturated_fat: '', polyunsaturated_fat: '', trans_fat: '', cholesterol: '', fiber: '', sugar: '', sodium: '', potassium: '', calcium: '', iron: '', vitamin_d: '', zinc: '', notes: '' })
        setShowFoodModal(false)
      }
    } catch (e) {
      console.error('Create food item failed', e)
    }
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <AppBar title="Create Meal" showBackButton />

      <View style={{ padding: 16, gap: 16 }}>
        <View>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>MEAL NAME</Text>
          <TextInput
            value={name}
            onChangeText={setName}
            placeholder="Enter meal name"
            style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12 }}
          />
        </View>

        <View>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>DATE & TIME</Text>
          <View style={{ flexDirection: 'row', gap: 12 }}>
            <Pressable onPress={() => setDt(new Date(Date.now()))} style={{ padding: 10, borderWidth: 1, borderColor: '#ddd', borderRadius: 8 }}>
              <Text>{dt.toLocaleDateString()}</Text>
            </Pressable>
            <Pressable onPress={() => setDt(new Date(Date.now()))} style={{ padding: 10, borderWidth: 1, borderColor: '#ddd', borderRadius: 8 }}>
              <Text>{dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
            </Pressable>
          </View>
        </View>

        <View>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>MEAL TYPE</Text>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
            {mealTypes.map(t => (
              <Pressable key={t} onPress={() => setMealType(t)} style={{ paddingVertical: 6, paddingHorizontal: 10, borderRadius: 12, borderWidth: 1, borderColor: mealType === t ? '#1d4ed8' : '#ddd', backgroundColor: mealType === t ? '#e0ecff' : '#fff' }}>
                <Text>{t}</Text>
              </Pressable>
            ))}
          </View>
        </View>

        <View>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>FOODS</Text>
          {selectedFoods.length === 0 ? (
            <Text style={{ color: '#666', marginBottom: 8 }}>No foods added yet</Text>
          ) : (
            <View style={{ marginBottom: 8 }}>
              {selectedFoods.map((sf, idx) => (
                <View key={sf.foodItem.id_ + '-' + idx} style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#eee' }}>
                  <View>
                    <Text style={{ fontWeight: '600' }}>{sf.foodItem.name}</Text>
                    <Text style={{ color: '#666' }}>{sf.quantity} {sf.servingUnit}</Text>
                  </View>
                  <Pressable onPress={() => removeSelectedFoodAt(idx)} style={{ paddingHorizontal: 8, paddingVertical: 6 }}>
                    <Text style={{ color: '#b91c1c', fontWeight: '600' }}>Remove</Text>
                  </Pressable>
                </View>
              ))}
            </View>
          )}
          <Pressable onPress={() => { setShowFoodModal(true); setCreatingNew(false) }} style={{ borderWidth: 1, borderColor: '#1d4ed8', borderRadius: 10, paddingVertical: 10, alignItems: 'center' }}>
            <Text style={{ color: '#1d4ed8', fontWeight: '700' }}>Add Food</Text>
          </Pressable>
        </View>

        <View>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>NOTES</Text>
          <TextInput
            value={notes}
            onChangeText={setNotes}
            placeholder="Add notes..."
            multiline
            style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, minHeight: 80, textAlignVertical: 'top' }}
          />
        </View>

        <Pressable disabled={!canSubmit || creatingMeal} onPress={onSubmit} style={{ marginTop: 12, backgroundColor: canSubmit ? '#1d4ed8' : '#93c5fd', paddingVertical: 14, borderRadius: 10, alignItems: 'center' }}>
          <Text style={{ color: '#fff', fontWeight: '700' }}>{creatingMeal ? 'Creating…' : 'CREATE MEAL'}</Text>
        </Pressable>
      </View>

      {/* Food search modal */}
      <Modal visible={showFoodModal} transparent animationType="fade" onRequestClose={() => setShowFoodModal(false)}>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <Pressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => setShowFoodModal(false)} />
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%' }}>
            <View style={{ alignSelf: 'center', width: '96%', backgroundColor: '#fff', maxHeight: '90%', borderRadius: 12, padding: 16, position: 'relative' }}>
              {!creatingNew ? (
                <>
                  <Text style={{ fontWeight: '600', fontSize: 16, marginBottom: 10 }}>Add Food</Text>
                  <TextInput
                    value={search}
                    onChangeText={setSearch}
                    placeholder="Search for food items..."
                    placeholderTextColor="#9CA3AF"
                    autoFocus
                    style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10, marginBottom: 12 }}
                  />
                  <Pressable onPress={() => setCreatingNew(true)} style={{ paddingVertical: 10 }}>
                    <Text style={{ color: '#1d4ed8', fontWeight: '700' }}>＋ Create New Item</Text>
                  </Pressable>
                  <View style={{ height: Platform.OS === 'web' ? 420 : 360, marginTop: 6 }}>
                    <FlatList
                      keyboardShouldPersistTaps="handled"
                      showsVerticalScrollIndicator={true}
                      data={searchResults}
                      keyExtractor={(item) => item.id_}
                      ListEmptyComponent={!searching ? (
                        <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                          <Text style={{ color: '#6b7280' }}>No matches found</Text>
                        </View>
                      ) : null}
                      renderItem={({ item }) => (
                        <Pressable onPress={() => openQuantityFor(item)} style={{ paddingVertical: 10 }}>
                          <Text style={{ fontWeight: '600' }}>{item.name}</Text>
                          <Text style={{ color: '#666' }}>{item.servingSize}{item.servingUnit} • {Math.round(item.calories)} kcal</Text>
                        </Pressable>
                      )}
                    />
                  </View>

                  {/* Quantity selector inline */}
                  {selectedForQuantity && (
                    <View style={{ marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#eee' }}>
                      <Text style={{ fontWeight: '600', marginBottom: 6 }}>Set Quantity</Text>
                      <Text style={{ marginBottom: 6 }}>{selectedForQuantity.name}</Text>
                      <View style={{ flexDirection: 'row', gap: 8 }}>
                        <TextInput
                          value={quantity}
                          onChangeText={setQuantity}
                          keyboardType="numeric"
                          placeholder="Quantity"
                          placeholderTextColor="#9CA3AF"
                          style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }}
                        />
                        <TextInput
                          value={servingUnit}
                          onChangeText={setServingUnit}
                          placeholder="Unit"
                          placeholderTextColor="#9CA3AF"
                          style={{ width: 100, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }}
                        />
                      </View>
                      <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginTop: 10, gap: 10 }}>
                        <Pressable onPress={() => setSelectedForQuantity(null)} style={{ paddingVertical: 10, paddingHorizontal: 12 }}>
                          <Text style={{ color: '#666' }}>Cancel</Text>
                        </Pressable>
                        <Pressable onPress={addSelectedFood} style={{ paddingVertical: 10, paddingHorizontal: 12, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
                          <Text style={{ color: '#fff', fontWeight: '700' }}>Add</Text>
                        </Pressable>
                      </View>
                    </View>
                  )}
                </>
              ) : (
                <>
                  <Text style={{ fontWeight: '600', fontSize: 16, marginBottom: 10 }}>Create Food Item</Text>
                  <ScrollView keyboardShouldPersistTaps="handled" style={{ flex: 1 }} contentContainerStyle={{ paddingBottom: 80 }}>
                    <TextInput value={newFood.name} onChangeText={(v) => setNewFood(s => ({ ...s, name: v }))} placeholder="Name" placeholderTextColor="#9CA3AF" style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                    <View style={{ flexDirection: 'row', gap: 8 }}>
                      <TextInput value={newFood.serving_size} onChangeText={(v) => setNewFood(s => ({ ...s, serving_size: v }))} placeholder="Serving Size" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.serving_unit} onChangeText={(v) => setNewFood(s => ({ ...s, serving_unit: v }))} placeholder="Unit" placeholderTextColor="#9CA3AF" style={{ width: 100, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.calories} onChangeText={(v) => setNewFood(s => ({ ...s, calories: v }))} placeholder="Calories" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.protein} onChangeText={(v) => setNewFood(s => ({ ...s, protein: v }))} placeholder="Protein (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.carbohydrates} onChangeText={(v) => setNewFood(s => ({ ...s, carbohydrates: v }))} placeholder="Carbs (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.fat} onChangeText={(v) => setNewFood(s => ({ ...s, fat: v }))} placeholder="Fat (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <Text style={{ marginTop: 12, fontWeight: '600' }}>Micronutrients (optional)</Text>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.fiber} onChangeText={(v) => setNewFood(s => ({ ...s, fiber: v }))} placeholder="Fiber (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.sugar} onChangeText={(v) => setNewFood(s => ({ ...s, sugar: v }))} placeholder="Sugar (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.sodium} onChangeText={(v) => setNewFood(s => ({ ...s, sodium: v }))} placeholder="Sodium (mg)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.potassium} onChangeText={(v) => setNewFood(s => ({ ...s, potassium: v }))} placeholder="Potassium (mg)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.calcium} onChangeText={(v) => setNewFood(s => ({ ...s, calcium: v }))} placeholder="Calcium (mg)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.iron} onChangeText={(v) => setNewFood(s => ({ ...s, iron: v }))} placeholder="Iron (mg)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.vitamin_d} onChangeText={(v) => setNewFood(s => ({ ...s, vitamin_d: v }))} placeholder="Vitamin D (mcg)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.zinc} onChangeText={(v) => setNewFood(s => ({ ...s, zinc: v }))} placeholder="Zinc (mg)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.cholesterol} onChangeText={(v) => setNewFood(s => ({ ...s, cholesterol: v }))} placeholder="Cholesterol (mg)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.saturated_fat} onChangeText={(v) => setNewFood(s => ({ ...s, saturated_fat: v }))} placeholder="Saturated Fat (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.monounsaturated_fat} onChangeText={(v) => setNewFood(s => ({ ...s, monounsaturated_fat: v }))} placeholder="Monounsat. Fat (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                      <TextInput value={newFood.polyunsaturated_fat} onChangeText={(v) => setNewFood(s => ({ ...s, polyunsaturated_fat: v }))} placeholder="Polyunsat. Fat (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
                      <TextInput value={newFood.trans_fat} onChangeText={(v) => setNewFood(s => ({ ...s, trans_fat: v }))} placeholder="Trans Fat (g)" placeholderTextColor="#9CA3AF" keyboardType="numeric" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                    </View>
                    <TextInput value={newFood.notes} onChangeText={(v) => setNewFood(s => ({ ...s, notes: v }))} placeholder="Notes (optional)" placeholderTextColor="#9CA3AF" style={{ marginTop: 8, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
                  </ScrollView>
                  <View style={{ position: 'absolute', left: 0, right: 0, bottom: 0, borderTopWidth: 1, borderTopColor: '#eee', padding: 12, backgroundColor: '#fff', flexDirection: 'row', justifyContent: 'flex-end', gap: 10 }}>
                    <Pressable onPress={() => setCreatingNew(false)} style={{ paddingVertical: 10, paddingHorizontal: 12 }}>
                      <Text style={{ color: '#666' }}>Cancel</Text>
                    </Pressable>
                    <Pressable disabled={creatingFood} onPress={saveNewFoodItem} style={{ paddingVertical: 10, paddingHorizontal: 12, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
                      <Text style={{ color: '#fff', fontWeight: '700' }}>{creatingFood ? 'Saving…' : 'Save Item'}</Text>
                    </Pressable>
                  </View>
                </>
              )}
            </View>
          </KeyboardAvoidingView>
        </View>
      </Modal>
    </SafeAreaView>
  )
} 