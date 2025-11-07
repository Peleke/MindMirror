import React from 'react';
import { View, Text, Pressable, Animated } from 'react-native';
import { LucideIcon } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';

interface FlippableFeatureCardProps {
  icon: LucideIcon;
  label: string;
  description: string;
  gradient: string;
  isWarm: boolean;
  isFlipped: boolean;
  onFlip: () => void;
}

// Map gradient class names to actual colors
const getGradientColors = (gradient: string): [string, string] => {
  const gradientMap: Record<string, [string, string]> = {
    'from-warm-crimson-500 to-warm-crimson-600': ['#ef4444', '#dc2626'],
    'from-cool-blue-500 to-cool-blue-600': ['#3b82f6', '#2563eb'],
    'from-green-500 to-green-600': ['#22c55e', '#16a34a'],
    'from-warm-gold-500 to-warm-gold-600': ['#f59e0b', '#d97706'],
    'from-orange-500 to-orange-600': ['#f97316', '#ea580c'],
    'from-purple-500 to-purple-600': ['#a855f7', '#9333ea'],
    'from-warm-crimson-400 to-warm-gold-500': ['#f87171', '#f59e0b'],
    'from-cool-indigo-500 to-cool-indigo-600': ['#6366f1', '#4f46e5'],
    'from-pink-500 to-pink-600': ['#ec4899', '#db2777'],
  };
  return gradientMap[gradient] || ['#3b82f6', '#2563eb'];
};

export function FlippableFeatureCard({
  icon: Icon,
  label,
  description,
  gradient,
  isWarm,
  isFlipped,
  onFlip,
}: FlippableFeatureCardProps) {
  const flipAnim = React.useRef(new Animated.Value(0)).current;
  const [startColor, endColor] = getGradientColors(gradient);

  React.useEffect(() => {
    Animated.spring(flipAnim, {
      toValue: isFlipped ? 1 : 0,
      friction: 8,
      tension: 10,
      useNativeDriver: true,
    }).start();
  }, [isFlipped, flipAnim]);

  const frontInterpolate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '180deg'],
  });

  const backInterpolate = flipAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['180deg', '360deg'],
  });

  const opacityFront = flipAnim.interpolate({
    inputRange: [0, 0.5, 1],
    outputRange: [1, 0, 0],
  });

  const opacityBack = flipAnim.interpolate({
    inputRange: [0, 0.5, 1],
    outputRange: [0, 0, 1],
  });

  return (
    <Pressable
      onPress={onFlip}
      style={{
        width: '100%',
        aspectRatio: 1,
        perspective: 1000,
      }}
    >
      {/* Front of card */}
      <Animated.View
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: opacityFront,
          transform: [{ rotateY: frontInterpolate }],
          backfaceVisibility: 'hidden',
        }}
      >
        <LinearGradient
          colors={[startColor, endColor]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={{
            width: '100%',
            height: '100%',
            borderRadius: 16,
            padding: 24,
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Icon size={40} color="#fff" style={{ marginBottom: 12 }} />
          <Text
            style={{
              color: '#fff',
              fontWeight: '600',
              fontSize: 16,
              textAlign: 'center',
            }}
          >
            {label}
          </Text>
        </LinearGradient>
      </Animated.View>

      {/* Back of card */}
      <Animated.View
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: opacityBack,
          transform: [{ rotateY: backInterpolate }],
          backfaceVisibility: 'hidden',
        }}
      >
        <View
          style={{
            width: '100%',
            height: '100%',
            backgroundColor: isWarm ? '#fdfaf6' : '#ffffff',
            borderRadius: 16,
            padding: 20,
            borderWidth: 2,
            borderColor: isWarm ? '#fecaca' : '#bfdbfe',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Icon size={32} color={isWarm ? '#dc2626' : '#2563eb'} style={{ marginBottom: 12 }} />
          <Text
            style={{
              fontWeight: '700',
              fontSize: 15,
              textAlign: 'center',
              marginBottom: 8,
              color: isWarm ? '#292524' : '#0f172a',
            }}
          >
            {label}
          </Text>
          <Text
            numberOfLines={4}
            ellipsizeMode="tail"
            style={{
              fontSize: 13,
              textAlign: 'center',
              lineHeight: 19,
              color: isWarm ? '#57534e' : '#475569',
              opacity: 0.85,
            }}
          >
            {description}
          </Text>
        </View>
      </Animated.View>
    </Pressable>
  );
}
