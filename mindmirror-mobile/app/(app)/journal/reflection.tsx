import { Box } from '@/components/ui/box'
import { Button, ButtonText } from '@/components/ui/button'
import { Heading } from '@/components/ui/heading'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { ScrollView } from '@/components/ui/scroll-view'
import { Slider, SliderFilledTrack, SliderThumb, SliderTrack } from '@/components/ui/slider'
import { Text } from '@/components/ui/text'
import { Textarea, TextareaInput } from '@/components/ui/textarea'
import { VStack } from '@/components/ui/vstack'
import { CREATE_REFLECTION_JOURNAL_ENTRY } from '@/services/api/mutations'
import { JOURNAL_ENTRY_EXISTS_TODAY, GET_JOURNAL_ENTRIES } from '@/services/api/queries'
import { useMutation, useQuery } from '@apollo/client'
import { useRouter } from 'expo-router'
import { useState } from 'react'
import { Alert } from 'react-native'
import { AppBar } from '@/components/common/AppBar'



export default function ReflectionJournalScreen() {
  const [wins, setWins] = useState('')
  const [improvements, setImprovements] = useState('')
  const [mood, setMood] = useState(5)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const router = useRouter()



  // Create reflection entry mutation
  const [createEntry, { loading: creating, error }] = useMutation(CREATE_REFLECTION_JOURNAL_ENTRY, {
    refetchQueries: [
      { query: GET_JOURNAL_ENTRIES },
      { query: JOURNAL_ENTRY_EXISTS_TODAY, variables: { entryType: 'REFLECTION' } }
    ],
    onCompleted: () => {
      setIsSubmitted(true);
      setSubmitError(null);
    },
    onError: (error) => {
      setSubmitError(`GraphQL Error: ${error.message}`);
    }
  });

  const getMoodText = (mood: number) => {
    if (mood >= 8) return 'Excellent';
    if (mood >= 7) return 'Great';
    if (mood >= 6) return 'Good';
    if (mood >= 5) return 'Okay';
    if (mood >= 4) return 'Meh';
    if (mood >= 3) return 'Not great';
    return 'Struggling';
  };

  const handleSubmit = async () => {
    // Validation
    if (!wins.trim()) {
      setSubmitError('Please fill in your wins for today');
      return;
    }
    if (!improvements.trim()) {
      setSubmitError('Please fill in areas for improvement');
      return;
    }

    // Prepare data matching GraphQL schema
    const inputData = {
      wins: [wins.trim()],
      improvements: [improvements.trim()],
      mood: getMoodText(mood)
    };

    try {
      setSubmitError(null);
      await createEntry({
        variables: {
          input: inputData
        }
      });
    } catch (err: any) {
      setSubmitError(`Submission failed: ${err.message}`);
    }
  };

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Reflection Journal" showBackButton />
        
        <ScrollView
          showsVerticalScrollIndicator={false}
          className="flex-1"
        >
          {/* Success State */}
          {isSubmitted && (
            <VStack className="px-6 py-6" space="md">
              <Box className="p-6 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-700">
                <Text className="text-green-700 dark:text-green-300 text-center font-semibold mb-2">
                  Reflection saved!
                </Text>
                <Text className="text-green-600 dark:text-green-400 text-center text-sm mb-4">
                  Your thoughts have been recorded. Great job on another day of growth.
                </Text>
                <Button
                  onPress={() => router.push('/(app)')}
                  className="mt-4"
                >
                  <ButtonText>Go to Home</ButtonText>
                </Button>
              </Box>
            </VStack>
          )}

          {/* Main Form - Only show if not submitted */}
          {!isSubmitted && (
            <>
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
                      onValueChange={(values: number[]) => setMood(values[0] ?? 5)}
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
                
                {(submitError || error) && (
                  <Box className="p-4 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-700">
                    <Text className="text-red-700 dark:text-red-300 text-sm">
                      {submitError || error?.message}
                    </Text>
                  </Box>
                )}

                <Button
                  onPress={handleSubmit}
                  disabled={creating}
                  className="mt-4"
                >
                  <ButtonText>
                    {creating ? 'Saving...' : 'Save Entry'}
                  </ButtonText>
                </Button>
              </VStack>
            </Box>
          </VStack>
            </>
          )}
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 