import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from "@/components/ui/avatar"
import { Box } from "@/components/ui/box"
import { Button, ButtonText } from "@/components/ui/button"
import { Heading } from "@/components/ui/heading"
import { HStack } from "@/components/ui/hstack"
import { Icon, MenuIcon } from "@/components/ui/icon"
import { Pressable } from "@/components/ui/pressable"
import { SafeAreaView } from "@/components/ui/safe-area-view"
import { ScrollView } from "@/components/ui/scroll-view"
import { Text } from "@/components/ui/text"
import { VStack } from "@/components/ui/vstack"
import { useNavigation } from '@react-navigation/native'
import { useRouter } from 'expo-router'
import { Heart, Lightbulb, PenTool } from "lucide-react-native"

function AppBar() {
  const router = useRouter()
  const navigation = useNavigation()

  const handleMenuPress = () => {
    (navigation as any).openDrawer()
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
        <Pressable onPress={handleMenuPress}>
          <Icon as={MenuIcon} />
        </Pressable>
        <Text className="text-xl">Journal Hub</Text>
      </HStack>
      
      <Pressable onPress={handleProfilePress}>
        <Avatar className="h-9 w-9">
          <AvatarFallbackText>U</AvatarFallbackText>
          <AvatarImage source={{ uri: "https://i.pravatar.cc/300" }} />
          <AvatarBadge />
        </Avatar>
      </Pressable>
    </HStack>
  )
}

const JournalCard = ({ title, description, icon, onPress, testID }) => (
    <Pressable
      onPress={onPress}
      className="bg-background-50 dark:bg-background-100 p-6 rounded-lg shadow-md w-full"
      testID={testID}
    >
      <HStack space="md" className="items-center">
        <Icon as={icon} size="xl" className="text-primary-500" />
        <VStack>
          <Heading size="md">{title}</Heading>
          <Text size="sm" className="text-typography-500 mt-1">
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
        <AppBar />
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
              onPress={handleGratitudePress}
              testID="gratitude-journal-button"
            />
            <JournalCard
              title="Daily Reflection"
              description="Review your wins and areas for growth."
              icon={Lightbulb}
              onPress={handleReflectionPress}
              testID="reflection-journal-button"
            />
            <JournalCard
              title="Freeform Entry"
              description="Write about anything that's on your mind."
              icon={PenTool}
              onPress={handleFreeformPress}
              testID="freeform-journal-button"
            />
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 