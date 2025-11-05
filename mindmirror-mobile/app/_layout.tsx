import { GluestackUIProvider } from "@/components/ui/gluestack-ui-provider";
import React from "react";
import { ThemeVariantProvider, useThemeVariant } from "@/theme/ThemeContext";
import { AuthStateHandler } from '@/features/auth/components/AuthStateHandler';
import { AuthProvider } from '@/features/auth/context/AuthContext';
import { ApolloProviderWrapper, SimpleApolloProvider } from '@/services/api/apollo-provider';
import { AutoEnrollHandler } from '@/features/auth/components/AutoEnrollHandler';
import FontAwesome from "@expo/vector-icons/FontAwesome";
import {
  DarkTheme,
  DefaultTheme,
  ThemeProvider,
} from "@react-navigation/native";
import { useFonts } from "expo-font";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { useColorScheme } from "nativewind";
import { useEffect } from "react";
import "../global.css";

export {
  // Catch any errors thrown by the Layout component.
  ErrorBoundary
} from "expo-router";

export const unstable_settings = {
  // Start on landing page at root
  initialRouteName: "index",
};

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require("../assets/fonts/SpaceMono-Regular.ttf"),
    ...FontAwesome.font,
  });

  // Expo Router uses Error Boundaries to catch errors in the navigation tree.
  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <ThemeVariantProvider>
      <RootLayoutNav />
    </ThemeVariantProvider>
  );
}

function RootLayoutNav() {
  const { colorScheme } = useColorScheme();
  const { themeId } = useThemeVariant();

  return (
    <GluestackUIProvider mode={(colorScheme ?? "light") as "light" | "dark"} themeId={themeId}>
      <ThemeProvider value={colorScheme === "dark" ? DarkTheme : DefaultTheme}>
        <SimpleApolloProvider>
          <AuthProvider>
            <ApolloProviderWrapper>
              {/* Temporarily disable auth redirects to show landing page */}
              {/* <AuthStateHandler /> */}
              <AutoEnrollHandler />
              <Stack screenOptions={{ headerShown: false }}>
                <Stack.Screen name="index" options={{ headerShown: false }} />
                <Stack.Screen name="(auth)" options={{ headerShown: false }} />
                <Stack.Screen name="(app)" options={{ headerShown: false }} />
              </Stack>
            </ApolloProviderWrapper>
          </AuthProvider>
        </SimpleApolloProvider>
      </ThemeProvider>
    </GluestackUIProvider>
  );
}

export function RootLayoutProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeVariantProvider>
      {children}
    </ThemeVariantProvider>
  );
}
