import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, Pressable, Modal, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import {
  Brain, NotebookPen, Dumbbell, Soup, Activity, Moon, BarChart3,
  CheckCircle2, Sparkles, X, Palette, Leaf, Shield, Focus, Layers3,
  HeartHandshake, CreditCard, XCircle, Check
} from 'lucide-react-native';
import { LandingThemeProvider, useLandingTheme } from '@/contexts/LandingThemeContext';
import { DeviceMockup } from '@/components/DeviceMockup';
import { FlippableFeatureCard } from '@/components/FlippableFeatureCard';

function LandingContent() {
  const router = useRouter();
  const { theme, toggleTheme, isWarm } = useLandingTheme();
  const [animatedPhrase, setAnimatedPhrase] = useState('Move Forward');
  const [showStripeModal, setShowStripeModal] = useState(false);
  const [currentScreen, setCurrentScreen] = useState(0);
  const [flippedCard, setFlippedCard] = useState<string | null>(null);

  const phrases = [
    'Move Forward',
    'Build Better',
    'Grow Steady',
    'Live Gently',
    'Progress Naturally',
    'Thrive Daily'
  ];

  const mockupScreens = ['Journal', 'Habits', 'Analytics', 'Meals'];

  useEffect(() => {
    const interval = setInterval(() => {
      setAnimatedPhrase((current) => {
        const currentIndex = phrases.indexOf(current);
        return phrases[(currentIndex + 1) % phrases.length];
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentScreen((prev) => (prev + 1) % mockupScreens.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  // Theme-aware color classes
  const primaryColor = isWarm ? 'warm-crimson-600' : 'cool-blue-600';
  const primaryBg = isWarm ? 'bg-warm-crimson-600' : 'bg-cool-blue-600';
  const primaryText = isWarm ? 'text-warm-crimson-600' : 'text-cool-blue-600';
  const secondaryColor = isWarm ? 'warm-gold-500' : 'cool-indigo-500';
  const bgColor = isWarm ? 'bg-warm-sepia-50' : 'bg-cool-slate-50';
  const bgAlt = isWarm ? 'bg-warm-sepia-100' : 'bg-cool-slate-100';
  const textColor = isWarm ? 'text-warm-sepia-900' : 'text-cool-slate-900';
  const borderColor = isWarm ? 'border-warm-sepia-200' : 'border-cool-slate-200';

  const features = [
    {
      icon: NotebookPen,
      label: 'Journal',
      gradient: isWarm ? 'from-warm-crimson-500 to-warm-crimson-600' : 'from-cool-blue-500 to-cool-blue-600',
      description: 'Structured prompts for gratitude and reflection. Freeform notes when you need space. Your thoughts, organized gently.'
    },
    {
      icon: Dumbbell,
      label: 'Movement',
      gradient: 'from-green-500 to-green-600',
      description: 'Programs with progressions and kind regressions. Smart substitutions when equipment or time changes.'
    },
    {
      icon: Soup,
      label: 'Meals',
      gradient: isWarm ? 'from-warm-gold-500 to-warm-gold-600' : 'from-orange-500 to-orange-600',
      description: 'Quick, flexible logging. A living library of meals you actually eat. Optional computer vision estimates.'
    },
    {
      icon: Activity,
      label: 'Habits',
      gradient: 'from-purple-500 to-purple-600',
      description: 'Weekly habit focus with loving guardrails. Streaks that whisper, not yell. Real progress, not perfection.'
    },
    {
      icon: Moon,
      label: 'Reflection',
      gradient: isWarm ? 'from-warm-crimson-400 to-warm-gold-500' : 'from-cool-indigo-500 to-cool-indigo-600',
      description: 'Evening check-ins to surface patterns gently. Next steps offered, never forced. Privacy-forward by default.'
    },
    {
      icon: BarChart3,
      label: 'Analytics',
      gradient: 'from-pink-500 to-pink-600',
      description: 'Visualize your consistency and growth. Human signals + smart data you can actually feel and trust.'
    }
  ];

  const featureSections = [
    {
      title: 'Habits & Programs',
      bullets: [
        'Weekly habit focus with simple, loving guardrails',
        'Guided lessons you can read on a walk'
      ],
      visualization: 'stats',
      stats: [
        { label: 'Current Streak', value: '14', icon: Activity, gradient: 'from-green-500 to-emerald-600' },
        { label: 'Weekly Focus', value: '98%', icon: Focus, gradient: isWarm ? 'from-warm-crimson-500 to-warm-gold-500' : 'from-cool-blue-500 to-cool-indigo-500' },
        { label: 'Total Habits', value: '8', icon: Layers3, gradient: 'from-purple-500 to-violet-600' },
        { label: 'This Week', value: '6/7', icon: CheckCircle2, gradient: 'from-cyan-500 to-teal-600' }
      ]
    },
    {
      title: 'Journaling & Insights',
      bullets: [
        'Structured prompts when you want them, freeform when you don\'t',
        'Patterns surface gently—next steps offered, not forced',
        'Privacy-forward by default'
      ],
      visualization: 'cards',
      cards: [
        { title: 'Morning Gratitude', description: 'What are you grateful for today?' },
        { title: 'Evening Reflection', description: 'What went well? What could improve?' },
        { title: 'Freeform Notes', description: 'Your thoughts, your way' }
      ]
    },
    {
      title: 'Meals',
      bullets: [
        'Quick, flexible logging—no spreadsheets required',
        'A living library of meals you actually eat',
        'Future: optional estimates via computer vision'
      ],
      visualization: 'list',
      items: [
        { label: 'Breakfast', detail: 'Oatmeal with berries & almonds', time: '8:30 AM' },
        { label: 'Lunch', detail: 'Grilled chicken salad', time: '12:45 PM' },
        { label: 'Dinner', detail: 'Salmon with roasted veggies', time: '7:00 PM' }
      ]
    },
    {
      title: 'Movement',
      bullets: [
        'Programs with progressions and kind regressions',
        'Smart substitutions when equipment or time changes',
        'Built on a movement graph for real-world flexibility'
      ],
      visualization: 'progress',
      exercises: [
        { name: 'Push-ups', sets: '3x12', progress: 0.8 },
        { name: 'Squats', sets: '3x15', progress: 0.6 },
        { name: 'Plank', sets: '3x45s', progress: 0.9 }
      ]
    }
  ];

  return (
    <ScrollView className={`flex-1 ${isWarm ? 'bg-warm-sepia-50' : 'bg-white'}`}>
      {/* Header */}
      <View className={`px-4 py-4 border-b ${borderColor} ${isWarm ? 'bg-warm-sepia-50/90' : 'bg-white/90'}`}>
        <View className="flex-row items-center justify-between max-w-7xl mx-auto">
          <View className="flex-row items-center">
            <View className={`w-10 h-10 rounded-lg ${isWarm ? 'bg-gradient-to-br from-warm-crimson-600 to-warm-gold-500' : 'bg-gradient-to-br from-gray-900 to-gray-600'} items-center justify-center`}>
              <Brain size={20} color="#fff" />
            </View>
            <Text className={`ml-3 text-xl font-semibold ${textColor}`}>Swae OS</Text>
          </View>
          <View className="flex-row items-center gap-2">
            <Pressable
              onPress={toggleTheme}
              className={`p-2 rounded-lg ${isWarm ? 'bg-warm-sepia-200' : 'bg-gray-100'} active:opacity-70`}
            >
              <Palette size={20} color={isWarm ? '#dc2626' : '#2563eb'} />
            </Pressable>
            <Pressable
              onPress={() => router.push('/signup')}
              className={`px-4 py-2 ${primaryBg} rounded-lg active:opacity-70`}
            >
              <Text className="text-white font-medium">Get started</Text>
            </Pressable>
          </View>
        </View>
      </View>

      {/* Hero Section */}
      <View className="px-4 pt-16 pb-12">
        <View className="max-w-6xl mx-auto">
          {/* Mobile: Stack with mockup below, Desktop: Side-by-side */}
          <View className="flex-col lg:flex-row items-center gap-8 lg:gap-12">
            {/* Text content */}
            <View className="flex-1 w-full">
              <View className="mb-8 lg:mb-12">
                <Text className={`text-5xl md:text-6xl font-bold leading-tight mb-6 ${textColor}`}>
                  {animatedPhrase}
                </Text>
                <Text className={`text-4xl md:text-5xl font-normal opacity-80 ${textColor}`}>
                  with Swae
                </Text>
                <Text className={`text-xl mt-8 mb-10 opacity-80 ${textColor}`}>
                  Swae gently coordinates daily habits, journaling, movement, and meals into a rhythm you can trust for less tech and more nourishment.
                </Text>
                <Pressable
                  onPress={() => setShowStripeModal(true)}
                  className={`${primaryBg} px-8 py-4 rounded-xl self-start active:opacity-70`}
                >
                  <Text className="text-white text-lg font-semibold">Join early access</Text>
                </Pressable>
              </View>
            </View>

            {/* Device mockup - positioned to peek ~33% above fold on mobile */}
            <View className="flex-1 items-center w-full -mt-16 lg:mt-0">
              <DeviceMockup theme={isWarm ? 'warm' : 'cool'} activeScreen={currentScreen} />

              {/* Screen indicators */}
              <View className="flex-row gap-2 mt-8 justify-center">
                {mockupScreens.map((screen, index) => (
                  <Pressable
                    key={screen}
                    onPress={() => setCurrentScreen(index)}
                    className={`rounded-full transition-all ${currentScreen === index ? 'w-8' : 'w-2'} h-2`}
                    style={{
                      backgroundColor: currentScreen === index
                        ? (isWarm ? '#dc2626' : '#2563eb')
                        : (isWarm ? '#d6d3d1' : '#cbd5e1'),
                    }}
                  />
                ))}
              </View>
            </View>
          </View>
        </View>
      </View>

      {/* Interactive Feature Grid */}
      <View className="px-4 pb-20 pt-32 md:pt-16">
        <View className="max-w-6xl mx-auto">
          <Text className={`text-3xl font-bold text-center mb-4 ${textColor}`}>
            Everything You Need
          </Text>
          <Text className={`text-lg text-center mb-12 opacity-80 ${textColor}`}>
            Tap any card to learn more
          </Text>
          <View
            className={`p-8 ${bgAlt} rounded-3xl border ${borderColor}`}
            style={{
              flexDirection: 'row',
              flexWrap: 'wrap',
              gap: 16,
            }}
          >
            {features.map((feature) => (
              <View
                key={feature.label}
                style={{
                  width: 'calc(33.333% - 11px)',
                  minWidth: 150,
                }}
              >
                <FlippableFeatureCard
                  icon={feature.icon}
                  label={feature.label}
                  description={feature.description}
                  gradient={feature.gradient}
                  isWarm={isWarm}
                  isFlipped={flippedCard === feature.label}
                  onFlip={() => setFlippedCard(flippedCard === feature.label ? null : feature.label)}
                />
              </View>
            ))}
          </View>
        </View>
      </View>

      {/* Conversational Section */}
      <View className="px-4 py-20">
        <View className="max-w-3xl mx-auto">
          <Text className={`text-4xl font-bold mb-6 ${textColor}`}>
            Swae: Your Life, Not Your Checklist
          </Text>
          <Text className={`text-lg opacity-85 mb-4 ${textColor}`}>
            You don't need another app telling you to do more—you need a system that moves with you.
          </Text>
          <Text className={`text-lg opacity-85 mb-4 ${textColor}`}>
            Swae meets you where you are, weaving habits, journaling, meals, and movement into a rhythm that fits your life. Progress isn't punishment; it's momentum made effortless, guided by insight, not shame.
          </Text>
          <Text className={`text-lg opacity-85 ${textColor}`}>
            Start with one habit, one prompt, or one reflection. Swae handles the rest—stacking small wins into lasting change.
          </Text>
        </View>
      </View>

      {/* Old Way vs New Way Comparison */}
      <View className={`px-4 py-24 ${bgAlt}`}>
        <View className="max-w-6xl mx-auto">
          <Text className={`text-4xl font-bold text-center mb-4 ${textColor}`}>
            The Old Way vs. The Swae Way
          </Text>
          <Text className={`text-xl text-center mb-12 opacity-80 ${textColor}`}>
            Most wellness tools assume you'll bend your life to fit their program. We do the opposite.
          </Text>

          {/* Mobile: Reduced gap, Desktop: Normal gap */}
          <View className="flex-row gap-3 md:gap-8">
            {/* Old Way */}
            <View className={`flex-1 rounded-2xl border-2 border-red-200 ${isWarm ? 'bg-white' : 'bg-white'} p-4 md:p-6`}>
              <View className="flex-row items-center gap-2 bg-red-100 px-3 py-1 rounded-full self-start mb-4 md:mb-6">
                <XCircle size={16} color="#991b1b" />
                <Text className="text-red-800 text-sm font-medium">The fragmented way</Text>
              </View>
              <View className="space-y-3 md:space-y-4">
                {[
                  'Fragmented tools, endless dashboards, decision fatigue',
                  'Shame-first nudges, perfection or bust',
                  'Track everything or feel like you are failing',
                  'Short sprints, long burnouts, Monday restarts',
                  'Data you can\'t feel, progress you can\'t trust'
                ].map((item, i) => (
                  <View key={i} className={`flex-row items-start gap-2 md:gap-3 p-2 md:p-3 ${bgColor} rounded-lg`}>
                    <XCircle size={20} color="#ef4444" className="mt-0.5 flex-shrink-0" />
                    <Text className="flex-1 text-sm">{item}</Text>
                  </View>
                ))}
              </View>
            </View>

            {/* New Way */}
            <View className={`flex-1 rounded-2xl border-2 ${isWarm ? 'border-warm-gold-500 bg-gradient-to-br from-warm-gold-50 to-warm-crimson-50' : 'border-green-500 bg-gradient-to-br from-green-50 to-emerald-50'} p-4 md:p-6`}>
              <View className={`flex-row items-center gap-2 ${isWarm ? 'bg-warm-gold-100' : 'bg-green-100'} px-3 py-1 rounded-full self-start mb-4 md:mb-6`}>
                <Check size={16} color={isWarm ? '#92400e' : '#166534'} />
                <Text className={`${isWarm ? 'text-warm-gold-800' : 'text-green-800'} text-sm font-medium`}>The Swae way</Text>
              </View>
              <View className="space-y-3 md:space-y-4">
                {[
                  'One gentle habit at a time; practical wins, steady momentum',
                  'Real life first—travel, kids, chaos welcome',
                  'Simple check-ins for consistency (not perfection)',
                  'Tiny actions, stacked wins, resilient growth',
                  'Human signals + smart data you can actually feel'
                ].map((item, i) => (
                  <View key={i} className="flex-row items-start gap-2 md:gap-3 p-2 md:p-3 bg-white rounded-lg">
                    <Check size={20} color="#22c55e" className="mt-0.5 flex-shrink-0" />
                    <Text className="flex-1 text-sm font-medium">{item}</Text>
                  </View>
                ))}
              </View>
            </View>
          </View>
        </View>
      </View>

      {/* Feature Sections */}
      <View className="px-4 py-24">
        <View className="max-w-6xl mx-auto space-y-24 md:space-y-20">
          {featureSections.map((section, sectionIndex) => (
            <View key={section.title} className={`flex-col md:${sectionIndex % 2 === 1 ? 'flex-row-reverse' : 'flex-row'} gap-6 md:gap-10 items-start`}>
              <View className="flex-1 w-full">
                <Text className={`text-2xl font-bold mb-4 ${textColor}`}>{section.title}</Text>
                <View className="space-y-3">
                  {section.bullets.map((bullet, i) => (
                    <View key={i} className="flex-row items-start gap-3">
                      <CheckCircle2 size={20} color={isWarm ? '#dc2626' : '#2563eb'} className="mt-0.5" />
                      <Text className={`flex-1 text-base ${textColor}`}>{bullet}</Text>
                    </View>
                  ))}
                </View>
              </View>

              {/* Visualization */}
              <View className="flex-1 w-full">
                {section.visualization === 'stats' && (
                  <View className="grid grid-cols-2 gap-4 mt-4 md:mt-0 mb-12 md:mb-0">
                    {section.stats?.map((stat, i) => {
                      const StatIcon = stat.icon;
                      return (
                        <View key={i} className={`bg-gradient-to-br ${stat.gradient} rounded-xl p-6 active:scale-95 transition-transform`}>
                          <StatIcon size={32} color="#fff" className="mb-2" />
                          <Text className="text-3xl font-bold text-white">{stat.value}</Text>
                          <Text className="text-sm text-white opacity-90">{stat.label}</Text>
                        </View>
                      );
                    })}
                  </View>
                )}

                {section.visualization === 'cards' && (
                  <View className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2 md:mt-0 mb-12 md:mb-0">
                    {section.cards?.map((card, i) => (
                      <View key={i} className={`p-4 rounded-xl bg-gradient-to-br from-purple-50 to-indigo-100 dark:from-purple-900/20 dark:to-indigo-900/20 shadow-sm`}>
                        <Text className={`font-semibold mb-2 ${textColor}`}>{card.title}</Text>
                        <Text className={`text-sm opacity-80 ${textColor}`}>{card.description}</Text>
                      </View>
                    ))}
                  </View>
                )}

                {section.visualization === 'list' && (
                  <View className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2 md:mt-0 mb-12 md:mb-0">
                    {section.items?.map((item, i) => (
                      <View key={i} className={`p-4 rounded-xl bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/20 shadow-sm`}>
                        <Text className={`font-semibold ${textColor}`}>{item.label}</Text>
                        <Text className={`text-sm opacity-80 ${textColor}`}>{item.detail}</Text>
                        <Text className="text-xs opacity-60 mt-1">{item.time}</Text>
                      </View>
                    ))}
                  </View>
                )}

                {section.visualization === 'progress' && (
                  <View className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {section.exercises?.map((exercise, i) => (
                      <View key={i}>
                        <View className="flex-row justify-between mb-2">
                          <Text className={`font-medium ${textColor}`}>{exercise.name}</Text>
                          <Text className={`text-sm opacity-70 ${textColor}`}>{exercise.sets}</Text>
                        </View>
                        <View className={`h-2 ${bgAlt} rounded-full overflow-hidden`}>
                          <View
                            className={`h-full ${primaryBg}`}
                            style={{ width: `${exercise.progress * 100}%` }}
                          />
                        </View>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            </View>
          ))}
        </View>
      </View>

      {/* CTA Section */}
      <View className={`px-4 py-24 ${bgAlt}`}>
        <View className="max-w-4xl mx-auto items-center">
          <Text className={`text-5xl font-bold mb-6 text-center ${textColor}`}>
            Get early access to Swae OS
          </Text>
          <Text className={`text-xl mb-10 opacity-85 text-center ${textColor}`}>
            Start gentle. We'll invite you as features roll out—first habits and journaling, then meals and movement.
          </Text>
          <Pressable
            onPress={() => setShowStripeModal(true)}
            className={`${primaryBg} px-8 py-4 rounded-xl active:opacity-70`}
          >
            <Text className="text-white text-lg font-semibold">Join early access</Text>
          </Pressable>
          <Text className={`text-sm mt-4 opacity-70 ${textColor}`}>
            No spam. Just steady, human-first progress notes and early-access invites.
          </Text>
        </View>
      </View>

      {/* Footer */}
      <View className={`border-t ${borderColor} py-12 px-4`}>
        <View className="max-w-7xl mx-auto flex-row justify-between items-center">
          <View className="flex-row items-center">
            <View className={`w-8 h-8 rounded-lg ${isWarm ? 'bg-gradient-to-br from-warm-crimson-600 to-warm-gold-500' : 'bg-gradient-to-br from-gray-900 to-gray-600'} items-center justify-center`}>
              <Brain size={16} color="#fff" />
            </View>
            <Text className={`ml-3 text-xl font-semibold ${textColor}`}>Swae OS</Text>
          </View>
          <Text className={`text-sm opacity-80 ${textColor}`}>
            © {new Date().getFullYear()} Swae. All rights reserved.
          </Text>
        </View>
      </View>

      {/* Stripe Checkout Modal */}
      <Modal
        visible={showStripeModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowStripeModal(false)}
      >
        <Pressable
          className="flex-1 bg-black/50 items-center justify-center p-4"
          onPress={() => setShowStripeModal(false)}
        >
          <Pressable
            className={`w-full max-w-md ${isWarm ? 'bg-warm-sepia-50' : 'bg-white'} rounded-2xl overflow-hidden`}
            onPress={(e) => e.stopPropagation()}
          >
            <View className={`p-6 border-b ${borderColor}`}>
              <View className="flex-row items-center justify-between mb-4">
                <Text className={`text-2xl font-bold ${textColor}`}>Early Access Pass</Text>
                <Pressable onPress={() => setShowStripeModal(false)} className="p-2">
                  <X size={24} color={isWarm ? '#2a221b' : '#0f172a'} />
                </Pressable>
              </View>
              <Text className={`text-sm opacity-80 ${textColor}`}>
                Get instant access to Swae OS with all features. Limited time 100% discount applied.
              </Text>
            </View>

            <View className="p-6">
              <View className="flex-row items-end gap-3 mb-6">
                <Text className={`text-4xl font-bold ${textColor}`}>$0</Text>
                <Text className="text-xl line-through opacity-50">$49</Text>
                <Text className={`font-semibold ${primaryText}`}>100% OFF</Text>
              </View>

              <View className="space-y-3 mb-6">
                <View className="flex-row items-center gap-2">
                  <CheckCircle2 size={20} color={isWarm ? '#dc2626' : '#2563eb'} />
                  <Text className={textColor}>Instant access to habit system</Text>
                </View>
                <View className="flex-row items-center gap-2">
                  <CheckCircle2 size={20} color={isWarm ? '#dc2626' : '#2563eb'} />
                  <Text className={textColor}>Journaling with AI insights</Text>
                </View>
                <View className="flex-row items-center gap-2">
                  <CheckCircle2 size={20} color={isWarm ? '#dc2626' : '#2563eb'} />
                  <Text className={textColor}>Early access to movement & meals</Text>
                </View>
              </View>

              <Pressable
                onPress={() => {
                  setShowStripeModal(false);
                  router.push('/signup');
                }}
                className={`${primaryBg} px-6 py-4 rounded-xl flex-row items-center justify-center gap-2 active:opacity-70`}
              >
                <CreditCard size={20} color="#fff" />
                <Text className="text-white text-lg font-semibold">Claim Your Free Access</Text>
              </Pressable>

              <Text className={`text-xs text-center mt-4 opacity-60 ${textColor}`}>
                No payment required. Sign up and start immediately.
              </Text>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
    </ScrollView>
  );
}

export default function LandingPage() {
  return (
    <LandingThemeProvider>
      <LandingContent />
    </LandingThemeProvider>
  );
}
