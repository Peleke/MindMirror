import { Platform } from 'react-native'

export const animations = {
  // Duration constants
  duration: {
    fast: 150,
    normal: 300,
    slow: 500,
    verySlow: 800,
  },
  
  // Easing functions
  easing: {
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    linear: 'linear',
  },
  
  // Scale values
  scale: {
    none: 1,
    small: 0.95,
    medium: 0.9,
    large: 0.8,
  },
  
  // Opacity values
  opacity: {
    transparent: 0,
    dim: 0.3,
    medium: 0.5,
    high: 0.8,
    opaque: 1,
  },
  
  // Translation values
  translate: {
    none: 0,
    small: 4,
    medium: 8,
    large: 16,
    xl: 32,
  },
  
  // Rotation values
  rotation: {
    none: '0deg',
    small: '5deg',
    medium: '15deg',
    large: '45deg',
    full: '360deg',
  },
} as const

export type AnimationToken = typeof animations
export type DurationKey = keyof AnimationToken['duration']
export type EasingKey = keyof AnimationToken['easing']
export type ScaleKey = keyof AnimationToken['scale']

// Common animation configurations
export const animationConfigs = {
  // Button press animation
  buttonPress: {
    duration: animations.duration.fast,
    easing: animations.easing.easeOut,
    scale: animations.scale.small,
  },
  
  // Card hover animation
  cardHover: {
    duration: animations.duration.normal,
    easing: animations.easing.easeInOut,
    scale: animations.scale.none,
    translateY: -animations.translate.small,
  },
  
  // Modal enter/exit
  modal: {
    enter: {
      duration: animations.duration.normal,
      easing: animations.easing.easeOut,
    },
    exit: {
      duration: animations.duration.fast,
      easing: animations.easing.easeIn,
    },
  },
  
  // List item animations
  listItem: {
    duration: animations.duration.normal,
    easing: animations.easing.easeOut,
    stagger: 50, // Delay between items
  },
  
  // Loading spinner
  spinner: {
    duration: 1000,
    easing: animations.easing.linear,
    rotation: animations.rotation.full,
  },
} as const

// Platform-specific animation adjustments
export const getPlatformAnimation = (config: any) => {
  if (Platform.OS === 'android') {
    // Android-specific adjustments
    return {
      ...config,
      useNativeDriver: true,
    }
  }
  
  // iOS-specific adjustments
  return {
    ...config,
    useNativeDriver: true,
  }
} 