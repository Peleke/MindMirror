import React, { useCallback, useState } from 'react'
import { View, Text, Pressable, ActivityIndicator, Platform } from 'react-native'
import { CameraView, useCameraPermissions } from 'expo-camera'
import * as Haptics from 'expo-haptics'
import { gql, useMutation } from '@apollo/client'
import { useRouter, useLocalSearchParams } from 'expo-router'

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
  const params = useLocalSearchParams<{ from?: string }>()
  const [permission, requestPermission] = useCameraPermissions()
  const [scanningEnabled, setScanningEnabled] = useState(true)
  const [importing, setImporting] = useState(false)
  const [toast, setToast] = useState<{ msg: string; type: 'error' | 'success' } | null>(null)
  const router = useRouter()
  const [importOff] = useMutation(IMPORT_OFF_PRODUCT)

  const doImport = useCallback(async (code: string) => {
    setImporting(true)
    try {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
      const res = await importOff({ variables: { code } })
      const created = res.data?.importOffProduct
      if (created?.id_) {
        // Return directly to the create modal and preselect the imported item
        router.replace(`/meals/create?openFoodModal=1&importAddId=${encodeURIComponent(created.id_)}`)
      } else {
        setImporting(false)
        setTimeout(() => setScanningEnabled(true), 800)
        setToast({ msg: 'No product found for this barcode', type: 'error' })
        setTimeout(() => setToast(null), 2000)
      }
    } catch (e) {
      setImporting(false)
      setTimeout(() => setScanningEnabled(true), 1000)
      setToast({ msg: 'Import failed. Check network and try again.', type: 'error' })
      setTimeout(() => setToast(null), 2200)
    }
  }, [importOff, router])

  const handleBarCodeScanned = useCallback(async (event: any) => {
    if (!scanningEnabled || importing) return
    setScanningEnabled(false)
    const first = Array.isArray(event?.barcodes) && event.barcodes.length > 0 ? event.barcodes[0] : null
    const val = first?.rawValue || first?.data || event?.data || event?.rawValue || ''
    const code = String(val).trim()
    if (!/^[0-9]{8,}$/.test(code)) {
      setTimeout(() => setScanningEnabled(true), 800)
      return
    }
    await doImport(code)
  }, [scanningEnabled, importing, doImport])

  if (!permission) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 8 }}>Initializing…</Text>
      </View>
    )
  }

  if (!permission.granted) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 24 }}>
        <Text style={{ textAlign: 'center', marginBottom: 12 }}>Camera access is required to scan barcodes.</Text>
        <Pressable onPress={requestPermission} style={{ backgroundColor: '#1d4ed8', borderRadius: 8, paddingVertical: 12, paddingHorizontal: 16 }}>
          <Text style={{ color: '#fff', fontWeight: '700' }}>Grant Permission</Text>
        </Pressable>
      </View>
    )
  }

  return (
    <View style={{ flex: 1, backgroundColor: '#000' }}>
      <CameraView
        style={{ flex: 1 }}
        facing="back"
        barcodeScannerSettings={{
          barcodeTypes: ['ean13', 'ean8', 'upc_e', 'upc_a', 'code128', 'code39', 'code93', 'itf14', 'qr'],
        }}
        onBarcodeScanned={scanningEnabled ? handleBarCodeScanned : undefined}
      />

      {toast && (
        <View style={{ position: 'absolute', top: Platform.OS === 'ios' ? 60 : 30, left: 16, right: 16, alignItems: 'center' }}>
          <View style={{ backgroundColor: toast.type === 'error' ? '#ef4444' : '#16a34a', paddingVertical: 8, paddingHorizontal: 12, borderRadius: 8 }}>
            <Text style={{ color: '#fff', fontWeight: '700' }}>{toast.msg}</Text>
          </View>
        </View>
      )}

      {/* Overlay */}
      <View pointerEvents="none" style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center' }}>
        <View style={{ width: '70%', height: 220, borderColor: '#22c55e', borderWidth: 2, borderRadius: 12, backgroundColor: 'rgba(0,0,0,0.15)' }} />
        <Text style={{ color: '#fff', marginTop: 12 }}>Align the barcode within the frame</Text>
      </View>

      {/* Controls */}
      <View style={{ position: 'absolute', bottom: 24, left: 16, right: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Pressable onPress={() => {
          const from = typeof params?.from === 'string' && params.from ? String(params.from) : '/meals/create?openFoodModal=1'
          router.replace(from)
        }} style={{ paddingVertical: 10, paddingHorizontal: 14, backgroundColor: 'rgba(255,255,255,0.9)', borderRadius: 10 }}>
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