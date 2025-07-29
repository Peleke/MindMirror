import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from "@/components/ui/avatar";
import { HStack } from "@/components/ui/hstack";
import { ChevronLeftIcon, Icon, MenuIcon } from "@/components/ui/icon";
import { Pressable } from "@/components/ui/pressable";
import { Text } from "@/components/ui/text";
import { useNavigation } from '@react-navigation/native';
import { useRouter } from 'expo-router';
import { useAuth } from '@/features/auth/context/AuthContext';
import { getAvatarUrlSync } from '@/utils/avatar';

interface AppBarProps {
  title: string;
  showBackButton?: boolean; // vs menu button
  onBackPress?: () => void; // custom back handler
  showProfile?: boolean; // some screens might not need it
}

export function AppBar({ 
  title, 
  showBackButton = false, 
  onBackPress,
  showProfile = true 
}: AppBarProps) {
  const router = useRouter();
  const navigation = useNavigation();
  const { user } = useAuth();

  const handleMenuPress = () => {
    (navigation as any).openDrawer();
  };

  const handleBackPress = () => {
    if (onBackPress) {
      onBackPress();
    } else {
      router.back();
    }
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
        <Pressable onPress={showBackButton ? handleBackPress : handleMenuPress}>
          <Icon as={showBackButton ? ChevronLeftIcon : MenuIcon} />
        </Pressable>
        <Text className="text-xl">{title}</Text>
      </HStack>
      
      {showProfile && (
        <Pressable onPress={handleProfilePress}>
          <Avatar className="h-9 w-9">
            <AvatarFallbackText>U</AvatarFallbackText>
            <AvatarImage source={{ uri: getAvatarUrlSync(user?.email) }} />
            <AvatarBadge />
          </Avatar>
        </Pressable>
      )}
    </HStack>
  );
} 