import { OverlayProvider } from '@gluestack-ui/overlay';
import { ToastProvider } from '@gluestack-ui/toast';
import { useColorScheme } from 'nativewind';
import React from 'react';
import { View, ViewProps } from 'react-native';
import { config } from './config';

export type ModeType = 'light' | 'dark' | 'system';
export type ThemeVariantId = keyof typeof config['variants'] | undefined;

export function GluestackUIProvider({
  mode = 'light',
  themeId,
  ...props
}: {
  mode?: ModeType;
  themeId?: ThemeVariantId;
  children?: React.ReactNode;
  style?: ViewProps['style'];
}) {
  const { colorScheme } = useColorScheme();
  const baseStyle = config[colorScheme!];
  const variantStyle = themeId ? config.variants?.[themeId] : undefined;
  return (
    <View
      key={String(themeId || '')}
      className="flex-1 h-full w-full"
      style={[
        baseStyle,
        variantStyle,
        props.style,
      ]}
    >
      <OverlayProvider>
        <ToastProvider>{props.children}</ToastProvider>
      </OverlayProvider>
    </View>
  );
}
