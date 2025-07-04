import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from "@/components/ui/avatar";
import { Box } from "@/components/ui/box";
import { Heading } from "@/components/ui/heading";
import { HStack } from "@/components/ui/hstack";
import { ChevronRightIcon, Icon, MenuIcon } from "@/components/ui/icon";
import { Pressable } from "@/components/ui/pressable";
import { SafeAreaView } from "@/components/ui/safe-area-view";
import { ScrollView } from "@/components/ui/scroll-view";
import { Text } from "@/components/ui/text";
import { VStack } from "@/components/ui/vstack";
import { useNavigation } from '@react-navigation/native';
import { useRouter } from 'expo-router';
import { Heart, Lightbulb, PenTool } from "lucide-react-native";

const JOURNAL_TYPES = [
  {
    id: 'gratitude',
    title: 'Gratitude Journal',
    description: 'Reflect on what you\'re grateful for today',
    icon: Heart,
    color: 'bg-blue-50 dark:bg-blue-950',
    iconColor: 'text-blue-600 dark:text-blue-400',
    route: '/journal/gratitude'
  },
  {
    id: 'reflection',
    title: 'Daily Reflection',
    description: 'Look back on your day and insights',
    icon: Lightbulb,
    color: 'bg-indigo-50 dark:bg-indigo-950',
    iconColor: 'text-indigo-600 dark:text-indigo-400',
    route: '/journal/reflection'
  },
  {
    id: 'freeform',
    title: 'Freeform Writing',
    description: 'Express your thoughts freely',
    icon: PenTool,
    color: 'bg-purple-50 dark:bg-purple-950',
    iconColor: 'text-purple-600 dark:text-purple-400',
    route: '/journal/freeform'
  }
];

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

  const handleJournalPress = (route: string) => {
    router.push(route as any);
  };

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
            <Heading size="2xl" className="font-roboto text-typography-900">
              Start Your Journal
            </Heading>
            <Text className="text-typography-600">
              Choose the type of entry you'd like to create
            </Text>
          </VStack>
          
          {/* Content */}
          <VStack className="px-6 pb-6" space="md">
            {JOURNAL_TYPES.map((journalType) => (
              <Pressable
                key={journalType.id}
                onPress={() => handleJournalPress(journalType.route)}
                className="mb-4"
              >
                <Box 
                  className={`p-6 min-h-[120px] rounded-lg ${journalType.color} border border-border-200 dark:border-border-700`}
                >
                  {/* Card Header */}
                  <Box className="mb-4">
                    <Icon 
                      as={journalType.icon}
                      size="lg"
                      className={journalType.iconColor}
                    />
                  </Box>
                  
                  {/* Card Title */}
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white mb-2">
                    {journalType.title}
                  </Text>
                  
                  {/* Card Description */}
                  <Text className="text-base text-typography-600 dark:text-gray-200 leading-6 flex-1 mb-4">
                    {journalType.description}
                  </Text>
                  
                  {/* Card Footer */}
                  <Box className="items-end">
                    <Icon 
                      as={ChevronRightIcon}
                      size="sm"
                      className="text-typography-400 dark:text-typography-500"
                    />
                  </Box>
                </Box>
              </Pressable>
            ))}
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  );
} 