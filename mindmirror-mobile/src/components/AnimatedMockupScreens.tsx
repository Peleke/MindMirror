import React, { useState, useEffect } from 'react';
import { View, Text, Animated } from 'react-native';
import { NotebookPen, Activity, CheckCircle2, BarChart3, Dumbbell, Soup } from 'lucide-react-native';

interface AnimatedMockupScreensProps {
  activeScreen: number;
  isWarm: boolean;
}

export function AnimatedMockupScreens({ activeScreen, isWarm }: AnimatedMockupScreensProps) {
  const primaryColor = isWarm ? '#dc2626' : '#2563eb';
  const bgColor = isWarm ? '#faf8f5' : '#f8fafc';
  const textColor = isWarm ? '#2a221b' : '#0f172a';

  // Animation states for each screen
  const [typing, setTyping] = useState('');
  const [habitChecks, setHabitChecks] = useState([false, false, false, false]);
  const [barHeights] = useState([0.4, 0.7, 0.95, 0.85, 1.0, 0.9, 0.6].map(() => new Animated.Value(0)));
  const [workoutReps, setWorkoutReps] = useState([0, 0, 0]);
  const [mealAdded, setMealAdded] = useState(false);

  // Typing animation for journal
  useEffect(() => {
    if (activeScreen === 0) {
      setTyping('');
      const text = 'Grateful for morning coffee and quiet time to reflect...';
      let i = 0;
      const interval = setInterval(() => {
        if (i < text.length) {
          setTyping(text.slice(0, i + 1));
          i++;
        } else {
          clearInterval(interval);
        }
      }, 50);
      return () => clearInterval(interval);
    }
  }, [activeScreen]);

  // Habit checking animation
  useEffect(() => {
    if (activeScreen === 1) {
      setHabitChecks([false, false, false, false]);
      const timers = [0, 800, 1600, 2400].map((delay, index) =>
        setTimeout(() => {
          setHabitChecks(prev => {
            const newChecks = [...prev];
            newChecks[index] = true;
            return newChecks;
          });
        }, delay)
      );
      return () => timers.forEach(clearTimeout);
    }
  }, [activeScreen]);

  // Bar chart animation
  useEffect(() => {
    if (activeScreen === 2) {
      barHeights.forEach((height, index) => {
        height.setValue(0);
        Animated.spring(height, {
          toValue: 1,
          delay: index * 100,
          friction: 5,
          useNativeDriver: false,
        }).start();
      });
    }
  }, [activeScreen]);

  // Workout rep counter
  useEffect(() => {
    if (activeScreen === 3) {
      setWorkoutReps([0, 0, 0]);
      const intervals = [
        setInterval(() => setWorkoutReps(prev => [Math.min(prev[0] + 1, 12), prev[1], prev[2]]), 200),
        setInterval(() => setWorkoutReps(prev => [prev[0], Math.min(prev[1] + 1, 12), prev[2]]), 200),
        setInterval(() => setWorkoutReps(prev => [prev[0], prev[1], Math.min(prev[2] + 1, 12)]), 200),
      ];
      return () => intervals.forEach(clearInterval);
    }
  }, [activeScreen]);

  // Meal adding animation
  useEffect(() => {
    if (activeScreen === 3) {
      setMealAdded(false);
      const timer = setTimeout(() => setMealAdded(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [activeScreen]);

  return (
    <View className="relative w-full h-full">
      {/* Screen 1: Journal Entry */}
      <View
        className="absolute inset-0 p-6 transition-opacity duration-500"
        style={{ opacity: activeScreen === 0 ? 1 : 0 }}
      >
        <View className="space-y-4">
          <View className="flex-row items-center gap-2">
            <View
              className="w-8 h-8 rounded-full items-center justify-center"
              style={{ backgroundColor: isWarm ? '#fef3c7' : '#dbeafe' }}
            >
              <NotebookPen size={16} color={primaryColor} />
            </View>
            <Text className="text-sm font-semibold" style={{ color: textColor }}>
              Morning Journal
            </Text>
          </View>

          <View className="space-y-3">
            <View
              className="p-4 rounded-xl"
              style={{ backgroundColor: isWarm ? '#fff' : '#fff' }}
            >
              <Text className="text-xs opacity-60 mb-2" style={{ color: textColor }}>
                What are you grateful for?
              </Text>
              <Text className="text-sm" style={{ color: textColor }}>
                {typing}<Text className="opacity-50">|</Text>
              </Text>
            </View>

            <View
              className="p-4 rounded-xl"
              style={{ backgroundColor: isWarm ? '#fff' : '#fff' }}
            >
              <Text className="text-xs opacity-60 mb-2" style={{ color: textColor }}>
                Today's intention
              </Text>
              <Text className="text-sm" style={{ color: textColor }}>
                Stay present and focus on what matters most
              </Text>
            </View>

            <View className="flex-row gap-2">
              <View
                className="px-3 py-1.5 rounded-full"
                style={{ backgroundColor: isWarm ? '#fef3c7' : '#dbeafe' }}
              >
                <Text className="text-xs font-medium" style={{ color: primaryColor }}>
                  ✓ Completed
                </Text>
              </View>
            </View>
          </View>
        </View>
      </View>

      {/* Screen 2: Habits Progress */}
      <View
        className="absolute inset-0 p-6 transition-opacity duration-500"
        style={{ opacity: activeScreen === 1 ? 1 : 0 }}
      >
        <View className="space-y-4">
          <View className="flex-row items-center gap-2">
            <View
              className="w-8 h-8 rounded-full items-center justify-center"
              style={{ backgroundColor: isWarm ? '#fef3c7' : '#dbeafe' }}
            >
              <Activity size={16} color={primaryColor} />
            </View>
            <Text className="text-sm font-semibold" style={{ color: textColor }}>
              Today's Habits
            </Text>
          </View>

          <View className="space-y-3">
            {[
              { label: 'Morning meditation', streak: 14 },
              { label: 'Read 20 pages', streak: 7 },
              { label: 'Evening walk', streak: 21 },
              { label: 'Journal reflection', streak: 5 },
            ].map((habit, i) => (
              <View
                key={i}
                className="p-4 rounded-xl"
                style={{ backgroundColor: isWarm ? '#fff' : '#fff' }}
              >
                <View className="flex-row items-center justify-between mb-2">
                  <Text className="text-sm font-medium" style={{ color: textColor }}>
                    {habit.label}
                  </Text>
                  {habitChecks[i] ? (
                    <CheckCircle2 size={20} color={isWarm ? '#16a34a' : '#059669'} />
                  ) : (
                    <View className="w-5 h-5 rounded-full border-2" style={{ borderColor: primaryColor, opacity: 0.3 }} />
                  )}
                </View>
                <View className="flex-row items-center gap-2">
                  <View className="flex-1 h-1.5 rounded-full" style={{ backgroundColor: isWarm ? '#f3f0ec' : '#e2e8f0' }}>
                    <View
                      className="h-full rounded-full transition-all"
                      style={{
                        width: habitChecks[i] ? '100%' : '0%',
                        backgroundColor: primaryColor,
                      }}
                    />
                  </View>
                  <Text className="text-xs opacity-60" style={{ color: textColor }}>
                    {habit.streak}d
                  </Text>
                </View>
              </View>
            ))}
          </View>
        </View>
      </View>

      {/* Screen 3: Analytics */}
      <View
        className="absolute inset-0 p-6 transition-opacity duration-500"
        style={{ opacity: activeScreen === 2 ? 1 : 0 }}
      >
        <View className="space-y-4">
          <View className="flex-row items-center gap-2">
            <View
              className="w-8 h-8 rounded-full items-center justify-center"
              style={{ backgroundColor: isWarm ? '#fef3c7' : '#dbeafe' }}
            >
              <BarChart3 size={16} color={primaryColor} />
            </View>
            <Text className="text-sm font-semibold" style={{ color: textColor }}>
              This Week
            </Text>
          </View>

          <View className="grid grid-cols-2 gap-3">
            {[
              { label: 'Current Streak', value: '14', gradient: 'from-green-500 to-emerald-600' },
              { label: 'Weekly Focus', value: '98%', gradient: isWarm ? 'from-warm-crimson-500 to-warm-gold-500' : 'from-cool-blue-500 to-cool-indigo-500' },
              { label: 'Total Habits', value: '8', gradient: 'from-purple-500 to-violet-600' },
              { label: 'Completed', value: '6/7', gradient: 'from-cyan-500 to-teal-600' },
            ].map((stat, i) => (
              <View
                key={i}
                className={`p-4 rounded-xl bg-gradient-to-br ${stat.gradient}`}
                style={{ backgroundColor: primaryColor }}
              >
                <Text className="text-2xl font-bold text-white mb-1">{stat.value}</Text>
                <Text className="text-xs text-white opacity-90">{stat.label}</Text>
              </View>
            ))}
          </View>

          <View
            className="p-4 rounded-xl mt-4"
            style={{ backgroundColor: isWarm ? '#fff' : '#fff' }}
          >
            <Text className="text-xs opacity-60 mb-3" style={{ color: textColor }}>
              7-Day Consistency
            </Text>
            <View className="flex-row justify-between items-end" style={{ height: 80 }}>
              {[0.4, 0.7, 0.95, 0.85, 1.0, 0.9, 0.6].map((targetHeight, i) => (
                <View key={i} className="flex-1 items-center justify-end px-1">
                  <Animated.View
                    className="w-full rounded-t-lg"
                    style={{
                      height: barHeights[i].interpolate({
                        inputRange: [0, 1],
                        outputRange: ['0%', `${targetHeight * 100}%`],
                      }),
                      backgroundColor: targetHeight === 1.0 ? (isWarm ? '#16a34a' : '#059669') : primaryColor,
                      opacity: targetHeight === 1.0 ? 1 : 0.6,
                    }}
                  />
                </View>
              ))}
            </View>
          </View>
        </View>
      </View>

      {/* Screen 4: Meal Logging */}
      <View
        className="absolute inset-0 p-6 transition-opacity duration-500"
        style={{ opacity: activeScreen === 3 ? 1 : 0 }}
      >
        <View className="space-y-4">
          <View className="flex-row items-center gap-2">
            <View
              className="w-8 h-8 rounded-full items-center justify-center"
              style={{ backgroundColor: isWarm ? '#fef3c7' : '#dbeafe' }}
            >
              <Soup size={16} color={primaryColor} />
            </View>
            <Text className="text-sm font-semibold" style={{ color: textColor }}>
              Today's Meals
            </Text>
          </View>

          <View className="space-y-3">
            <View
              className="p-4 rounded-xl"
              style={{ backgroundColor: isWarm ? '#fff' : '#fff' }}
            >
              <View className="flex-row items-center justify-between mb-2">
                <View>
                  <Text className="text-sm font-medium mb-1" style={{ color: textColor }}>
                    🌅 Breakfast
                  </Text>
                  <Text className="text-xs opacity-60" style={{ color: textColor }}>
                    8:30 AM
                  </Text>
                </View>
              </View>
              <Text className="text-sm mt-2" style={{ color: textColor }}>
                Oatmeal with berries & almonds
              </Text>
            </View>

            <View
              className="p-4 rounded-xl"
              style={{ backgroundColor: isWarm ? '#fff' : '#fff' }}
            >
              <View className="flex-row items-center justify-between mb-2">
                <View>
                  <Text className="text-sm font-medium mb-1" style={{ color: textColor }}>
                    🌞 Lunch
                  </Text>
                  <Text className="text-xs opacity-60" style={{ color: textColor }}>
                    12:45 PM
                  </Text>
                </View>
              </View>
              <Text className="text-sm mt-2" style={{ color: textColor }}>
                Grilled chicken salad with avocado
              </Text>
            </View>

            {/* New meal being added animation */}
            {mealAdded && (
              <View
                className="p-4 rounded-xl border-2 border-dashed"
                style={{
                  backgroundColor: isWarm ? '#fef3c7' : '#dbeafe',
                  borderColor: primaryColor,
                }}
              >
                <View className="flex-row items-center justify-between mb-2">
                  <View>
                    <Text className="text-sm font-medium mb-1" style={{ color: textColor }}>
                      🌙 Dinner
                    </Text>
                    <Text className="text-xs opacity-60" style={{ color: textColor }}>
                      Just now
                    </Text>
                  </View>
                  <Text className="text-xs font-semibold" style={{ color: primaryColor }}>
                    +Added
                  </Text>
                </View>
                <Text className="text-sm mt-2" style={{ color: textColor }}>
                  Salmon with roasted vegetables
                </Text>
              </View>
            )}
          </View>
        </View>
      </View>
    </View>
  );
}
