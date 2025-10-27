import React, { useEffect, useMemo, useRef, useState } from 'react'
import { SafeAreaView, View, Text, TextInput, Pressable, Modal, FlatList, KeyboardAvoidingView, Platform, Animated, Easing } from 'react-native'
import { gql, useLazyQuery, useMutation } from '@apollo/client'
import { AppBar } from '@/components/common/AppBar'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { useAuth } from '@/features/auth/context/AuthContext'

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
    importOffProduct(code: $code) { id_ name servingUnit servingSize calories protein carbohydrates fat }
  }
`

const ADD_FOOD_TO_MEAL = gql`
  mutation AddFood($mealId: ID!, $foodItemId: ID!, $quantity: Float!, $servingUnit: String!) {
    addFoodToMeal(mealId: $mealId, foodItemId: $foodItemId, quantity: $quantity, servingUnit: $servingUnit) {
      id_
    }
  }
`

export default function AddIngredientScreen() {
  const { mealId } = useLocalSearchParams<{ mealId: string }>()
  const { session } = useAuth()
  const userId = session?.user?.id || ''
  const router = useRouter()

  const [search, setSearch] = useState('')
  const [showFoodModal, setShowFoodModal] = useState(true)
  const [selectedForQuantity, setSelectedForQuantity] = useState<any | null>(null)
  const [quantity, setQuantity] = useState<string>('1')
  const [servingUnit, setServingUnit] = useState<string>('')

  const [runSearch, { data: searchData, loading: searching }] = useLazyQuery(SEARCH_FOOD_ITEMS, { fetchPolicy: 'network-only' })
  const [runAutocomplete, { data: autoData }] = useLazyQuery(AUTOCOMPLETE_FOOD_ITEMS, { fetchPolicy: 'no-cache' })
  const [importOff] = useMutation(IMPORT_OFF_PRODUCT)
  const [addFood] = useMutation(ADD_FOOD_TO_MEAL)

  useEffect(() => {
    const term = (search || '').trim()
    const h = setTimeout(() => {
      runSearch({ variables: { userId, search: term, limit: 15 } })
      if (term.length > 1) runAutocomplete({ variables: { q: term, limit: 8 } })
    }, 300)
    return () => clearTimeout(h)
  }, [search, userId, runSearch, runAutocomplete])

  const searchResults = searchData?.foodItemsForUserWithPublic ?? []
  const offResults = useMemo(() => (autoData?.foodItemsAutocomplete ?? []).filter((r: any) => r.source === 'off').slice(0,4), [autoData])

  const openQuantityFor = (item: any) => {
    setSelectedForQuantity(item)
    setQuantity(item?.servingSize != null ? String(item.servingSize) : '1')
    setServingUnit(item?.servingUnit || 'g')
  }

  const onImportOffPress = async (externalId?: string | null) => {
    if (!externalId) return
    const res = await importOff({ variables: { code: externalId } })
    const created = res.data?.importOffProduct
    if (created) openQuantityFor(created)
  }

  const onAdd = async () => {
    if (!selectedForQuantity || !mealId) return
    const qty = parseFloat(quantity)
    if (!isFinite(qty) || qty <= 0) return
    const unit = (servingUnit || selectedForQuantity.servingUnit || 'g').trim()
    await addFood({ variables: { mealId, foodItemId: selectedForQuantity.id_, quantity: qty, servingUnit: unit } })
    router.replace(`/meals/${mealId}`)
  }

  const qtyAnimOpacity = useRef(new Animated.Value(0)).current
  const qtyAnimTranslateY = useRef(new Animated.Value(24)).current
  useEffect(() => {
    if (selectedForQuantity) {
      qtyAnimOpacity.setValue(0)
      qtyAnimTranslateY.setValue(24)
      Animated.parallel([
        Animated.timing(qtyAnimOpacity, { toValue: 1, duration: 180, easing: Easing.out(Easing.quad), useNativeDriver: true }),
        Animated.timing(qtyAnimTranslateY, { toValue: 0, duration: 200, easing: Easing.out(Easing.quad), useNativeDriver: true }),
      ]).start()
    }
  }, [selectedForQuantity])

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <AppBar title="Add Ingredient" showBackButton onBackPress={() => router.replace(`/meals/${mealId}`)} />

      <View style={{ padding: 16, gap: 12, flex: 1 }}>
        <Text style={{ fontWeight: '600' }}>Search for a food item</Text>
        <TextInput value={search} onChangeText={setSearch} placeholder="Search foods…" style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
        <View style={{ flex: 1 }}>
          <FlatList
            keyboardDismissMode="on-drag"
            keyboardShouldPersistTaps="handled"
            data={searchResults}
            keyExtractor={(item) => item.id_}
            renderItem={({ item }) => (
              <Pressable onPress={() => openQuantityFor(item)} style={{ paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#f1f5f9' }}>
                <Text style={{ fontWeight: '600' }}>{item.name}</Text>
                <Text style={{ color: '#666' }}>{item.servingSize}{item.servingUnit} • {Math.round(item.calories)} kcal</Text>
              </Pressable>
            )}
            ListFooterComponent={offResults.length > 0 ? (
              <View style={{ marginTop: 16 }}>
                <View style={{ backgroundColor: '#f9fafb', paddingVertical: 6, paddingHorizontal: 10, borderRadius: 8, marginBottom: 8, borderWidth: 1, borderColor: '#e5e7eb' }}>
                  <Text style={{ fontWeight: '700', color: '#111827' }}>Open Food Facts</Text>
                </View>
                {offResults.map((r: any) => (
                  <Pressable key={(r.externalId || r.name) + (r.brand || '')} onPress={() => onImportOffPress(r.externalId)} style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#f3f4f6' }}>
                    <Text style={{ fontWeight: '600' }}>{r.name}{r.brand ? ` • ${r.brand}` : ''}</Text>
                  </Pressable>
                ))}
              </View>
            ) : null}
          />
        </View>
      </View>

      {selectedForQuantity && (
        <Animated.View style={{ position: 'absolute', left: 16, right: 16, bottom: 16, backgroundColor: '#fff', borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 10, padding: 12, shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, opacity: qtyAnimOpacity, transform: [{ translateY: qtyAnimTranslateY }] }}>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>Set Quantity</Text>
          <Text style={{ marginBottom: 6 }}>{selectedForQuantity.name}</Text>
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <TextInput value={quantity} onChangeText={setQuantity} keyboardType="numeric" placeholder="Quantity" style={{ flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
            <TextInput value={servingUnit} onChangeText={setServingUnit} placeholder="Unit" style={{ width: 100, borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
          </View>
          <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginTop: 10, gap: 10 }}>
            <Pressable onPress={() => setSelectedForQuantity(null)} style={{ paddingVertical: 10, paddingHorizontal: 12 }}>
              <Text style={{ color: '#666' }}>Cancel</Text>
            </Pressable>
            <Pressable onPress={onAdd} style={{ paddingVertical: 10, paddingHorizontal: 12, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
              <Text style={{ color: '#fff', fontWeight: '700' }}>Add</Text>
            </Pressable>
          </View>
        </Animated.View>
      )}
    </SafeAreaView>
  )
} 