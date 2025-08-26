import React, { useCallback, useEffect, useState } from 'react'
import { View, Text, Pressable, ActivityIndicator, Platform } from 'react-native'
import { BarCodeScanner } from 'expo-barcode-scanner'
import * as Haptics from 'expo-haptics'
import { gql, useMutation } from '@apollo/client'
import { useRouter } from 'expo-router'

const IMPORT_OFF_PRODUCT = gql`
  mutation ImportOff($code: String!) {
    importOffProduct(code: $code) {
      id_
      name
      brand
      externalId
    }
  }
`

export default function ScanBarcodeScreen() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  const [scanningEnabled, setScanningEnabled] = useState(true)
  const [importing, setImporting] = useState(false)
  const router = useRouter()
  const [importOff] = useMutation(IMPORT_OFF_PRODUCT)

  useEffect(() => {
    ;(async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync()
      setHasPermission(status === 'granted')
    })()
  }, [])

  const doImport = useCallback(async (code: string) => {
    setImporting(true)
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
      const res = await importOff({ variables: { code } })
      const created = res.data?.importOffProduct
      if (created?.id_) {
        router.replace(`/foods/${created.id_}?from=${encodeURIComponent('/meals/create')}`)
      } else {
        setImporting(false)
        setTimeout(() => setScanningEnabled(true), 800)
      }
    } catch (e) {
      setImporting(false)
      setTimeout(() => setScanningEnabled(true), 1000)
    }
  }, [importOff, router])

  const handleBarCodeScanned = useCallback(async ({ data }: { data: string }) => {
    if (!scanningEnabled || importing) return
    setScanningEnabled(false)
    const code = String(data || '').trim()
    if (!/^[0-9]{8,}$/.test(code)) {
      setTimeout(() => setScanningEnabled(true), 800)
      return
    }
    await doImport(code)
  }, [scanningEnabled, importing, doImport])

  if (hasPermission === null) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 8 }}>Requesting camera permission…</Text>
      </View>
    )
  }

  if (hasPermission === false) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 24 }}>
        <Text style={{ textAlign: 'center', marginBottom: 12 }}>Camera access is required to scan barcodes.</Text>
        <Pressable onPress={async () => {
          const { status } = await BarCodeScanner.requestPermissionsAsync()
          setHasPermission(status === 'granted')
        }} style={{ backgroundColor: '#1d4ed8', borderRadius: 8, paddingVertical: 12, paddingHorizontal: 16 }}>
          <Text style={{ color: '#fff', fontWeight: '700' }}>Grant Permission</Text>
        </Pressable>
      </View>
    )
  }

  return (
    <View style={{ flex: 1, backgroundColor: '#000' }}>
      <BarCodeScanner
        onBarCodeScanned={scanningEnabled ? (handleBarCodeScanned as unknown as any) : undefined}
        style={{ flex: 1 }}
      />

      {/* Overlay */}
      <View pointerEvents="none" style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center' }}>
        <View style={{ width: '70%', height: 220, borderColor: '#22c55e', borderWidth: 2, borderRadius: 12, backgroundColor: 'rgba(0,0,0,0.15)' }} />
        <Text style={{ color: '#fff', marginTop: 12 }}>Align the barcode within the frame</Text>
      </View>

      {/* Controls */}
      <View style={{ position: 'absolute', bottom: 24, left: 16, right: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Pressable onPress={() => router.back()} style={{ paddingVertical: 10, paddingHorizontal: 14, backgroundColor: 'rgba(255,255,255,0.9)', borderRadius: 10 }}>
          <Text style={{ fontWeight: '700' }}>Close</Text>
        </Pressable>
        <Pressable disabled={importing} onPress={() => setScanningEnabled(s => !s)} style={{ paddingVertical: 10, paddingHorizontal: 14, backgroundColor: 'rgba(255,255,255,0.9)', borderRadius: 10 }}>
          <Text style={{ fontWeight: '700' }}>{scanningEnabled ? 'Pause' : 'Resume'}</Text>
        </Pressable>
      </View>

      {importing && (
        <View style={{ position: 'absolute', top: Platform.OS === 'ios' ? 60 : 30, left: 0, right: 0, alignItems: 'center' }}>
          <View style={{ backgroundColor: 'rgba(17,24,39,0.9)', paddingVertical: 8, paddingHorizontal: 12, borderRadius: 8 }}>
            <Text style={{ color: '#fff' }}>Importing…</Text>
          </View>
        </View>
      )}
    </View>
  )
} 