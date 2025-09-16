import React, { useState } from 'react'
import { Pressable as RNPressable, Text, Modal, View, TextInput } from 'react-native'
import { useRouter } from 'expo-router'
import { gql, useMutation } from '@apollo/client'
import { useAuth } from '@/features/auth/context/AuthContext'
import { useThemeVariant } from '@/theme/ThemeContext'

export default function GlobalFab({ onPress, label }: { onPress?: () => void, label?: string }) {
  const router = useRouter()
  const { session } = useAuth()
  const { toggle, themeId } = useThemeVariant()
  const userId = session?.user?.id || ''
  const [showFab, setShowFab] = useState(false)
  const [showWaterModal, setShowWaterModal] = useState(false)
  const [waterAmount, setWaterAmount] = useState('')

  const CREATE_WATER = gql`
    mutation CreateWaterFab($input: WaterConsumptionCreateInput!) {
      createWaterConsumption(input: $input) { id_ }
    }
  `
  const [createWater] = useMutation(CREATE_WATER, {
    onCompleted: () => {
      setShowWaterModal(false)
      setWaterAmount('')
    },
  })

  return (
    <>
      <RNPressable onPress={onPress || (() => setShowFab(true))} style={{ position: 'absolute', right: 16, bottom: 24, width: 56, height: 56, borderRadius: 28, backgroundColor: '#ffffff', borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)', justifyContent: 'center', alignItems: 'center', elevation: 8, zIndex: 50, shadowColor: '#000', shadowOpacity: 0.25, shadowRadius: 5, shadowOffset: { width: 0, height: 3 } }}>
        <Text style={{ color: '#000', fontSize: 28, marginTop: -2 }}>{label || '＋'}</Text>
      </RNPressable>

      {/* FAB bottom sheet */}
      <Modal visible={showFab} transparent animationType="fade" onRequestClose={() => setShowFab(false)}>
        <RNPressable style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' }} onPress={() => setShowFab(false)}>
          <View style={{ backgroundColor: '#ffffff', padding: 16, borderTopLeftRadius: 16, borderTopRightRadius: 16, borderTopWidth: 1, borderColor: '#e5e7eb', shadowColor: '#000', shadowOpacity: 0.25, shadowRadius: 8, shadowOffset: { width: 0, height: -2 }, elevation: 12 }}>
            <RNPressable onPress={() => { setShowFab(false); router.push('/meals/create?from=/'); }} style={{ paddingVertical: 12, flexDirection: 'row', alignItems: 'center' }}>
              <Text style={{ marginRight: 8 }}>🍽️</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#111827' }}>Create New Meal</Text>
            </RNPressable>
            <View style={{ height: 1, backgroundColor: '#e5e7eb', marginVertical: 4 }} />
            <RNPressable onPress={() => { setShowFab(false); setShowWaterModal(true) }} style={{ paddingVertical: 12, flexDirection: 'row', alignItems: 'center' }}>
              <Text style={{ marginRight: 8 }}>💧</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#111827' }}>Log Water</Text>
            </RNPressable>
            <View style={{ height: 1, backgroundColor: '#e5e7eb', marginVertical: 4 }} />
            <RNPressable onPress={() => { setShowFab(false); router.push('/(app)/workout-create') }} style={{ paddingVertical: 12, flexDirection: 'row', alignItems: 'center' }}>
              <Text style={{ marginRight: 8 }}>🏋️</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#111827' }}>Create Workout</Text>
            </RNPressable>
            <View style={{ height: 1, backgroundColor: '#e5e7eb', marginVertical: 4 }} />
            <RNPressable onPress={() => { setShowFab(false); router.push('/journal-hub') }} style={{ paddingVertical: 12, flexDirection: 'row', alignItems: 'center' }}>
              <Text style={{ marginRight: 8 }}>📝</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#111827' }}>Create Journal</Text>
            </RNPressable>
            <View style={{ height: 1, backgroundColor: '#e5e7eb', marginVertical: 4 }} />
            <RNPressable onPress={() => { toggle(); }} style={{ paddingVertical: 12, flexDirection: 'row', alignItems: 'center' }}>
              <Text style={{ marginRight: 8 }}>🎨</Text>
              <Text style={{ fontSize: 16, fontWeight: '600', color: '#111827' }}>Toggle Theme ({themeId})</Text>
            </RNPressable>
            <View style={{ height: 1, backgroundColor: '#e5e7eb', marginVertical: 4 }} />
            <RNPressable onPress={() => setShowFab(false)} style={{ paddingVertical: 12 }}>
              <Text style={{ fontSize: 16, color: '#ef4444' }}>Cancel</Text>
            </RNPressable>
          </View>
        </RNPressable>
      </Modal>

      {/* Log Water modal */}
      <Modal visible={showWaterModal} transparent animationType="fade" onRequestClose={() => setShowWaterModal(false)}>
        <RNPressable style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'center', alignItems: 'center' }} onPress={() => setShowWaterModal(false)}>
          <View style={{ backgroundColor: '#ffffff', padding: 16, borderRadius: 12, width: '90%', borderWidth: 1, borderColor: '#e5e7eb' }}>
            <Text style={{ fontWeight: '700', fontSize: 16, marginBottom: 10 }}>Log Water</Text>
            <Text style={{ marginBottom: 6, color: '#374151' }}>Amount (oz)</Text>
            <View style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
              <TextInput value={waterAmount} onChangeText={setWaterAmount} placeholder="e.g., 8" keyboardType="numeric" style={{ padding: 12 }} />
            </View>
            <View style={{ flexDirection: 'row', gap: 10, justifyContent: 'flex-end', marginTop: 12 }}>
              <RNPressable onPress={() => setShowWaterModal(false)} style={{ paddingVertical: 10, paddingHorizontal: 12 }}>
                <Text style={{ color: '#666' }}>Cancel</Text>
              </RNPressable>
              <RNPressable onPress={async () => {
                const qty = parseFloat(waterAmount)
                if (!isFinite(qty) || qty <= 0 || !userId) return
                const ml = qty * 29.5735
                await createWater({ variables: { input: { userId, quantity: ml, consumedAt: new Date().toISOString() } } })
              }} style={{ paddingVertical: 10, paddingHorizontal: 12, backgroundColor: '#1d4ed8', borderRadius: 8 }}>
                <Text style={{ color: '#ffffff', fontWeight: '700' }}>Save</Text>
              </RNPressable>
            </View>
          </View>
        </RNPressable>
      </Modal>
    </>
  )
}
