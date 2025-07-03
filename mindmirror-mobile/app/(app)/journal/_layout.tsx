import { Tabs } from 'expo-router'

export default function JournalLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: { display: 'none' }, // Hide the entire tab bar
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          href: null, // Hide from parent tab bar
        }}
      />
      <Tabs.Screen
        name="freeform"
        options={{
          href: null, // Hide from parent tab bar
        }}
      />
      <Tabs.Screen
        name="gratitude"
        options={{
          href: null, // Hide from parent tab bar
        }}
      />
      <Tabs.Screen
        name="reflection"
        options={{
          href: null, // Hide from parent tab bar
        }}
      />
    </Tabs>
  )
} 