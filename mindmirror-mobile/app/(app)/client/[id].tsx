import React, { useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { AppBar } from '@/components/common/AppBar'
import { useLocalSearchParams } from 'expo-router'
import { useUserById } from '@/services/api/users'
import { useWorkoutsForUser } from '@/services/api/practices'
import GlobalFab from '@/components/common/GlobalFab'
import { Alert, AlertIcon, AlertText } from '@/components/ui/alert'
import { AlertCircleIcon } from 'lucide-react-native'
import { Avatar, AvatarFallbackText, AvatarImage, AvatarBadge } from '@/components/ui/avatar'
import { Badge, BadgeText } from '@/components/ui/badge'
import { Button, ButtonText } from '@/components/ui/button'

export default function ClientProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const [activeTab, setActiveTab] = useState<'workouts' | 'meals'>('workouts')

  const { data: clientData, loading: clientLoading, error: clientError } = useUserById(id || '')
  const { data: workoutsData, loading: workoutsLoading, error: workoutsError } = useWorkoutsForUser(
    id || '', 
    undefined, // dateFrom
    undefined, // dateTo
    'completed'  // status
  )

  const client = clientData?.userById
  const workouts = workoutsData?.workoutsForUser || []

  // Get last 7 days for recent workouts
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  const recentWorkouts = workouts.filter((workout: any) => 
    new Date(workout.date) >= sevenDaysAgo
  )

  if (clientLoading) {
    return (
      <SafeAreaView className="h-full w-full">
        <VStack className="h-full w-full bg-background-0">
          <AppBar title="Client Profile" showBackButton />
          <VStack className="flex-1 justify-center items-center">
            <Text className="text-typography-600 dark:text-gray-300">Loading client...</Text>
          </VStack>
        </VStack>
      </SafeAreaView>
    )
  }

  if (clientError || !client) {
    return (
      <SafeAreaView className="h-full w-full">
        <VStack className="h-full w-full bg-background-0">
          <AppBar title="Client Profile" showBackButton />
          <VStack className="flex-1 justify-center items-center px-6">
            <Alert action="error" variant="solid">
              <AlertIcon as={AlertCircleIcon} />
              <AlertText>Failed to load client profile</AlertText>
            </Alert>
          </VStack>
        </VStack>
      </SafeAreaView>
    )
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Client Profile" showBackButton />
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {/* Client Header */}
            <VStack space="md" className="items-center">
              <Avatar size="xl">
                <AvatarFallbackText>
                  {client.supabaseId.substring(0, 2).toUpperCase()}
                </AvatarFallbackText>
                <AvatarBadge />
              </Avatar>
              <VStack space="xs" className="items-center">
                <Text className="text-xl font-bold text-typography-900 dark:text-white">
                  Client {client.supabaseId.substring(0, 8)}...
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm">
                  Member since {new Date(client.createdAt).toLocaleDateString()}
                </Text>
                <Badge variant="solid" className="bg-green-100 border-green-200">
                  <BadgeText className="text-green-800">Active Client</BadgeText>
                </Badge>
              </VStack>
            </VStack>

            {/* Quick Stats */}
            <HStack space="md" className="justify-around">
              <VStack className="items-center">
                <Text className="text-2xl font-bold text-typography-900 dark:text-white">
                  {recentWorkouts.length}
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm text-center">
                  Workouts (7d)
                </Text>
              </VStack>
              <VStack className="items-center">
                <Text className="text-2xl font-bold text-typography-900 dark:text-white">
                  {workouts.length}
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm text-center">
                  Total Workouts
                </Text>
              </VStack>
              <VStack className="items-center">
                <Text className="text-2xl font-bold text-typography-900 dark:text-white">
                  0
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm text-center">
                  Meals Logged
                </Text>
              </VStack>
            </HStack>

            {/* Tab Navigation */}
            <HStack space="sm" className="bg-background-50 dark:bg-background-100 rounded-lg p-1">
              <Button
                variant={activeTab === 'workouts' ? 'solid' : 'outline'}
                className={`flex-1 ${activeTab === 'workouts' ? 'bg-primary-600' : 'bg-transparent border-0'}`}
                onPress={() => setActiveTab('workouts')}
              >
                <ButtonText className={activeTab === 'workouts' ? 'text-white' : 'text-typography-600'}>
                  Workouts
                </ButtonText>
              </Button>
              <Button
                variant={activeTab === 'meals' ? 'solid' : 'outline'}
                className={`flex-1 ${activeTab === 'meals' ? 'bg-primary-600' : 'bg-transparent border-0'}`}
                onPress={() => setActiveTab('meals')}
              >
                <ButtonText className={activeTab === 'meals' ? 'text-white' : 'text-typography-600'}>
                  Meals
                </ButtonText>
              </Button>
            </HStack>

            {/* Tab Content */}
            {activeTab === 'workouts' ? (
              <VStack space="md">
                <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                  Completed Workouts
                </Text>
                {workoutsLoading ? (
                  <Text className="text-typography-600 dark:text-gray-300">Loading workouts...</Text>
                ) : workoutsError ? (
                  <Alert action="error" variant="solid">
                    <AlertIcon as={AlertCircleIcon} />
                    <AlertText>Failed to load workouts</AlertText>
                  </Alert>
                ) : workouts.length === 0 ? (
                  <VStack space="md" className="items-center py-8">
                    <Text className="text-typography-600 dark:text-gray-300 text-center">
                      No completed workouts yet.
                    </Text>
                  </VStack>
                ) : (
                  <VStack space="md">
                    {workouts.slice(0, 10).map((workout: any) => (
                      <Box 
                        key={workout.id_} 
                        className="p-4 rounded-xl border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700"
                      >
                        <VStack space="xs">
                          <HStack className="items-center justify-between">
                            <Text className="text-base font-semibold text-typography-900 dark:text-white">
                              {workout.title || 'Workout'}
                            </Text>
                            <Text className="text-typography-500 dark:text-gray-400 text-sm">
                              {new Date(workout.date).toLocaleDateString()}
                            </Text>
                          </HStack>
                          {workout.description && (
                            <Text className="text-typography-600 dark:text-gray-300 text-sm">
                              {workout.description}
                            </Text>
                          )}
                          <HStack className="items-center justify-between">
                            <Badge variant="solid" className="bg-green-100 border-green-200">
                              <BadgeText className="text-green-800">Completed</BadgeText>
                            </Badge>
                            {workout.completedAt && (
                              <Text className="text-typography-500 dark:text-gray-400 text-xs">
                                Completed {new Date(workout.completedAt).toLocaleString()}
                              </Text>
                            )}
                          </HStack>
                        </VStack>
                      </Box>
                    ))}
                    {workouts.length > 10 && (
                      <Text className="text-typography-500 dark:text-gray-400 text-sm text-center">
                        Showing 10 of {workouts.length} workouts
                      </Text>
                    )}
                  </VStack>
                )}
              </VStack>
            ) : (
              <VStack space="md">
                <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                  Meal Log
                </Text>
                <VStack space="md" className="items-center py-8">
                  <Text className="text-typography-600 dark:text-gray-300 text-center">
                    Meal tracking not yet implemented.
                  </Text>
                  <Text className="text-typography-500 dark:text-gray-400 text-sm text-center">
                    This feature will show the client's logged meals and nutrition data.
                  </Text>
                </VStack>
              </VStack>
            )}
          </VStack>
        </ScrollView>
      </VStack>
      <GlobalFab />
    </SafeAreaView>
  )
} 