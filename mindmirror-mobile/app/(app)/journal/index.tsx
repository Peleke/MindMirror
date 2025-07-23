import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from "@/components/ui/avatar";
import { Box } from "@/components/ui/box";
import { HStack } from "@/components/ui/hstack";
import { Icon, MenuIcon } from "@/components/ui/icon";
import { Pressable } from "@/components/ui/pressable";
import { SafeAreaView } from "@/components/ui/safe-area-view";
import { ScrollView } from "@/components/ui/scroll-view";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { useNavigation } from '@react-navigation/native';
import { useRouter } from 'expo-router';
import { Heart, Lightbulb } from "lucide-react-native";
import { useState } from 'react';
import { UserGreeting } from '../../../src/components/journal/UserGreeting';
import { AffirmationDisplay } from '../../../src/components/journal/AffirmationDisplay';
import { JournalEntryForm } from '../../../src/components/journal/JournalEntryForm';
import { TransitionOverlay } from '../../../src/components/journal/TransitionOverlay';
import { useJournalFlow } from '../../../src/hooks/useJournalFlow';
import { useToast } from '@/components/ui/toast';
import { Toast, ToastDescription, ToastTitle } from '@/components/ui/toast';
import { useAuth } from '@/features/auth/context/AuthContext';
import { useAffirmation } from '@/hooks/useAffirmation';

function AppBar() {
  const router = useRouter();
  const navigation = useNavigation();

  const handleMenuPress = () => {
    (navigation as any).openDrawer();
  };

  const handleProfilePress = () => {
    router.push('/(app)/profile');
  };

  return (
    <HStack
      className="py-6 px-4 border-b border-border-300 bg-background-0 items-center justify-between"
      space="md"
    >
      <HStack className="items-center" space="sm">
        <Pressable onPress={handleMenuPress}>
          <Icon as={MenuIcon} />
        </Pressable>
        <Text className="text-xl">Journal</Text>
      </HStack>
      
      <Pressable onPress={handleProfilePress}>
        <Avatar className="h-9 w-9">
          <AvatarFallbackText>U</AvatarFallbackText>
          <AvatarImage source={{ uri: "https://i.pravatar.cc/300" }} />
          <AvatarBadge />
        </Avatar>
      </Pressable>
    </HStack>
  );
}

export default function JournalScreen() {
  const router = useRouter();
  const { show } = useToast();
  const { user } = useAuth();
  const { affirmation, isLoading: isAffirmationLoading } = useAffirmation();
  
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

  const userName = user?.user_metadata?.full_name || user?.email || "User";

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar />
        
        <ScrollView
          showsVerticalScrollIndicator={false}
          className="flex-1"
        >
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

          {/* MOVED: Structured Journal Options are now at the top */}
          <VStack className="px-6 pb-6" space="md">
            <HStack className="space-x-4">
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
                    Gratitude
                  </Text>
                </Box>
              </Pressable>
              
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
                    Reflection
                  </Text>
                </Box>
              </Pressable>
            </HStack>
          </VStack>
          
          {/* Main Journal Entry Form */}
          <VStack className="px-6 pb-6" space="md">
            <JournalEntryForm
              onSaveAndChat={handleSaveAndChat}
              onSave={handleSave}
              isLoading={isSubmitting}
              className="bg-background-50 dark:bg-background-100 rounded-lg p-6"
            />
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