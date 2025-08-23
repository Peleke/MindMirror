import React, { useMemo, useState } from 'react'
import { SafeAreaView, View, Text, TextInput, Pressable, FlatList, Alert } from 'react-native'
import { gql, useMutation, useQuery } from '@apollo/client'
import { AppBar } from '@/components/common/AppBar'
import { useLocalSearchParams, useRouter } from 'expo-router'

const GET_MEAL = gql`
  query Meal($id: ID!) {
    meal(id: $id) {
      id_
      name
      type
      date
      notes
      mealFoods { id_ quantity servingUnit foodItem { id_ name calories protein carbohydrates fat } }
    }
  }
`

const UPDATE_MEAL = gql`
  mutation UpdateMeal($id: ID!, $input: MealUpdateInput!) {
    updateMeal(id: $id, input: $input) { id_ name notes }
  }
`

const DELETE_MEAL = gql`
  mutation DeleteMeal($id: ID!) { deleteMeal(id: $id) }
`

export default function MealDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const router = useRouter()

  const mealQuery = useQuery(GET_MEAL, { variables: { id } })
  const [updateMeal, { loading: saving }] = useMutation(UPDATE_MEAL)
  const [deleteMeal, { loading: deleting }] = useMutation(DELETE_MEAL, {
    onCompleted: () => router.replace('/meals'),
  })

  const meal = mealQuery.data?.meal
  const [name, setName] = useState<string>(meal?.name ?? '')
  const [notes, setNotes] = useState<string>(meal?.notes ?? '')

  React.useEffect(() => {
    if (meal) {
      setName(meal.name || '')
      setNotes(meal.notes || '')
    }
  }, [meal])

  const onSave = async () => {
    await updateMeal({ variables: { id, input: { name, notes } } })
    mealQuery.refetch()
  }

  const onDelete = async () => {
    Alert.alert('Delete Meal', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Delete', style: 'destructive', onPress: async () => { await deleteMeal({ variables: { id } }) } },
    ])
  }

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <AppBar title="Meal Details" showBackButton onBackPress={() => router.replace('/meals')} />

      {!meal ? (
        <View style={{ padding: 16 }}>
          <Text>Loading…</Text>
        </View>
      ) : (
        <View style={{ padding: 16 }}>
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>MEAL NAME</Text>
          <TextInput value={name} onChangeText={setName} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 12 }} />

          <Text style={{ fontWeight: '600', marginBottom: 6 }}>NOTES</Text>
          <TextInput value={notes} onChangeText={setNotes} multiline style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, minHeight: 80, textAlignVertical: 'top' }} />

          <View style={{ flexDirection: 'row', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
            <Pressable onPress={onDelete} style={{ paddingVertical: 10, paddingHorizontal: 12 }}>
              <Text style={{ color: '#ef4444', fontWeight: '700' }}>{deleting ? 'Deleting…' : 'Delete'}</Text>
            </Pressable>
            <Pressable disabled={saving} onPress={onSave} style={{ paddingVertical: 10, paddingHorizontal: 12, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
              <Text style={{ color: '#fff', fontWeight: '700' }}>{saving ? 'Saving…' : 'Save'}</Text>
            </Pressable>
          </View>

          <View style={{ marginTop: 24 }}>
            <Text style={{ fontWeight: '700', marginBottom: 8 }}>Ingredients</Text>
            <FlatList
              data={meal.mealFoods}
              keyExtractor={(mf) => mf.id_}
              renderItem={({ item }) => (
                <View style={{ paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f1f5f9', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                  <View>
                    <Text style={{ fontWeight: '600' }}>{item.foodItem.name}</Text>
                    <Text style={{ color: '#666' }}>{item.quantity} {item.servingUnit}</Text>
                  </View>
                  <Pressable onPress={() => router.push(`/foods/${item.foodItem.id_}?from=/meals/${id}`)} style={{ padding: 8 }}>
                    <Text style={{ color: '#1d4ed8', fontWeight: '600' }}>Edit</Text>
                  </Pressable>
                </View>
              )}
            />
          </View>
        </View>
      )}
    </SafeAreaView>
  )
} 