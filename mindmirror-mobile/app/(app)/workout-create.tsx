import React, { useState } from 'react'
import { View, Text, TextInput, Button, Alert } from 'react-native'
import { useRouter } from 'expo-router'
import dayjs from 'dayjs'
import { useCreateAdHocWorkout } from '@/services/api/practices'

export default function WorkoutCreateScreen() {
  const router = useRouter()
  const [title, setTitle] = useState('')
  const [date, setDate] = useState(dayjs().format('YYYY-MM-DD'))
  const [createWorkout, { loading }] = useCreateAdHocWorkout()

  const onSubmit = async () => {
    if (!title) {
      Alert.alert('Title required', 'Please enter a workout title')
      return
    }
    try {
      await createWorkout({ variables: { input: { title, date, prescriptions: [] } } })
      router.back()
    } catch (e: any) {
      Alert.alert('Error', e?.message || 'Failed to create workout')
    }
  }

  return (
    <View style={{ flex: 1, padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: '600' }}>Create Workout</Text>
      <Text>Title</Text>
      <TextInput value={title} onChangeText={setTitle} placeholder="e.g. Push Day" style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
      <Text>Date (YYYY-MM-DD)</Text>
      <TextInput value={date} onChangeText={setDate} placeholder="YYYY-MM-DD" style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 10 }} />
      <Button title={loading ? 'Creating...' : 'Create Workout'} onPress={onSubmit} disabled={loading} />
    </View>
  )
} 