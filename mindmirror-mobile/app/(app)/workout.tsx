import React from 'react'
import { View, Text, Button } from 'react-native'
import { useRouter } from 'expo-router'
import { Fab, FabLabel } from '@/components/ui/fab'

export default function WorkoutsScreen() {
  const router = useRouter()
  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 24, fontWeight: '600', marginBottom: 12 }}>Workouts</Text>
      <Button title="Create Workout" onPress={() => router.push('/(app)/workout-create')} />
      <Fab placement="bottom right" onPress={() => router.push('/(app)/workout-create')}>
        <FabLabel>Create Workout</FabLabel>
      </Fab>
    </View>
  )
} 