import { Box } from "@/components/ui/box"
import { Button, ButtonText } from "@/components/ui/button"
import { Heading } from "@/components/ui/heading"
import { HStack } from "@/components/ui/hstack"
import { Icon } from "@/components/ui/icon"
import { Pressable } from "@/components/ui/pressable"
import { SafeAreaView } from "@/components/ui/safe-area-view"
import { ScrollView } from "@/components/ui/scroll-view"
import { Text } from "@/components/ui/text"
import { VStack } from "@/components/ui/vstack"
import { useRouter } from 'expo-router'
import { Heart, Lightbulb, PenTool } from "lucide-react-native"
import { AppBar } from '@/components/common/AppBar'
import GlobalFab from '@/components/common/GlobalFab'


const JournalCard = ({ title, description, icon, onPress, testID, iconColor }: {
  title: string;
  description: string;
  icon: any;
  onPress: () => void;
  testID: string;
  iconColor: string;
}) => (
    <Pressable
      onPress={onPress}
      className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-6 rounded-lg shadow-md w-full"
      testID={testID}
    >
      <HStack space="md" className="items-center">
        <Icon as={icon} size="xl" className={iconColor} />
        <VStack>
          <Heading size="md" className="text-blue-900 dark:text-blue-100">{title}</Heading>
          <Text size="sm" className="text-blue-700 dark:text-blue-300 mt-1">
            {description}
          </Text>
        </VStack>
      </HStack>
    </Pressable>
  );
  

export default function JournalHubScreen() {
  const router = useRouter();

  const handleGratitudePress = () => {
    router.push('/journal/gratitude');
  };

  const handleReflectionPress = () => {
    router.push('/journal/reflection');
  };

  const handleFreeformPress = () => {
    router.push('/journal/freeform');
  };

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Journal Hub" />
        <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
          <VStack space="md" className="p-6">
            <Heading size="xl" className="mb-2">
              How would you like to journal today?
            </Heading>
            <Text className="text-typography-500 mb-6">
              Choose an entry type to begin your session.
            </Text>

            <JournalCard
              title="Gratitude Journal"
              description="Focus on the positive aspects of your day."
              icon={Heart}
              iconColor="text-red-500 dark:text-red-400"
              onPress={handleGratitudePress}
              testID="gratitude-journal-button"
            />
            <JournalCard
              title="Daily Reflection"
              description="Review your wins and areas for growth."
              icon={Lightbulb}
              iconColor="text-yellow-500 dark:text-yellow-400"
              onPress={handleReflectionPress}
              testID="reflection-journal-button"
            />
            <JournalCard
              title="Freeform Entry"
              description="Write about anything that's on your mind."
              icon={PenTool}
              iconColor="text-indigo-500 dark:text-indigo-400"
              onPress={handleFreeformPress}
              testID="freeform-journal-button"
            />
          </VStack>
        </ScrollView>
      </VStack>
      <GlobalFab />
    </SafeAreaView>
  )
} 