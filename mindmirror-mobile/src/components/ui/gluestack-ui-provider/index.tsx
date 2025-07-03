import { OverlayProvider } from '@gluestack-ui/overlay';
import { ToastProvider } from '@gluestack-ui/toast';
import { useColorScheme } from 'nativewind';
import React from 'react';
import { View, ViewProps } from 'react-native';
import { config } from './config';

export type ModeType = 'light' | 'dark' | 'system';

export function GluestackUIProvider({
  mode = 'light',
  ...props
}: {
  mode?: ModeType;
  children?: React.ReactNode;
  style?: ViewProps['style'];
}) {
  const { colorScheme } = useColorScheme();

  return (
    <View
      className="flex-1 h-full w-full"
      style={[
        config[colorScheme!],
        props.style,
      ]}
    >
      <OverlayProvider>
        <ToastProvider>{props.children}</ToastProvider>
      </OverlayProvider>
    </View>
  );
}
