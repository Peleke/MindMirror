import React, { useEffect, useState } from 'react'
import { SafeAreaView, View, Text, TextInput, Pressable } from 'react-native'
import { gql, useMutation, useQuery } from '@apollo/client'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { AppBar } from '@/components/common/AppBar'

const GET_FOOD = gql`
  query Food($id: ID!) {
    foodItem(id: $id) {
      id_
      name
      servingSize
      servingUnit
      calories
      protein
      carbohydrates
      fat
      notes
    }
  }
`

const UPDATE_FOOD = gql`
  mutation UpdateFood($id: ID!, $input: FoodItemUpdateInput!) {
    updateFoodItem(id: $id, input: $input) { id_ name servingSize servingUnit calories protein carbohydrates fat notes }
  }
`

export default function FoodDetailScreen() {
  const params = useLocalSearchParams<{ id: string; from?: string }>()
  const id = params.id
  const from = params.from as string | undefined
  const router = useRouter()
  const q = useQuery(GET_FOOD, { variables: { id } })
  const [updateFood, { loading: saving }] = useMutation(UPDATE_FOOD)

  const food = q.data?.foodItem
  const [form, setForm] = useState<any>({})

  useEffect(() => {
    if (food) setForm({ ...food })
  }, [food])

  const onChange = (key: string, value: string) => setForm((f: any) => ({ ...f, [key]: value }))

  const onSave = async () => {
    const payload: any = {}
    if (form.name !== food.name) payload.name = form.name
    if (String(form.servingSize) !== String(food.servingSize)) payload.serving_size = parseFloat(form.servingSize)
    if (form.servingUnit !== food.servingUnit) payload.serving_unit = form.servingUnit
    ;['calories','protein','carbohydrates','fat'].forEach(k => {
      if (String(form[k]) !== String(food[k])) payload[k] = parseFloat(form[k])
    })
    if (form.notes !== food.notes) payload.notes = form.notes
    await updateFood({ variables: { id, input: payload } })
    q.refetch()
    // After saving, return to the originating screen if provided
    if (from) {
      router.replace(from)
    } else {
      router.back()
    }
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <AppBar title="Food Item" showBackButton onBackPress={() => {
        if (from) router.replace(from)
        else router.back()
      }} />
      {!food ? (
        <View style={{ padding: 16 }}><Text>Loading…</Text></View>
      ) : (
        <View style={{ padding: 16 }}>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>NAME</Text>
          <TextInput value={form.name} onChangeText={(v) => onChange('name', v)} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 12 }} />

          <Text style={{ fontWeight: '600', marginBottom: 6 }}>SERVING</Text>
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <TextInput value={String(form.servingSize ?? '')} onChangeText={(v) => onChange('servingSize', v)} keyboardType="numeric" placeholder="Size" style={{ flex: 1, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
            <TextInput value={form.servingUnit} onChangeText={(v) => onChange('servingUnit', v)} placeholder="Unit" style={{ width: 100, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
          </View>

          <Text style={{ fontWeight: '600', marginVertical: 6 }}>MACROS</Text>
          <View style={{ flexDirection: 'row', gap: 8 }}>
            <TextInput value={String(form.calories ?? '')} onChangeText={(v) => onChange('calories', v)} keyboardType="numeric" placeholder="Calories" style={{ flex: 1, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
            <TextInput value={String(form.protein ?? '')} onChangeText={(v) => onChange('protein', v)} keyboardType="numeric" placeholder="Protein (g)" style={{ flex: 1, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
          </View>
          <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
            <TextInput value={String(form.carbohydrates ?? '')} onChangeText={(v) => onChange('carbohydrates', v)} keyboardType="numeric" placeholder="Carbs (g)" style={{ flex: 1, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
            <TextInput value={String(form.fat ?? '')} onChangeText={(v) => onChange('fat', v)} keyboardType="numeric" placeholder="Fat (g)" style={{ flex: 1, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
          </View>

          <Text style={{ fontWeight: '600', marginTop: 12, marginBottom: 6 }}>NOTES</Text>
          <TextInput value={form.notes ?? ''} onChangeText={(v) => onChange('notes', v)} placeholder="Notes" style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />

          <View style={{ flexDirection: 'row', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
            <Pressable disabled={saving} onPress={onSave} style={{ paddingVertical: 10, paddingHorizontal: 12, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
              <Text style={{ color: '#fff', fontWeight: '700' }}>{saving ? 'Saving…' : 'Save'}</Text>
            </Pressable>
          </View>
        </View>
      )}
    </SafeAreaView>
  )
} 