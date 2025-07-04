import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from '@/components/ui/avatar'
import { Box } from '@/components/ui/box'
import { Button, ButtonText } from '@/components/ui/button'
import { Heading } from '@/components/ui/heading'
import { HStack } from '@/components/ui/hstack'
import { ChevronLeftIcon, Icon } from '@/components/ui/icon'
import { Pressable } from '@/components/ui/pressable'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { ScrollView } from '@/components/ui/scroll-view'
import { Slider, SliderFilledTrack, SliderThumb, SliderTrack } from '@/components/ui/slider'
import { Text } from '@/components/ui/text'
import { Textarea, TextareaInput } from '@/components/ui/textarea'
import { VStack } from '@/components/ui/vstack'
import { useNavigation } from '@react-navigation/native'
import { useRouter } from 'expo-router'
import { useState } from 'react'
import { Alert } from 'react-native'

function AppBar() {
  const router = useRouter()
  const navigation = useNavigation()

  const handleBackPress = () => {
    router.back()
  }

  const handleProfilePress = () => {
    router.push('/(app)/profile')
  }

  return (
    <HStack
      className="py-6 px-4 border-b border-border-300 bg-background-0 items-center justify-between"
      space="md"
    >
      <HStack className="items-center" space="sm">
        <Pressable onPress={handleBackPress}>
          <Icon as={ChevronLeftIcon} />
        </Pressable>
        <Text className="text-xl">Daily Reflection</Text>
      </HStack>
      
      <Pressable onPress={handleProfilePress}>
        <Avatar className="h-9 w-9">
          <AvatarFallbackText>U</AvatarFallbackText>
          <AvatarImage source={{ uri: 'https://i.pravatar.cc/300' }} />
          <AvatarBadge />
        </Avatar>
      </Pressable>
    </HStack>
  )
}

export default function ReflectionJournalScreen() {
  const [wins, setWins] = useState('')
  const [improvements, setImprovements] = useState('')
  const [mood, setMood] = useState(5)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async () => {
    if (!wins.trim()) {
      Alert.alert('Error', 'Please fill in your wins for today')
      return
    }

    setLoading(true)
    try {
      // TODO: Implement GraphQL mutation to save reflection journal entry
      console.log('Saving reflection entry:', { wins, improvements, mood })
      
      Alert.alert(
        'Success',
        'Your reflection entry has been saved!',
        [{ text: 'OK', onPress: () => router.back() }]
      )
    } catch (error) {
      Alert.alert('Error', 'Failed to save your entry')
    } finally {
      setLoading(false)
    }
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar />
        
        <ScrollView
          showsVerticalScrollIndicator={false}
          className="flex-1"
        >
          {/* Header */}
          <VStack className="px-6 py-6" space="xs">
            <Heading size="2xl" className="font-roboto text-typography-900 dark:text-white">
              Look back on your day
            </Heading>
            <Text className="text-typography-600 dark:text-gray-200">
              Reflect on your experiences and insights
            </Text>
          </VStack>
          
          {/* Content */}
          <VStack className="px-6 pb-6" space="md">
            <Box className="p-6 bg-indigo-50 dark:bg-indigo-950 rounded-lg border border-border-200 dark:border-border-700">
              <VStack space="md">
                <VStack space="xs">
                  <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                    Today's Wins
                  </Text>
                  <Textarea className="bg-white dark:bg-gray-100">
                    <TextareaInput
                      placeholder="What went well today?"
                      value={wins}
                      onChangeText={setWins}
                      numberOfLines={4}
                    />
                  </Textarea>
                </VStack>
                
                <VStack space="xs">
                  <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                    Areas for Improvement
                  </Text>
                  <Textarea className="bg-white dark:bg-gray-100">
                    <TextareaInput
                      placeholder="What could you improve on?"
                      value={improvements}
                      onChangeText={setImprovements}
                      numberOfLines={4}
                    />
                  </Textarea>
                </VStack>
                
                <VStack space="xs">
                  <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                    How are you feeling? (1-10)
                  </Text>
                  <VStack space="sm" className="py-2">
                    <HStack className="justify-between items-center">
                      <Text className="text-xs text-typography-500 dark:text-gray-400">1</Text>
                      <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                        {mood}
                      </Text>
                      <Text className="text-xs text-typography-500 dark:text-gray-400">10</Text>
                    </HStack>
                    <Slider
                      value={[mood]}
                      onValueChange={(values) => setMood(values[0])}
                      minValue={1}
                      maxValue={10}
                      step={1}
                      size="md"
                    >
                      <SliderTrack>
                        <SliderFilledTrack />
                      </SliderTrack>
                      <SliderThumb />
                    </Slider>
                  </VStack>
                </VStack>
                
                <Button
                  onPress={handleSubmit}
                  disabled={loading}
                  className="mt-4"
                >
                  <ButtonText>
                    {loading ? 'Saving...' : 'Save Entry'}
                  </ButtonText>
                </Button>
              </VStack>
            </Box>
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 