import React from 'react';
import { View, Image, ImageSourcePropType } from 'react-native';
import { AnimatedMockupScreens } from './AnimatedMockupScreens';

interface DeviceMockupProps {
  screenshot?: ImageSourcePropType;
  theme?: 'warm' | 'cool';
  activeScreen?: number;
}

export function DeviceMockup({ screenshot, theme = 'warm', activeScreen = 0 }: DeviceMockupProps) {
  const isWarm = theme === 'warm';

  return (
    <View className="relative mx-auto" style={{ maxWidth: 320 }}>
      {/* Glow effect */}
      <View
        className="absolute inset-0 blur-3xl opacity-30"
        style={{
          transform: [{ translateY: 32 }],
          backgroundColor: isWarm ? '#dc2626' : '#2563eb'
        }}
      />

      {/* Device frame */}
      <View className="relative">
        {/* Outer bezel - dark phone frame */}
        <View
          className={`rounded-[40px] p-3 shadow-2xl ${isWarm ? 'bg-warm-sepia-900' : 'bg-gray-900'}`}
          style={{
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 20 },
            shadowOpacity: 0.4,
            shadowRadius: 40,
          }}
        >
          {/* Inner screen */}
          <View className="rounded-[32px] overflow-hidden bg-white">
            {/* Status bar */}
            <View className={`px-6 py-2 flex-row justify-between items-center ${isWarm ? 'bg-warm-sepia-50' : 'bg-white'}`}>
              <View className="text-xs opacity-60">9:41</View>
              <View className="flex-row gap-1">
                <View className="w-1 h-1 rounded-full bg-black opacity-40" />
                <View className="w-1 h-1 rounded-full bg-black opacity-40" />
                <View className="w-1 h-1 rounded-full bg-black opacity-40" />
              </View>
            </View>

            {/* Screenshot content */}
            <View
              className={`relative ${isWarm ? 'bg-warm-sepia-50' : 'bg-white'}`}
              style={{ height: 600, aspectRatio: 9 / 19.5 }}
            >
              {screenshot ? (
                <Image
                  source={screenshot}
                  className="w-full h-full"
                  resizeMode="cover"
                />
              ) : (
                // Animated placeholder UIs when no screenshot
                <AnimatedMockupScreens activeScreen={activeScreen} isWarm={isWarm} />
              )}
            </View>

            {/* Home indicator */}
            <View className={`flex items-center py-2 ${isWarm ? 'bg-warm-sepia-50' : 'bg-white'}`}>
              <View
                className={`w-24 h-1 rounded-full ${isWarm ? 'bg-warm-sepia-900' : 'bg-gray-900'}`}
                style={{ opacity: 0.4 }}
              />
            </View>
          </View>
        </View>

        {/* Notch */}
        <View
          className="absolute top-0 left-1/2 bg-black rounded-b-3xl"
          style={{
            width: 120,
            height: 28,
            transform: [{ translateX: -60 }, { translateY: 12 }],
          }}
        />
      </View>
    </View>
  );
}
