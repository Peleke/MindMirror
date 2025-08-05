import React, { useEffect, useRef } from 'react';
import { Animated, Dimensions } from 'react-native';
import { Box } from '@/components/ui/box';
import { VStack } from '@/components/ui/vstack';
import { Text } from '@/components/ui/text';
import { HStack } from '@/components/ui/hstack';
import { Icon } from '@/components/ui/icon';
import { MessageCircle, Sparkles } from 'lucide-react-native';

interface TransitionOverlayProps {
  isVisible: boolean;
  onComplete: () => void;
  className?: string;
}

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

export function TransitionOverlay({ 
  isVisible, 
  onComplete, 
  className = "" 
}: TransitionOverlayProps) {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;
  const slideAnim = useRef(new Animated.Value(screenWidth)).current;

  useEffect(() => {
    if (isVisible) {
      // Start transition animation
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 400,
          useNativeDriver: true,
        }),
        Animated.timing(slideAnim, {
          toValue: 0,
          duration: 500,
          useNativeDriver: true,
        }),
      ]).start(() => {
        // Call onComplete after animation finishes
        setTimeout(onComplete, 200);
      });
    } else {
      // Reset animations
      fadeAnim.setValue(0);
      scaleAnim.setValue(0.8);
      slideAnim.setValue(screenWidth);
    }
  }, [isVisible, fadeAnim, scaleAnim, slideAnim, onComplete]);

  if (!isVisible) return null;

  return (
    <Animated.View
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        opacity: fadeAnim,
        zIndex: 1000,
      }}
      className={className}
    >
      <Box className="flex-1 items-center justify-center p-6">
        <Animated.View
          style={{
            transform: [
              { scale: scaleAnim },
              { translateX: slideAnim }
            ],
          }}
        >
          <VStack className="items-center space-y-6 bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-sm">
            <HStack className="items-center space-x-3">
              <Icon as={Sparkles} size="lg" className="text-purple-600 dark:text-purple-400" />
              <Icon as={MessageCircle} size="lg" className="text-blue-600 dark:text-blue-400" />
            </HStack>
            
            <VStack className="items-center space-y-3">
              <Text className="text-xl font-semibold text-typography-900 dark:text-white text-center">
                Journal Saved!
              </Text>
              <Text className="text-base text-typography-600 dark:text-gray-300 text-center leading-6">
                Now let's continue the conversation with your AI companion...
              </Text>
            </VStack>

            <HStack className="items-center space-x-1">
              <Box className="w-2 h-2 bg-purple-400 dark:bg-purple-500 rounded-full animate-pulse" />
              <Box className="w-2 h-2 bg-blue-400 dark:bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
              <Box className="w-2 h-2 bg-purple-400 dark:bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
            </HStack>
          </VStack>
        </Animated.View>
      </Box>
    </Animated.View>
  );
} 