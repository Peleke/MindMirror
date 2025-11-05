import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Pressable, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { Brain, NotebookPen, Dumbbell, Soup, Activity, Moon, BarChart3, CheckCircle2, Sparkles } from 'lucide-react-native';

export default function LandingPage() {
  const router = useRouter();
  const [animatedPhrase, setAnimatedPhrase] = useState('Move Forward');

  const phrases = [
    'Move Forward',
    'Build Better',
    'Grow Steady',
    'Live Gently',
    'Progress Naturally',
    'Thrive Daily'
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setAnimatedPhrase((current) => {
        const currentIndex = phrases.indexOf(current);
        return phrases[(currentIndex + 1) % phrases.length];
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const features = [
    { icon: NotebookPen, label: 'Journal', gradient: 'bg-gradient-to-br from-blue-500 to-blue-600' },
    { icon: Dumbbell, label: 'Movement', gradient: 'bg-gradient-to-br from-green-500 to-green-600' },
    { icon: Soup, label: 'Meals', gradient: 'bg-gradient-to-br from-orange-500 to-orange-600' },
    { icon: Activity, label: 'Habits', gradient: 'bg-gradient-to-br from-purple-500 to-purple-600' },
    { icon: Moon, label: 'Reflection', gradient: 'bg-gradient-to-br from-indigo-500 to-indigo-600' },
    { icon: BarChart3, label: 'Analytics', gradient: 'bg-gradient-to-br from-pink-500 to-pink-600' }
  ];

  return (
    <ScrollView className="flex-1 bg-white">
      {/* Header */}
      <View className="px-4 py-4 border-b border-gray-200 bg-white/90">
        <View className="flex-row items-center justify-between max-w-7xl mx-auto">
          <View className="flex-row items-center">
            <View className="w-10 h-10 rounded-lg bg-gradient-to-br from-gray-900 to-gray-600 items-center justify-center">
              <Brain size={20} color="#fff" />
            </View>
            <Text className="ml-3 text-xl font-semibold">Swae OS</Text>
          </View>
          <Pressable
            onPress={() => router.push('/auth/login')}
            className="px-4 py-2 bg-gray-900 rounded-lg active:opacity-70"
          >
            <Text className="text-white font-medium">Get started</Text>
          </Pressable>
        </View>
      </View>

      {/* Hero Section */}
      <View className="px-4 pt-16 pb-12">
        <View className="max-w-6xl mx-auto">
          <View className="mb-12">
            <Text className="text-5xl md:text-6xl font-bold leading-tight mb-6">
              {animatedPhrase}
            </Text>
            <Text className="text-4xl md:text-5xl font-normal opacity-80">
              with Swae
            </Text>
            <Text className="text-xl mt-8 mb-10 opacity-80">
              Swae gently coordinates daily habits, journaling, movement, and meals into a rhythm you can trust for less tech and more nourishment.
            </Text>
            <Pressable
              onPress={() => router.push('/auth/signup')}
              className="bg-gray-900 px-8 py-4 rounded-xl self-start active:opacity-70"
            >
              <Text className="text-white text-lg font-semibold">Join early access</Text>
            </Pressable>
          </View>

          {/* Feature Grid Mockup */}
          <View className="grid grid-cols-3 gap-4 p-8 bg-gray-50 rounded-3xl border border-gray-200">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Pressable
                  key={feature.label}
                  className={`${feature.gradient} rounded-2xl p-6 items-center justify-center active:scale-95 transition-transform`}
                  style={{ aspectRatio: 1 }}
                >
                  <Icon size={32} color="#fff" className="mb-3" />
                  <Text className="text-white font-medium text-sm text-center">
                    {feature.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>
      </View>

      {/* Conversational Section */}
      <View className="px-4 py-20">
        <View className="max-w-3xl mx-auto">
          <Text className="text-4xl font-bold mb-6">
            Swae: Your Life, Not Your Checklist
          </Text>
          <Text className="text-lg opacity-85 mb-4">
            You don't need another app telling you to do more—you need a system that moves with you.
          </Text>
          <Text className="text-lg opacity-85 mb-4">
            Swae meets you where you are, weaving habits, journaling, meals, and movement into a rhythm that fits your life. Progress isn't punishment; it's momentum made effortless, guided by insight, not shame.
          </Text>
          <Text className="text-lg opacity-85">
            Start with one habit, one prompt, or one reflection. Swae handles the rest—stacking small wins into lasting change.
          </Text>
        </View>
      </View>

      {/* Old Way vs New Way Comparison */}
      <View className="px-4 py-24 bg-gray-50">
        <View className="max-w-6xl mx-auto">
          <Text className="text-4xl font-bold text-center mb-4">
            The Old Way vs. The Swae Way
          </Text>
          <Text className="text-xl text-center mb-12 opacity-80">
            Most wellness tools assume you'll bend your life to fit their program. We do the opposite.
          </Text>

          <View className="flex-row gap-8">
            {/* Old Way */}
            <View className="flex-1 rounded-2xl border-2 border-red-200 bg-white p-6">
              <View className="flex-row items-center gap-2 bg-red-100 px-3 py-1 rounded-full self-start mb-6">
                <Text className="text-red-800 text-sm">The fragmented way</Text>
              </View>
              <View className="space-y-4">
                {[
                  'Fragmented tools, endless dashboards, decision fatigue',
                  'Shame-first nudges, perfection or bust',
                  'Track everything or feel like you are failing',
                  'Short sprints, long burnouts, Monday restarts',
                  'Data you can't feel, progress you can't trust'
                ].map((item, i) => (
                  <View key={i} className="flex-row items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <CheckCircle2 size={20} color="#ef4444" className="mt-0.5" />
                    <Text className="flex-1 text-sm">{item}</Text>
                  </View>
                ))}
              </View>
            </View>

            {/* New Way */}
            <View className="flex-1 rounded-2xl border-2 border-green-500 bg-gradient-to-br from-green-50 to-emerald-50 p-6">
              <View className="flex-row items-center gap-2 bg-green-100 px-3 py-1 rounded-full self-start mb-6">
                <Text className="text-green-800 text-sm">The Swae way</Text>
              </View>
              <View className="space-y-4">
                {[
                  'One gentle habit at a time; practical wins, steady momentum',
                  'Real life first—travel, kids, chaos welcome',
                  'Simple check-ins for consistency (not perfection)',
                  'Tiny actions, stacked wins, resilient growth',
                  'Human signals + smart data you can actually feel'
                ].map((item, i) => (
                  <View key={i} className="flex-row items-start gap-3 p-3 bg-white rounded-lg">
                    <CheckCircle2 size={20} color="#22c55e" className="mt-0.5" />
                    <Text className="flex-1 text-sm font-medium">{item}</Text>
                  </View>
                ))}
              </View>
            </View>
          </View>
        </View>
      </View>

      {/* CTA Section */}
      <View className="px-4 py-24">
        <View className="max-w-4xl mx-auto text-center">
          <Text className="text-5xl font-bold mb-6">
            Get early access to Swae OS
          </Text>
          <Text className="text-xl mb-10 opacity-85">
            Start gentle. We'll invite you as features roll out—first habits and journaling, then meals and movement.
          </Text>
          <Pressable
            onPress={() => router.push('/auth/signup')}
            className="bg-gray-900 px-8 py-4 rounded-xl self-center active:opacity-70"
          >
            <Text className="text-white text-lg font-semibold">Join early access</Text>
          </Pressable>
          <Text className="text-sm mt-4 opacity-70">
            No spam. Just steady, human-first progress notes and early-access invites.
          </Text>
        </View>
      </View>

      {/* Footer */}
      <View className="border-t border-gray-200 py-12 px-4">
        <View className="max-w-7xl mx-auto flex-row justify-between items-center">
          <View className="flex-row items-center">
            <View className="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-900 to-gray-600 items-center justify-center">
              <Brain size={16} color="#fff" />
            </View>
            <Text className="ml-3 text-xl font-semibold">Swae OS</Text>
          </View>
          <Text className="text-sm opacity-80">
            © {new Date().getFullYear()} Swae. All rights reserved.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}
