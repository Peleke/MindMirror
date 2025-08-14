import { Box } from "@/components/ui/box";
import { HStack } from "@/components/ui/hstack";
import { Icon } from "@/components/ui/icon";
import { Pressable } from "@/components/ui/pressable";
import { SafeAreaView } from "@/components/ui/safe-area-view";
import { ScrollView } from "@/components/ui/scroll-view";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { useRouter } from 'expo-router';
import { Heart, Lightbulb } from "lucide-react-native";
import { useState } from 'react';
import { ActivityIndicator } from 'react-native';
import { UserGreeting } from '../../../src/components/journal/UserGreeting';
import { AffirmationDisplay } from '../../../src/components/journal/AffirmationDisplay';
import { JournalEntryForm } from '../../../src/components/journal/JournalEntryForm';
import { TransitionOverlay } from '../../../src/components/journal/TransitionOverlay';
import { useJournalFlow } from '../../../src/hooks/useJournalFlow';
import { useToast } from '@/components/ui/toast';
import { Toast, ToastDescription, ToastTitle } from '@/components/ui/toast';
import { useAuth } from '@/features/auth/context/AuthContext';
import { useAffirmation } from '@/hooks/useAffirmation';
import { useJournalStatus } from '@/hooks/useJournalStatus';
import { CompletedJournalCard } from '@/components/journal/CompletedJournalCard';
import { AppBar } from '@/components/common/AppBar';
import DailyTasksList from '@/components/habits/DailyTasksList'
import { getUserDisplayName } from '@/utils/user';

const LoadingJournalCard = ({ type }: { type: 'Gratitude' | 'Reflection' }) => {
  const isGratitude = type === 'Gratitude';
  const bgColor = isGratitude ? 'bg-blue-50 dark:bg-blue-950' : 'bg-indigo-50 dark:bg-indigo-950';
  const borderColor = isGratitude ? 'border-blue-200 dark:border-blue-800' : 'border-indigo-200 dark:border-indigo-800';
  const textColor = isGratitude ? 'text-blue-900 dark:text-blue-100' : 'text-indigo-900 dark:text-indigo-100';
  const spinnerColor = isGratitude ? '#2563eb' : '#4f46e5';
  
  return (
    <Box className={`flex-1 p-4 ${bgColor} rounded-lg border ${borderColor} items-center`}>
      <ActivityIndicator 
        size="small" 
        color={spinnerColor} 
        style={{ marginBottom: 8 }}
      />
      <Text className={`text-sm font-medium ${textColor} text-center`}>
        Loading {type}...
      </Text>
    </Box>
  );
};

export default function JournalScreen() {
  const router = useRouter();
  const { show } = useToast();
  const { user } = useAuth();
  const { affirmation, isLoading: isAffirmationLoading } = useAffirmation();
  const { hasCompletedGratitude, hasCompletedReflection, isLoading: isStatusLoading } = useJournalStatus();
  
  const {
    submitEntry,
    isTransitioning: hookIsTransitioning,
    isSubmitting,
    error,
  } = useJournalFlow();

  const handleSaveAndChat = async (entry: string) => {
    // Call submitEntry with the 'andChat' flag
    await submitEntry(entry, { andChat: true });
  };

  const handleSave = async (entry: string) => {
    // Call submitEntry without the 'andChat' flag
    const { success } = await submitEntry(entry, { andChat: false });
    if (success) {
      // Use the 'show' function with the correct component structure for the toast.
      show({
        placement: "top",
        render: ({ id }) => {
          const toastId = "toast-" + id;
          return (
            <Toast nativeID={toastId} action="success" variant="solid">
              <VStack space="xs">
                <ToastTitle>Entry Saved</ToastTitle>
                <ToastDescription>
                  Your journal entry has been saved successfully.
                </ToastDescription>
              </VStack>
            </Toast>
          );
        },
      });
      // Here you might want to clear the form, which would require
      // lifting the form's state up to this screen component.
      // For now, we'll leave it as is.
    }
  };

  const handleGratitudePress = () => {
    router.push('/journal/gratitude');
  };

  const handleReflectionPress = () => {
    router.push('/journal/reflection');
  };

  const userName = getUserDisplayName(user);

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Journal" />
        
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto">
          {/* Header Section */}
          <VStack className="px-6 py-6" space="md">
            <UserGreeting 
              userName={userName} 
              className="text-2xl font-semibold text-typography-900 dark:text-white"
            />
            
            <Text className="text-lg font-semibold text-typography-900 dark:text-white pt-4">
              From your journals...
            </Text>
            <AffirmationDisplay 
              affirmation={isAffirmationLoading ? "Loading..." : affirmation}
            />
          </VStack>

          {/* Structured Journal Options */}
          <VStack className="px-6 pb-6" space="md">
            <HStack className="space-x-4">
              {isStatusLoading ? (
                <LoadingJournalCard type="Gratitude" />
              ) : hasCompletedGratitude ? (
                <CompletedJournalCard journalType="Gratitude" />
              ) : (
                <Pressable
                  onPress={handleGratitudePress}
                  className="flex-1"
                >
                  <Box className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800 items-center">
                    <Icon 
                      as={Heart}
                      size="lg"
                      className="text-blue-600 dark:text-blue-400 mb-2"
                    />
                    <Text className="text-sm font-medium text-blue-900 dark:text-blue-100 text-center">
                      Morning Gratitude
                    </Text>
                  </Box>
                </Pressable>
              )}
              
              {isStatusLoading ? (
                <LoadingJournalCard type="Reflection" />
              ) : hasCompletedReflection ? (
                <CompletedJournalCard journalType="Reflection" />
              ) : (
                <Pressable
                  onPress={handleReflectionPress}
                  className="flex-1"
                >
                  <Box className="p-4 bg-indigo-50 dark:bg-indigo-950 rounded-lg border border-indigo-200 dark:border-indigo-800 items-center">
                    <Icon 
                      as={Lightbulb}
                      size="lg"
                      className="text-indigo-600 dark:text-indigo-400 mb-2"
                    />
                    <Text className="text-sm font-medium text-indigo-900 dark:text-indigo-100 text-center">
                      Evening Reflection
                    </Text>
                  </Box>
                </Pressable>
              )}
            </HStack>
          </VStack>
          
          {/* Divider */}
          <Box className="h-px bg-border-200 dark:bg-border-700 mx-6" />

          {/* Today's Tasks */}
          <VStack className="px-6 py-6" space="md">
            <Text className="text-lg font-semibold text-typography-900 dark:text-white">Today</Text>
            <DailyTasksList />
          </VStack>
          </VStack>
          
          {/* REMOVED: Old structured journal section */}
          
        </ScrollView>
        
        {/* Transition Overlay */}
        <TransitionOverlay 
          isVisible={hookIsTransitioning}
          // Add the required onComplete prop back with an empty function.
          onComplete={() => {}}
          className="absolute inset-0"
        />
      </VStack>
    </SafeAreaView>
  );
} 