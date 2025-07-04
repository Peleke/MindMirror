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
import { Text } from '@/components/ui/text'
import { Textarea, TextareaInput } from '@/components/ui/textarea'
import { VStack } from '@/components/ui/vstack'
import { CREATE_FREEFORM_JOURNAL_ENTRY } from '@/services/api/mutations'
import { JOURNAL_ENTRY_EXISTS_TODAY, GET_JOURNAL_ENTRIES } from '@/services/api/queries'
import { useMutation, useQuery } from '@apollo/client'
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
        <Text className="text-xl">Freeform Writing</Text>
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

export default function FreeformJournalScreen() {
  const [content, setContent] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const router = useRouter()

  // Check if entry exists for today (optional for freeform since multiple entries are allowed)
  const { data: existsData, loading: existsLoading } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'freeform' }
  });

  // Create freeform entry mutation
  const [createEntry, { loading: creating, error }] = useMutation(CREATE_FREEFORM_JOURNAL_ENTRY, {
    refetchQueries: [{ query: GET_JOURNAL_ENTRIES }],
    onCompleted: () => {
      setIsSubmitted(true);
      setSubmitError(null);
    },
    onError: (error) => {
      setSubmitError(`GraphQL Error: ${error.message}`);
    }
  });

  const handleSubmit = async () => {
    if (!content.trim()) {
      setSubmitError('Please write something in your journal');
      return;
    }

    try {
      setSubmitError(null);
      await createEntry({
        variables: {
          input: { content: content.trim() }
        }
      });
    } catch (err: any) {
      setSubmitError(`Submission failed: ${err.message}`);
    }
  };

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar />
        
        <ScrollView
          showsVerticalScrollIndicator={false}
          className="flex-1"
        >
          {/* Success State */}
          {isSubmitted && (
            <VStack className="px-6 py-6" space="md">
              <Box className="p-6 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-700">
                <Text className="text-green-700 dark:text-green-300 text-center font-semibold mb-2">
                  Entry Saved!
                </Text>
                <Text className="text-green-600 dark:text-green-400 text-center text-sm mb-4">
                  Your thoughts have been recorded.
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
                  Express your thoughts freely
                </Heading>
                <Text className="text-typography-600 dark:text-gray-200">
                  Write whatever comes to mind
                </Text>
              </VStack>
          
          {/* Content */}
          <VStack className="px-6 pb-6" space="md">
            <Box className="p-6 bg-purple-50 dark:bg-purple-950 rounded-lg border border-border-200 dark:border-border-700">
              <VStack space="md">
                <VStack space="xs">
                  <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                    Your Thoughts
                  </Text>
                  <Textarea className="bg-white dark:bg-gray-100 flex-1">
                    <TextareaInput
                      placeholder="Write whatever comes to mind..."
                      value={content}
                      onChangeText={setContent}
                      numberOfLines={12}
                      textAlignVertical="top"
                      style={{ flex: 1, minHeight: 500 }}
                    />
                  </Textarea>
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
                  disabled={creating || existsLoading}
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