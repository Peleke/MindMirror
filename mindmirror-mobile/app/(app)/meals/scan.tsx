import React from 'react'
import { View, Text, Pressable } from 'react-native'
import { useRouter } from 'expo-router'

export default function ScanFallback() {
  const router = useRouter()
  return (
    <View style={{ flex: 1, padding: 16, alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontSize: 18, fontWeight: '600', marginBottom: 12 }}>Scanner</Text>
      <Text style={{ color: '#6b7280', marginBottom: 12, textAlign: 'center', maxWidth: 420 }}>
        Use the native app to scan barcodes. On web, please create items via search or enter barcodes in native apps.
      </Text>
      <Pressable onPress={() => router.back()} style={{ backgroundColor: '#1d4ed8', borderRadius: 8, paddingVertical: 10, paddingHorizontal: 16 }}>
        <Text style={{ color: '#fff', fontWeight: '700' }}>Close</Text>
      </Pressable>
    </View>
  )
} 