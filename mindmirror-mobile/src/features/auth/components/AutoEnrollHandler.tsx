import React, { useEffect, useState } from 'react'
import { useMutation } from '@apollo/client'
import { AUTO_ENROLL } from '@/services/api/habits'
import { useAuth } from '@/features/auth/context/AuthContext'

export function AutoEnrollHandler() {
  const { session } = useAuth()
  const [autoEnrollState, setAutoEnrollState] = useState<'idle'|'success'|'mismatch'|'none'>('idle')
  const [autoEnroll] = useMutation(AUTO_ENROLL)
  const [hasTriedAutoEnroll, setHasTriedAutoEnroll] = useState(false)

  useEffect(() => {
    // Only try auto-enrollment once per session and only if we have a session
    if (session && !hasTriedAutoEnroll) {
      setHasTriedAutoEnroll(true)
      
      console.log('✅ User signed in, attempting auto-enrollment:', session.user?.email)
      
      const performAutoEnroll = async () => {
        try {
          // Prefer GQL gateway autoEnroll so both habits and admark enrollments occur
          const { data } = await autoEnroll({ variables: { campaign: 'uye' } })
          const j = data?.autoEnroll
          if (j?.enrolled) {
            console.log('🎟️ Auto-enrolled via voucher')
            setAutoEnrollState('success')
          } else if (j?.reason === 'email_mismatch') {
            console.log('⚠️ Voucher email mismatch; show voucher entry modal')
            setAutoEnrollState('mismatch')
          } else {
            setAutoEnrollState('none')
          }
        } catch (e) {
          console.log('autoenroll error', e)
          setAutoEnrollState('none')
        }
      }

      performAutoEnroll()
    }
  }, [session, hasTriedAutoEnroll, autoEnroll])

  // Reset auto-enrollment state when session changes
  useEffect(() => {
    if (!session) {
      setHasTriedAutoEnroll(false)
      setAutoEnrollState('idle')
    }
  }, [session])

  return (
    <>
      {autoEnrollState === 'success' && (
        <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, padding: 16, zIndex: 1000 }}>
          <div style={{ backgroundColor: '#10b981', padding: 12, borderRadius: 8 }}>
            <span style={{ color: 'white' }}>You're in! Your voucher has been applied.</span>
            <button onClick={() => setAutoEnrollState('idle')} style={{ marginLeft: 12, color: 'white', textDecorationLine: 'underline' }}>Dismiss</button>
          </div>
        </div>
      )}
      {autoEnrollState === 'mismatch' && (
        <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, padding: 16, zIndex: 1000 }}>
          <div style={{ backgroundColor: '#f59e0b', padding: 12, borderRadius: 8 }}>
            <span style={{ color: 'white' }}>We couldn't auto-apply your voucher. Enter your code here or use Marketplace → Redeem Voucher.</span>
            <button onClick={() => setAutoEnrollState('idle')} style={{ marginLeft: 12, color: 'white', textDecorationLine: 'underline' }}>Dismiss</button>
          </div>
        </div>
      )}
    </>
  )
}
