import React, { useMemo, useState } from 'react'
import { SafeAreaView, View, Text, TextInput, Pressable, Platform } from 'react-native'
import { gql, useMutation } from '@apollo/client'
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

const mealTypes = ['BREAKFAST','LUNCH','DINNER','SNACK'] as const

type MealType = typeof mealTypes[number]

export default function CreateMealScreen() {
  const [name, setName] = useState('')
  const [notes, setNotes] = useState('')
  const [mealType, setMealType] = useState<MealType>('BREAKFAST')
  const [dt, setDt] = useState<Date>(new Date())
  const router = useRouter()
  const { session } = useAuth()
  const userId = session?.user?.id || ''

  const [createMeal, { loading }] = useMutation(CREATE_MEAL)

  const input = useMemo(() => ({
    user_id: userId,
    name,
    type: mealType,
    date: dt.toISOString(),
    notes: notes || null,
    meal_foods_data: [],
  }), [userId, name, mealType, dt, notes])

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
          <Text style={{ fontWeight: '600', marginBottom: 6 }}>NOTES</Text>
          <TextInput
            value={notes}
            onChangeText={setNotes}
            placeholder="Add notes..."
            multiline
            style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, minHeight: 80, textAlignVertical: 'top' }}
          />
        </View>

        <Pressable disabled={!canSubmit || loading} onPress={onSubmit} style={{ marginTop: 12, backgroundColor: canSubmit ? '#1d4ed8' : '#93c5fd', paddingVertical: 14, borderRadius: 10, alignItems: 'center' }}>
          <Text style={{ color: '#fff', fontWeight: '700' }}>{loading ? 'Creating…' : 'CREATE MEAL'}</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  )
} 