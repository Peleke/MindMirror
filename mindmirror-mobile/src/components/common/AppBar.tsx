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
import { Box } from "@/components/ui/box";
import { useNavigation } from '@react-navigation/native';
import { useRouter } from 'expo-router';
import { useAuth } from '@/features/auth/context/AuthContext';
import { getAvatarUrl, getAvatarUrlSync } from '@/utils/avatar';
import { useState, useEffect } from 'react';
import { BellIcon } from 'lucide-react-native';
import { useMyPendingCoachingRequests } from '@/services/api/users';
import InboxDrawer from '@/components/inbox/InboxDrawer';

interface AppBarProps {
  title: string;
  showBackButton?: boolean; // vs menu button
  onBackPress?: () => void; // custom back handler
  showProfile?: boolean; // some screens might not need it
  showInbox?: boolean; // show inbox bell icon
}

export function AppBar({ 
  title, 
  showBackButton = false, 
  onBackPress,
  showProfile = true,
  showInbox = true
}: AppBarProps) {
  const router = useRouter();
  const navigation = useNavigation();
  const { user } = useAuth();
  const [avatarUrl, setAvatarUrl] = useState<string>(getAvatarUrlSync(user?.email));
  const [showInboxDrawer, setShowInboxDrawer] = useState(false);

  // Get pending coaching requests for notification badge
  const { data: inboxData } = useMyPendingCoachingRequests()
  const pendingRequestsCount = inboxData?.myPendingCoachingRequests?.length || 0

  // Load real Gravatar URL asynchronously
  useEffect(() => {
    const loadRealAvatar = async () => {
      if (user?.email) {
        console.log('🎯 Loading real Gravatar for:', user.email);
        const realUrl = await getAvatarUrl(user.email);
        console.log('🎯 Real Gravatar URL:', realUrl);
        setAvatarUrl(realUrl);
      }
    };
    loadRealAvatar();
  }, [user?.email]);

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

  const handleInboxPress = () => {
    setShowInboxDrawer(true);
  };

  return (
    <>
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
        
        <HStack className="items-center" space="sm">
          {/* Inbox Bell Icon */}
          {showInbox && (
            <Pressable onPress={handleInboxPress} className="relative p-2">
              <Icon as={BellIcon} size="md" className="text-typography-700" />
              {pendingRequestsCount > 0 && (
                <Box className="absolute -top-1 -right-1 bg-red-500 rounded-full w-5 h-5 items-center justify-center">
                  <Text className="text-white text-xs font-bold">
                    {pendingRequestsCount > 9 ? '9+' : pendingRequestsCount}
                  </Text>
                </Box>
              )}
            </Pressable>
          )}
          
          {showProfile && (
            <Pressable onPress={handleProfilePress}>
              <Avatar className="h-9 w-9">
                <AvatarFallbackText>U</AvatarFallbackText>
                <AvatarImage source={{ uri: avatarUrl }} />
                <AvatarBadge />
              </Avatar>
            </Pressable>
          )}
        </HStack>
      </HStack>
      
      {/* Inbox Drawer */}
      <InboxDrawer isOpen={showInboxDrawer} onClose={() => setShowInboxDrawer(false)} />
    </>
  );
} 