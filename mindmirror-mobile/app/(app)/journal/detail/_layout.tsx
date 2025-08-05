import { Tabs } from 'expo-router';

export default function DetailLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: { display: 'none' }, // Hide tab bar completely
      }}
    >
      <Tabs.Screen name="gratitude/[id]" options={{ href: null }} />
      <Tabs.Screen name="reflection/[id]" options={{ href: null }} />
      <Tabs.Screen name="freeform/[id]" options={{ href: null }} />
    </Tabs>
  );
} 