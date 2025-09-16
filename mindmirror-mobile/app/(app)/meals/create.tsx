import React, { useEffect, useMemo, useRef, useState } from 'react'
import { SafeAreaView, View, Text, TextInput, Pressable, Modal, FlatList, KeyboardAvoidingView, ScrollView, Platform, Animated, Easing } from 'react-native'
import DateTimePicker from '@react-native-community/datetimepicker'
import { gql, useMutation, useLazyQuery } from '@apollo/client'
import { AppBar } from '@/components/common/AppBar'
import { useRouter, useLocalSearchParams } from 'expo-router'
import { useAuth } from '@/features/auth/context/AuthContext'
import { getRecentFoods, addRecentFood } from '@/utils/recents'
import { findMatchingTemplates, recordMealAsTemplate, MealTemplateItem } from '@/utils/templates'

const CREATE_MEAL = gql`
  mutation CreateMeal($input: MealCreateInput!) {
    createMeal(input: $input) {
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
    createFoodItem(input: $input) {
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

const AUTOCOMPLETE_FOOD_ITEMS = gql`
  query AutocompleteFoods($q: String!, $limit: Int) {
    foodItemsAutocomplete(query: $q, limit: $limit) {
      source
      id_
      externalId
      name
      brand
      thumbnailUrl
      nutritionGrades
    }
  }
`

const IMPORT_OFF_PRODUCT = gql`
  mutation ImportOff($code: String!) {
    importOffProduct(code: $code) {
      id_
      name
      servingSize
      servingUnit
      calories
      protein
      carbohydrates
      fat
      brand
      thumbnailUrl
      source
      externalSource
      externalId
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
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [showTimePicker, setShowTimePicker] = useState(false)
  const [selectedFoods, setSelectedFoods] = useState<SelectedFood[]>([])

  const [showFoodModal, setShowFoodModal] = useState(false)
  const [search, setSearch] = useState('')
  const [selectedForQuantity, setSelectedForQuantity] = useState<any | null>(null)
  const [quantity, setQuantity] = useState<string>('1')
  const [servingUnit, setServingUnit] = useState<string>('')
  const [editIndex, setEditIndex] = useState<number | null>(null)
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
  const params = useLocalSearchParams<{ from?: string; openFoodModal?: string; importAddId?: string }>()
  const returnTo = (params?.from as string) || '/meals'
  const { session } = useAuth()
  const userId = session?.user?.id || ''

  const [createMeal, { loading: creatingMeal }] = useMutation(CREATE_MEAL)
  const [createFoodItem, { loading: creatingFood }] = useMutation(CREATE_FOOD_ITEM)
  const [runSearch, { data: searchData, loading: searching }] = useLazyQuery(SEARCH_FOOD_ITEMS, {
    fetchPolicy: 'network-only',
    nextFetchPolicy: 'network-only',
    notifyOnNetworkStatusChange: true,
  })
  const [runAutocomplete, { data: autoData, loading: autoLoading, refetch: refetchAuto }] = useLazyQuery(AUTOCOMPLETE_FOOD_ITEMS, {
    fetchPolicy: 'no-cache',
    nextFetchPolicy: 'no-cache',
    notifyOnNetworkStatusChange: true,
  })
  const [importOff, { loading: importingOff }] = useMutation(IMPORT_OFF_PRODUCT)
  const [toast, setToast] = useState<{ msg: string; type: 'error' | 'success' } | null>(null)
  const showToast = (msg: string, type: 'error' | 'success' = 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 2500)
  }
  const resultsHeight = useMemo(() => {
    if (selectedForQuantity) return Platform.OS === 'web' ? 220 : 180
    return Platform.OS === 'web' ? 420 : 360
  }, [selectedForQuantity])

  const qtyAnimOpacity = useRef(new Animated.Value(0)).current
  const qtyAnimTranslateY = useRef(new Animated.Value(24)).current

  useEffect(() => {
    if (selectedForQuantity) {
      qtyAnimOpacity.setValue(0)
      qtyAnimTranslateY.setValue(24)
      Animated.parallel([
        Animated.timing(qtyAnimOpacity, {
          toValue: 1,
          duration: 180,
          easing: Easing.out(Easing.quad),
          useNativeDriver: true,
        }),
        Animated.timing(qtyAnimTranslateY, {
          toValue: 0,
          duration: 200,
          easing: Easing.out(Easing.quad),
          useNativeDriver: true,
        }),
      ]).start()
    }
  }, [selectedForQuantity, qtyAnimOpacity, qtyAnimTranslateY])

  useEffect(() => {
    if (params?.openFoodModal === '1') {
      setShowFoodModal(true)
      // Clear search state when opening fresh
      setSearch('')
      setSelectedForQuantity(null)
      setEditIndex(null)
      setQuantity('1')
    }
    // If we were sent back with an imported item id, fetch minimal fields via search and preselect
    const importId = params?.importAddId as string | undefined
    if (importId && showFoodModal) {
      // try to find it in the current user+public query by id
      runSearch({ variables: { userId, search: '', limit: 25 } }).then((result: any) => {
        const all = (result?.data?.foodItemsForUserWithPublic ?? []) as any[]
        const found = all.find((f: any) => f.id_ === importId)
        if (found) openQuantityFor(found)
      }).catch(() => {})
    }
    const term = (search || '').trim()
    const h = setTimeout(() => {
      if (!showFoodModal) return
      runSearch({ variables: { userId, search: term, limit: 15 } })
      if (term.length > 1) {
        runAutocomplete({ variables: { q: term, limit: 8 } })
      }
    }, 300)
    return () => clearTimeout(h)
  }, [search, showFoodModal, runSearch, runAutocomplete, userId, params?.openFoodModal, params?.importAddId])

  const searchResults = searchData?.foodItemsForUserWithPublic ?? []
  const [recentFoods, setRecentFoods] = useState<any[]>([])
  useEffect(() => {
    (async () => {
      if (!userId) return
      const rec = await getRecentFoods(userId)
      setRecentFoods(rec)
    })()
  }, [userId, showFoodModal])

  const biasedResults = useMemo(() => {
    const term = (search || '').trim().toLowerCase()
    if (!term) return []
    const matchesRecent = recentFoods
      .filter(r => (r.name || '').toLowerCase().includes(term))
      .map(r => ({ ...r, __recent: true }))
    // Deduplicate by id_ then name
    const seen = new Set<string>()
    const merged: any[] = []
    for (const r of [...matchesRecent, ...searchResults]) {
      const key = r.id_ || r.name
      if (!key || seen.has(key)) continue
      seen.add(key)
      merged.push(r)
      if (merged.length >= 50) break
    }
    return merged
  }, [search, searchResults, recentFoods])

  const offResults = useMemo(() => {
    const list = autoData?.foodItemsAutocomplete ?? []
    const seen = new Set<string>()
    const filtered: any[] = []
    for (const r of list) {
      const key = (r.externalId || r.name) + '|' + (r.brand || '')
      if (!seen.has(key)) { seen.add(key); filtered.push(r) }
    }
    return filtered.filter((r: any) => r.source === 'off').slice(0, 4)
  }, [autoData])

  const nutriColor = (grade?: string | null) => {
    const g = (grade || '').toLowerCase()
    if (g === 'a') return '#16a34a'
    if (g === 'b') return '#65a30d'
    if (g === 'c') return '#ca8a04'
    if (g === 'd') return '#ea580c'
    if (g === 'e') return '#dc2626'
    return '#6b7280'
  }

  const onImportOffPress = async (externalId?: string | null) => {
    if (!externalId) return
    try {
      const res = await importOff({ variables: { code: externalId } })
      const created = res.data?.importOffProduct
      if (created) {
        // Immediately open quantity selector for the imported item within the modal
        openQuantityFor(created)
      }
    } catch (e) {
      console.error('Import OFF product failed', e)
      showToast('Import failed. Please try again.', 'error')
    }
  }

  const input = useMemo(() => ({
    userId: userId,
    name,
    type: mealType,
    date: dt.toISOString(),
    notes: notes || null,
    mealFoodsData: selectedFoods.map(sf => ({
      foodItemId: sf.foodItem.id_,
      quantity: sf.quantity,
      servingUnit: sf.servingUnit || sf.foodItem.servingUnit,
    })),
  }), [userId, name, mealType, dt, notes, selectedFoods])

  const canSubmit = name.trim().length > 0 && !!userId

  const onSubmit = async () => {
    if (!canSubmit) return
    try {
      const dayStr = dt.toISOString().slice(0,10)
      await createMeal({
        variables: { input },
        refetchQueries: [
          {
            query: gql`query MealsMini($userId: String!, $start: String!, $end: String!, $limit: Int) { mealsByUserAndDateRange(userId: $userId, startDate: $start, endDate: $end, limit: $limit) { id_ } }`,
            variables: { userId, start: dayStr, end: dayStr, limit: 50 },
          },
          {
            query: gql`query MealsByUser($userId: String!, $start: String!, $end: String!, $limit: Int) { mealsByUserAndDateRange(userId: $userId, startDate: $start, endDate: $end, limit: $limit) { id_ } }`,
            variables: { userId, start: dayStr, end: dayStr, limit: 50 },
          },
        ],
        awaitRefetchQueries: true,
      })
      // Save/update template for this meal name
      try {
        if (name.trim() && selectedFoods.length > 0 && userId) {
          const items: MealTemplateItem[] = selectedFoods.map(sf => ({
            foodItem: {
              id_: sf.foodItem.id_,
              name: sf.foodItem.name,
              servingUnit: sf.foodItem.servingUnit,
              servingSize: sf.foodItem.servingSize,
              calories: sf.foodItem.calories,
              protein: sf.foodItem.protein,
              carbohydrates: sf.foodItem.carbohydrates,
              fat: sf.foodItem.fat,
            },
            quantity: sf.quantity,
            servingUnit: sf.servingUnit || sf.foodItem.servingUnit,
          }))
          await recordMealAsTemplate(userId, name.trim(), items)
        }
      } catch {}
      if (params?.from) router.replace(returnTo)
      else router.replace('/meals')
    } catch (e) {
      console.error('Create meal failed', e)
    }
  }

  const openQuantityFor = (item: any, index: number | null = null, presetQty?: number, presetUnit?: string) => {
    setSelectedForQuantity(item)
    setQuantity(presetQty != null ? String(presetQty) : (item?.servingSize != null ? String(item.servingSize) : '1'))
    setServingUnit(presetUnit || item.servingUnit || 'g')
    setEditIndex(index)
  }

  const addSelectedFood = () => {
    if (!selectedForQuantity) return
    const qty = parseFloat(quantity)
    if (!isFinite(qty) || qty <= 0) return
    const unit = (servingUnit || selectedForQuantity.servingUnit || 'g').trim()
    setSelectedFoods((prev) => {
      if (editIndex != null) {
        const copy = [...prev]
        copy[editIndex] = { foodItem: selectedForQuantity, quantity: qty, servingUnit: unit }
        return copy
      }
      return [...prev, { foodItem: selectedForQuantity, quantity: qty, servingUnit: unit }]
    })
    // bump recents
    if (userId && selectedForQuantity) {
      addRecentFood(userId, {
        id_: selectedForQuantity.id_,
        name: selectedForQuantity.name,
        servingSize: selectedForQuantity.servingSize,
        servingUnit: selectedForQuantity.servingUnit,
        calories: selectedForQuantity.calories,
      })
    }
    setSelectedForQuantity(null)
    setEditIndex(null)
    setQuantity('1')
  }

  const removeSelectedFoodAt = (idx: number) => {
    setSelectedFoods(prev => prev.filter((_, i) => i !== idx))
  }

  const saveNewFoodItem = async () => {
    if (!userId) return
    const payload: any = {
      userId: userId,
      name: newFood.name.trim(),
      servingSize: parseFloat(newFood.serving_size) || 0,
      servingUnit: newFood.serving_unit.trim() || 'g',
      calories: parseFloat(newFood.calories) || 0,
    }
    if (newFood.protein) payload.protein = parseFloat(newFood.protein)
    if (newFood.carbohydrates) payload.carbohydrates = parseFloat(newFood.carbohydrates)
    if (newFood.fat) payload.fat = parseFloat(newFood.fat)
    if (newFood.saturated_fat) payload.saturatedFat = parseFloat(newFood.saturated_fat)
    if (newFood.monounsaturated_fat) payload.monounsaturatedFat = parseFloat(newFood.monounsaturated_fat)
    if (newFood.polyunsaturated_fat) payload.polyunsaturatedFat = parseFloat(newFood.polyunsaturated_fat)
    if (newFood.trans_fat) payload.transFat = parseFloat(newFood.trans_fat)
    if (newFood.cholesterol) payload.cholesterol = parseFloat(newFood.cholesterol)
    if (newFood.fiber) payload.fiber = parseFloat(newFood.fiber)
    if (newFood.sugar) payload.sugar = parseFloat(newFood.sugar)
    if (newFood.sodium) payload.sodium = parseFloat(newFood.sodium)
    if (newFood.potassium) payload.potassium = parseFloat(newFood.potassium)
    if (newFood.calcium) payload.calcium = parseFloat(newFood.calcium)
    if (newFood.iron) payload.iron = parseFloat(newFood.iron)
    if (newFood.vitamin_d) payload.vitaminD = parseFloat(newFood.vitamin_d)
    if (newFood.zinc) payload.zinc = parseFloat(newFood.zinc)
    if (newFood.notes?.trim()) payload.notes = newFood.notes.trim()

    try {
      const res = await createFoodItem({ variables: { input: payload } })
      const created = res.data?.createFoodItem
      if (created) {
        setSelectedFoods(prev => [...prev, { foodItem: created, quantity: created.servingSize || 1, servingUnit: created.servingUnit || payload.servingUnit }])
        setCreatingNew(false)
        setNewFood({ name: '', serving_size: '', serving_unit: 'g', calories: '', protein: '', carbohydrates: '', fat: '', saturated_fat: '', monounsaturated_fat: '', polyunsaturated_fat: '', trans_fat: '', cholesterol: '', fiber: '', sugar: '', sodium: '', potassium: '', calcium: '', iron: '', vitamin_d: '', zinc: '', notes: '' })
        setShowFoodModal(false)
      }
    } catch (e) {
      console.error('Create food item failed', e)
    }
  }

  const colors = {
    protein: '#16a34a', // green-600
    carbs: '#d97706',   // amber-700
    fat: '#2563eb',     // blue-600
    dot: '#9ca3af',     // gray-400
  }

  const formatMacros = (sf: SelectedFood) => {
    const fi = sf.foodItem
    const baseSize = Number(fi.servingSize) || 0
    const sameUnit = (sf.servingUnit || '').toLowerCase() === (fi.servingUnit || '').toLowerCase()
    const factor = baseSize > 0 && sameUnit ? sf.quantity / baseSize : 1
    const p = Math.round((fi.protein || 0) * factor)
    const c = Math.round((fi.carbohydrates || 0) * factor)
    const f = Math.round((fi.fat || 0) * factor)
    return { p, c, f }
  }

  const formatPreviewMacros = () => {
    const fi = selectedForQuantity
    if (!fi) return { p: 0, c: 0, f: 0, kcal: 0 }
    const qtyNum = parseFloat(quantity) || 0
    const baseSize = Number(fi.servingSize) || 0
    const sameUnit = (servingUnit || '').toLowerCase() === (fi.servingUnit || '').toLowerCase()
    const factor = baseSize > 0 && sameUnit ? qtyNum / baseSize : (baseSize > 0 && !sameUnit ? 1 : qtyNum)
    const p = Math.round((fi.protein || 0) * (isFinite(factor) ? factor : 0))
    const c = Math.round((fi.carbohydrates || 0) * (isFinite(factor) ? factor : 0))
    const f = Math.round((fi.fat || 0) * (isFinite(factor) ? factor : 0))
    const kcal = Math.round((fi.calories || 0) * (isFinite(factor) ? factor : 0))
    return { p, c, f, kcal }
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <AppBar title="Create Meal" showBackButton onBackPress={() => {
        if (params?.from) router.replace(returnTo)
        else router.back()
      }} />

      <View style={{ padding: 16, gap: 16 }}>
        <View>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>MEAL NAME</Text>
          <TextInput
            value={name}
            onChangeText={setName}
            placeholder="Enter meal name"
            style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12 }}
          />
          {/* Template suggestions */}
          {name.trim().length >= 1 && (
            <TemplateSuggestions userId={userId} query={name} onPrefill={(tpl: any) => {
              // Prefill selectedFoods from template
              setSelectedFoods(tpl.items.map((it: any) => ({
                foodItem: {
                  id_: it.foodItem.id_,
                  name: it.foodItem.name,
                  servingUnit: it.foodItem.servingUnit || 'g',
                  servingSize: it.foodItem.servingSize,
                  calories: it.foodItem.calories,
                  protein: it.foodItem.protein,
                  carbohydrates: it.foodItem.carbohydrates,
                  fat: it.foodItem.fat,
                } as any,
                quantity: it.quantity,
                servingUnit: it.servingUnit || it.foodItem.servingUnit || 'g'
              })))
            }} onQuickAdd={async (tpl: any) => {
              // Submit immediately using current date/time
              if (!userId) return
              const quickItems: { foodItemId: string; quantity: number; servingUnit: string }[] = tpl.items.map((it: any) => ({
                foodItemId: it.foodItem.id_,
                quantity: it.quantity,
                servingUnit: it.servingUnit || it.foodItem.servingUnit || 'g'
              }))
              const quickInput: any = {
                userId,
                name: tpl.name as string,
                type: mealType as any,
                date: new Date().toISOString(),
                notes: (notes || null) as any,
                mealFoodsData: quickItems
              }
              try {
                await createMeal({ variables: { input: quickInput } })
                await recordMealAsTemplate(userId, tpl.name, tpl.items)
                router.replace(returnTo)
              } catch (e: any) {
                console.error('Quick add failed', e)
              }
            }} />
          )}
        </View>

        <View>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>DATE & TIME</Text>
          <View style={{ flexDirection: 'row', gap: 12 }}>
            <Pressable onPress={() => setShowDatePicker(true)} style={{ padding: 10, borderWidth: 1, borderColor: '#ddd', borderRadius: 8 }}>
              <Text>{dt.toLocaleDateString()}</Text>
            </Pressable>
            <Pressable onPress={() => setShowTimePicker(true)} style={{ padding: 10, borderWidth: 1, borderColor: '#ddd', borderRadius: 8 }}>
              <Text>{dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
            </Pressable>
          </View>
          {showDatePicker && (
            <DateTimePicker
              value={dt}
              mode="date"
              display={Platform.OS === 'ios' ? 'inline' : 'default'}
              onChange={(_: any, d?: Date) => { setShowDatePicker(false); if (d) { const newDt = new Date(dt); newDt.setFullYear(d.getFullYear(), d.getMonth(), d.getDate()); setDt(newDt) } }}
            />
          )}
          {showTimePicker && (
            <DateTimePicker
              value={dt}
              mode="time"
              is24Hour={false}
              display={Platform.OS === 'ios' ? 'spinner' : 'default'}
              onChange={(_: any, d?: Date) => { setShowTimePicker(false); if (d) { const newDt = new Date(dt); newDt.setHours(d.getHours(), d.getMinutes(), 0, 0); setDt(newDt) } }}
            />
          )}
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
              {selectedFoods.map((sf, idx) => {
                const macros = formatMacros(sf)
                return (
                  <Pressable key={sf.foodItem.id_ + '-' + idx} onPress={() => { setShowFoodModal(true); setCreatingNew(false); openQuantityFor(sf.foodItem, idx, sf.quantity, sf.servingUnit) }} style={{ paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#eee' }}>
                    <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                      <View style={{ flex: 1 }}>
                        <Text style={{ fontWeight: '600' }}>{sf.foodItem.name}</Text>
                        <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 4 }}>
                          <Text style={{ color: '#666' }}>{sf.quantity} {sf.servingUnit}</Text>
                          <Text style={{ marginHorizontal: 6, color: colors.dot }}>•</Text>
                          <Text style={{ color: colors.protein, fontWeight: '600' }}>{macros.p}P</Text>
                          <Text style={{ marginHorizontal: 6, color: colors.dot }}>•</Text>
                          <Text style={{ color: colors.carbs, fontWeight: '600' }}>{macros.c}C</Text>
                          <Text style={{ marginHorizontal: 6, color: colors.dot }}>•</Text>
                          <Text style={{ color: colors.fat, fontWeight: '600' }}>{macros.f}F</Text>
                        </View>
                      </View>
                      <Pressable onPress={() => removeSelectedFoodAt(idx)} hitSlop={8} style={{ paddingHorizontal: 8, paddingVertical: 6 }}>
                        <Text style={{ color: '#b91c1c', fontWeight: '600' }}>Remove</Text>
                      </Pressable>
                    </View>
                  </Pressable>
                )
              })}
            </View>
          )}
          <Pressable onPress={() => { setShowFoodModal(true); setCreatingNew(false); setSelectedForQuantity(null); setEditIndex(null); setQuantity('1'); setSearch('') }} style={{ borderWidth: 1, borderColor: '#1d4ed8', borderRadius: 10, paddingVertical: 10, alignItems: 'center' }}>
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
      <Modal visible={showFoodModal} transparent animationType="fade" onRequestClose={() => { setShowFoodModal(false); setSearch(''); setSelectedForQuantity(null); setEditIndex(null) }}>
        <View style={{ flex: 1, justifyContent: 'flex-start', alignItems: 'center' }}>
          <Pressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => { setShowFoodModal(false); setSearch(''); setSelectedForQuantity(null); setEditIndex(null) }} />
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
            <View style={{ width: '96%', backgroundColor: '#fff', maxHeight: '80%', borderRadius: 12, padding: 16, position: 'relative' }}>
              {toast && (
                <View style={{ position: 'absolute', top: 48, left: 16, right: 16, zIndex: 10, alignItems: 'center' }}>
                  <View style={{ paddingVertical: 8, paddingHorizontal: 12, borderRadius: 10, backgroundColor: toast.type === 'error' ? '#ef4444' : '#16a34a' }}>
                    <Text style={{ color: '#fff', fontWeight: '700' }}>{toast.msg}</Text>
                  </View>
                </View>
              )}
              {!creatingNew ? (
                <View style={{ flex: 1 }}>
                  <Text style={{ fontWeight: '600', fontSize: 16, marginBottom: 10 }}>{editIndex != null ? 'Edit Quantity' : 'Add Food'}</Text>
                  <View style={{ flexDirection: 'row', gap: 10, marginBottom: 10 }}>
                    <Pressable onPress={() => setCreatingNew(true)} style={{ flex: 1, paddingVertical: 12, borderRadius: 10, borderWidth: 1, borderColor: '#1d4ed8', alignItems: 'center', backgroundColor: '#ffffff' }}>
                      <Text style={{ color: '#1d4ed8', fontWeight: '800' }}>＋ Create New Item</Text>
                    </Pressable>
                    <Pressable onPress={() => router.push(`/meals/scan?from=${encodeURIComponent('/meals/create?openFoodModal=1')}`)} style={{ flex: 1, paddingVertical: 12, borderRadius: 10, alignItems: 'center', backgroundColor: '#111827' }}>
                      <Text style={{ color: '#fff', fontWeight: '800' }}>Scan Barcode</Text>
                    </Pressable>
                  </View>
                  <TextInput
                    value={search}
                    onChangeText={setSearch}
                    placeholder="Search for food items..."
                    placeholderTextColor="#9CA3AF"
                    autoFocus
                    style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10, marginBottom: 12 }}
                  />
                  <View style={{ flex: 1, marginTop: 6 }}>
                    <FlatList
                      keyboardDismissMode="on-drag"
                      keyboardShouldPersistTaps="handled"
                      showsVerticalScrollIndicator={true}
                      data={biasedResults}
                      keyExtractor={(item) => item.id_}
                      style={{ flex: 1 }}
                      contentContainerStyle={{ paddingTop: 4, paddingBottom: selectedForQuantity ? 220 : 16, flexGrow: 1 }}
                      ListEmptyComponent={!searching ? (
                        <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                          <Text style={{ color: '#6b7280' }}>{(search||'').trim().length === 0 ? 'Type to search your foods' : 'No matches found'}</Text>
                        </View>
                      ) : null}
                      renderItem={({ item }) => (
                        <Pressable onPress={() => openQuantityFor(item)} style={{ paddingVertical: 10 }}>
                          <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                            <View style={{ flex: 1, paddingRight: 8 }}>
                              <Text style={{ fontWeight: '600' }}>{item.name}</Text>
                              <Text style={{ color: '#666' }}>{item.servingSize}{item.servingUnit} • {Math.round(item.calories)} kcal</Text>
                            </View>
                          </View>
                        </Pressable>
                      )}
                      ListFooterComponent={offResults.length > 0 ? (
                        <View style={{ marginTop: 16 }}>
                          <View style={{ backgroundColor: '#f9fafb', paddingVertical: 6, paddingHorizontal: 10, borderRadius: 8, marginBottom: 8, borderWidth: 1, borderColor: '#e5e7eb' }}>
                            <Text style={{ fontWeight: '700', color: '#111827' }}>Open Food Facts</Text>
                          </View>
                          {offResults.map((r: any) => (
                            <Pressable key={(r.externalId || r.name) + (r.brand || '')} onPress={() => onImportOffPress(r.externalId)} style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#f3f4f6' }}>
                              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                                <View style={{ flex: 1, paddingRight: 10 }}>
                                  <Text style={{ fontWeight: '600' }}>
                                    {r.name}{r.brand ? ` • ${r.brand}` : ''}
                                  </Text>
                                </View>
                                {!!r.nutritionGrades && (
                                  <View style={{ minWidth: 28, height: 28, borderRadius: 6, backgroundColor: nutriColor(r.nutritionGrades), alignItems: 'center', justifyContent: 'center' }}>
                                    <Text style={{ color: '#fff', fontWeight: '800' }}>{String(r.nutritionGrades).toUpperCase()}</Text>
                                  </View>
                                )}
                              </View>
                              <View style={{ flexDirection: 'row', gap: 10, marginTop: 8 }}>
                                <Pressable disabled={importingOff} onPress={() => onImportOffPress(r.externalId)}
                                  style={{ paddingVertical: 10, paddingHorizontal: 14, backgroundColor: '#f8fafc', borderRadius: 10, shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 8, shadowOffset: { width: 0, height: 3 }, elevation: 3, borderWidth: 1, borderColor: '#e5e7eb', alignSelf: 'flex-start' }}>
                                  <Text style={{ color: '#111827', fontWeight: '700' }}>{importingOff ? 'Importing…' : 'Import  >'}</Text>
                                </Pressable>
                              </View>
                            </Pressable>
                          ))}
                        </View>
                      ) : null}
                    />
                  </View>

                  {selectedForQuantity && (
                    <Animated.View style={{ position: 'absolute', left: 16, right: 16, bottom: 16, backgroundColor: '#fff', borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 10, padding: 12, shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, opacity: qtyAnimOpacity, transform: [{ translateY: qtyAnimTranslateY }], maxHeight: '50%' }}>
        <ScrollView showsVerticalScrollIndicator={false} style={{ maxHeight: 200 }}>
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
                      {/* Live macro preview */}
                      <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 10, gap: 8 }}>
                        {(() => { const m = formatPreviewMacros(); return (
                          <>
                            <View style={{ paddingVertical: 6, paddingHorizontal: 8, borderRadius: 8, backgroundColor: '#f0fdf4' }}>
                              <Text style={{ color: colors.protein, fontWeight: '700' }}>{m.p}P</Text>
                            </View>
                            <View style={{ paddingVertical: 6, paddingHorizontal: 8, borderRadius: 8, backgroundColor: '#fffbeb' }}>
                              <Text style={{ color: colors.carbs, fontWeight: '700' }}>{m.c}C</Text>
                            </View>
                            <View style={{ paddingVertical: 6, paddingHorizontal: 8, borderRadius: 8, backgroundColor: '#eff6ff' }}>
                              <Text style={{ color: colors.fat, fontWeight: '700' }}>{m.f}F</Text>
                            </View>
                            <Text style={{ marginLeft: 8, color: '#111827', fontWeight: '700' }}>{m.kcal} kcal</Text>
                          </>
                        ) })()}
                      </View>
                      <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginTop: 10, gap: 10 }}>
                        <Pressable onPress={() => { setSelectedForQuantity(null); setEditIndex(null) }} style={{ paddingVertical: 10, paddingHorizontal: 12 }}>
                          <Text style={{ color: '#666' }}>Cancel</Text>
                        </Pressable>
                        <Pressable onPress={addSelectedFood} style={{ paddingVertical: 10, paddingHorizontal: 12, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
                          <Text style={{ color: '#fff', fontWeight: '700' }}>{editIndex != null ? 'Update' : 'Add'}</Text>
                        </Pressable>
                      </View>
                    </ScrollView>
      </Animated.View>
                  )}
                </View>
              ) : (
                <>
                  <Text style={{ fontWeight: '600', fontSize: 16, marginBottom: 10 }}>Create Food Item</Text>
                  <ScrollView keyboardShouldPersistTaps="handled" style={{ flex: 1 }} contentContainerStyle={{ paddingBottom: 100 }}>
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

// Inline lightweight template suggestions component
function TemplateSuggestions({ userId, query, onPrefill, onQuickAdd }: { userId: string; query: string; onPrefill: (tpl: any) => void; onQuickAdd: (tpl: any) => void }) {
  const [items, setItems] = React.useState<any[]>([])
  React.useEffect(() => {
    let active = true
    ;(async () => {
      const list = await findMatchingTemplates(userId, query, 5)
      if (active) setItems(list)
    })()
    return () => { active = false }
  }, [userId, query])
  if (!userId || !query?.trim() || items.length === 0) return null
  return (
    <View style={{ marginTop: 8, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 10, overflow: 'hidden' }}>
      {items.map((tpl: any, idx: number) => (
        <View key={tpl.name + idx} style={{ padding: 10, backgroundColor: '#fff', borderTopWidth: idx === 0 ? 0 : 1, borderTopColor: '#f3f4f6' }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
            <Text style={{ fontWeight: '600' }}>{tpl.name}</Text>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              <Pressable onPress={() => onPrefill(tpl)} style={{ paddingVertical: 6, paddingHorizontal: 10, borderRadius: 8, borderWidth: 1, borderColor: '#1f2937' }}>
                <Text style={{ color: '#1f2937', fontWeight: '700' }}>Prefill</Text>
              </Pressable>
              <Pressable onPress={() => onQuickAdd(tpl)} style={{ paddingVertical: 6, paddingHorizontal: 10, borderRadius: 8, backgroundColor: '#111827' }}>
                <Text style={{ color: '#fff', fontWeight: '800' }}>＋</Text>
              </Pressable>
            </View>
          </View>
          <Text style={{ color: '#6b7280', marginTop: 4 }}>{tpl.items.length} items</Text>
        </View>
      ))}
    </View>
  )
} 