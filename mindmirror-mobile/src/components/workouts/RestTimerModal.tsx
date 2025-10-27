import React, { useEffect, useRef } from 'react'
import { Modal, Pressable, View, Animated } from 'react-native'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Button, ButtonText } from '@/components/ui/button'
import Svg, { Circle } from 'react-native-svg'

interface RestTimerModalProps {
  visible: boolean
  initialSeconds: number
  onComplete: () => void
  onSkip: () => void
}

const AnimatedCircle = Animated.createAnimatedComponent(Circle)

export const RestTimerModal: React.FC<RestTimerModalProps> = ({
  visible,
  initialSeconds,
  onComplete,
  onSkip,
}) => {
  const [seconds, setSeconds] = React.useState(initialSeconds)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const progressAnim = useRef(new Animated.Value(1)).current
  const initialSecondsRef = useRef(initialSeconds)
  const onCompleteRef = useRef(onComplete)

  // Keep refs up to date
  useEffect(() => {
    initialSecondsRef.current = initialSeconds
    onCompleteRef.current = onComplete
  }, [initialSeconds, onComplete])

  // Reset seconds and progress when modal opens
  useEffect(() => {
    if (visible) {
      console.log('RestTimerModal opening with initialSeconds:', initialSeconds)
      setSeconds(initialSeconds)
      progressAnim.setValue(1)
    }
  }, [visible, initialSeconds, progressAnim])

  // Separate effect for the countdown timer
  useEffect(() => {
    if (!visible) {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      return
    }

    console.log('Starting countdown timer, initial seconds:', initialSecondsRef.current)
    // Start the timer when modal becomes visible
    timerRef.current = setInterval(() => {
      setSeconds((prevSeconds) => {
        const newSeconds = Math.max(0, prevSeconds - 1)
        console.log('Timer tick:', prevSeconds, '->', newSeconds)

        // Update progress animation based on initial value
        if (initialSecondsRef.current > 0) {
          const progress = newSeconds / initialSecondsRef.current
          Animated.timing(progressAnim, {
            toValue: progress,
            duration: 1000,
            useNativeDriver: false,
          }).start()
        }

        // Auto-complete when timer hits 0
        if (newSeconds === 0) {
          console.log('Timer reached 0, auto-completing')
          if (timerRef.current) {
            clearInterval(timerRef.current)
            timerRef.current = null
          }
          setTimeout(() => {
            onCompleteRef.current()
          }, 500)
        }

        return newSeconds
      })
    }, 1000)

    return () => {
      console.log('Cleaning up timer')
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [visible, progressAnim])

  const handleAddTime = (amount: number) => {
    setSeconds((s) => s + amount)
  }

  const formatTime = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60)
    const secs = totalSeconds % 60
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }

  // Circle parameters
  const size = 240
  const strokeWidth = 12
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius

  // Animated stroke dash offset
  const strokeDashoffset = progressAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [circumference, 0],
  })

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={() => {
        console.log('🔵 Modal onRequestClose triggered')
        onSkip()
      }}
    >
      <View
        style={{
          flex: 1,
          backgroundColor: 'rgba(0, 0, 0, 0.6)',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Pressable
          style={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
          }}
          onPress={() => {}} // Prevent dismiss on background tap
        />
        <Box className="bg-white dark:bg-background-0 rounded-3xl p-8 m-6" style={{ maxWidth: 400 }}>
          <VStack space="xl" className="items-center">
            <Text className="text-2xl font-bold text-typography-900 dark:text-white">Rest Timer</Text>

            {/* Countdown Ring */}
            <Box className="items-center justify-center" style={{ width: size, height: size }}>
              <Svg width={size} height={size}>
                {/* Background circle */}
                <Circle
                  cx={size / 2}
                  cy={size / 2}
                  r={radius}
                  stroke="#E5E7EB"
                  strokeWidth={strokeWidth}
                  fill="none"
                />
                {/* Progress circle */}
                <AnimatedCircle
                  cx={size / 2}
                  cy={size / 2}
                  r={radius}
                  stroke="#10B981"
                  strokeWidth={strokeWidth}
                  fill="none"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  rotation="-90"
                  origin={`${size / 2}, ${size / 2}`}
                />
              </Svg>
              {/* Time display in center */}
              <Box
                style={{
                  position: 'absolute',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Text className="text-5xl font-bold text-typography-900 dark:text-white">
                  {formatTime(seconds)}
                </Text>
              </Box>
            </Box>

            {/* Action buttons */}
            <HStack space="md" className="w-full">
              <Button
                variant="outline"
                className="flex-1 border-border-300"
                onPress={() => handleAddTime(-15)}
                isDisabled={seconds <= 15}
              >
                <ButtonText>-15s</ButtonText>
              </Button>
              <Button
                variant="outline"
                className="flex-1 border-border-300"
                onPress={() => handleAddTime(15)}
              >
                <ButtonText>+15s</ButtonText>
              </Button>
            </HStack>

            <Button
              variant="solid"
              className="w-full bg-indigo-600"
              onPress={() => {
                console.log('🔴 Skip Rest button clicked')
                onSkip()
              }}
            >
              <ButtonText className="text-white">Skip Rest</ButtonText>
            </Button>
          </VStack>
        </Box>
      </View>
    </Modal>
  )
}
