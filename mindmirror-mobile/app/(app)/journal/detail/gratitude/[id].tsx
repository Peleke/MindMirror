import { SafeAreaView } from '@/components/ui/safe-area-view';
import { VStack } from '@/components/ui/vstack';
import { ScrollView } from '@/components/ui/scroll-view';
import { Heading } from '@/components/ui/heading';
import { Text } from '@/components/ui/text';
import { Box } from '@/components/ui/box';
import { Icon } from '@/components/ui/icon';
import { AppBar } from '@/components/common/AppBar';
import { ReadOnlyField } from '@/components/journal/ReadOnlyField';
import { MoodDisplay } from '@/components/journal/MoodDisplay';
import { DiscussMemoryButton } from '@/components/journal/DiscussMemoryButton';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useQuery } from '@apollo/client';
import { GET_JOURNAL_ENTRY } from '@/services/api/queries';
import { AlertCircle } from 'lucide-react-native';
import { ActivityIndicator } from 'react-native';

interface GratitudePayload {
  gratefulFor: string[];
  excitedAbout: string[];
  focus: string;
  affirmation: string;
  mood?: string | null;
}

interface GratitudeJournalEntry {
  id: string;
  createdAt: string;
  payload: GratitudePayload;
}

export default function GratitudeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  
  const { data, loading, error } = useQuery(GET_JOURNAL_ENTRY, {
    variables: { entryId: id },
    errorPolicy: 'all',
  });

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDiscussMemory = () => {
    // No-op for now - future chat integration
    console.log('Discuss memory pressed for entry:', id);
  };

  const handleBackPress = () => {
    router.push('/(app)/archive');
  };

  if (loading) {
    return (
      <SafeAreaView className="h-full w-full">
        <AppBar title="Loading..." showBackButton />
        <VStack className="h-full items-center justify-center">
          <ActivityIndicator size="large" color="#2563eb" />
          <Text className="mt-4 text-typography-600">Loading entry...</Text>
        </VStack>
      </SafeAreaView>
    );
  }

  if (error || !data?.journalEntry) {
    return (
      <SafeAreaView className="h-full w-full">
        <AppBar title="Error" showBackButton />
        <VStack className="h-full items-center justify-center px-6">
          <Icon as={AlertCircle} size="xl" className="text-red-500 mb-4" />
          <Text className="text-lg font-semibold text-red-600 mb-2">
            Failed to load entry
          </Text>
          <Text className="text-center text-typography-600">
            This entry may have been deleted or you may not have permission to view it.
          </Text>
        </VStack>
      </SafeAreaView>
    );
  }

  const entry = data.journalEntry as GratitudeJournalEntry;

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Gratitude Entry" showBackButton onBackPress={handleBackPress} />
        
        <ScrollView className="flex-1">
          {/* Header with date */}
          <VStack className="px-6 py-6" space="xs">
            <Heading size="2xl" className="font-roboto text-typography-900 dark:text-white">
              Your Gratitude
            </Heading>
            <Text className="text-typography-600 dark:text-gray-200">
              {formatDate(entry.createdAt)}
            </Text>
          </VStack>

          {/* Content */}
          <VStack className="px-6 pb-6" space="md">
            <Box className="p-6 bg-blue-50 dark:bg-blue-950 rounded-lg border border-border-200 dark:border-border-700">
              <VStack space="md">
                <ReadOnlyField
                  label="I am grateful for..."
                  value={entry.payload.gratefulFor.join('\n')}
                  numberOfLines={3}
                />
                
                <ReadOnlyField
                  label="I am excited about..."
                  value={entry.payload.excitedAbout.join('\n')}
                  numberOfLines={3}
                />
                
                <ReadOnlyField
                  label="My focus for today..."
                  value={entry.payload.focus}
                  numberOfLines={2}
                />
                
                <ReadOnlyField
                  label="Daily affirmation..."
                  value={entry.payload.affirmation}
                  numberOfLines={2}
                />
                
                {entry.payload.mood && (
                  <MoodDisplay mood={parseInt(entry.payload.mood)} />
                )}
              </VStack>
            </Box>
            
            <DiscussMemoryButton onPress={handleDiscussMemory} />
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  );
} 