import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { AppBar } from '@/components/common/AppBar'
import { Icon } from '@/components/ui/icon'
import { InboxIcon } from 'lucide-react-native'
import { useMyPendingCoachingRequests, useAcceptCoaching, useRejectCoaching } from '@/services/api/users'
import { Toast, ToastTitle, useToast } from '@/components/ui/toast'
import InboxMessageCard from '@/components/inbox/InboxMessageCard'

export default function InboxScreen() {
  const toast = useToast()
  const { data: requestsData, loading, refetch } = useMyPendingCoachingRequests()
  const [acceptCoaching] = useAcceptCoaching()
  const [rejectCoaching] = useRejectCoaching()
  
  const requests = requestsData?.myPendingCoachingRequests || []

  const handleAcceptRequest = async (coachUserId: string) => {
    try {
      await acceptCoaching({
        variables: { coachUserId }
      })
      
      toast.show({
        placement: "bottom right",
        render: ({ id }) => (
          <Toast nativeID={id} action="success">
            <ToastTitle>Coaching request accepted!</ToastTitle>
          </Toast>
        ),
      })
      
      await refetch()
    } catch (error: any) {
      toast.show({
        placement: "bottom right",
        render: ({ id }) => (
          <Toast nativeID={id} action="error">
            <ToastTitle>{error.message || "Failed to accept coaching request."}</ToastTitle>
          </Toast>
        ),
      })
    }
  }

  const handleRejectRequest = async (coachUserId: string) => {
    try {
      await rejectCoaching({
        variables: { coachUserId }
      })
      
      toast.show({
        placement: "bottom right",
        render: ({ id }) => (
          <Toast nativeID={id} action="success">
            <ToastTitle>Coaching request declined.</ToastTitle>
          </Toast>
        ),
      })
      
      await refetch()
    } catch (error: any) {
      toast.show({
        placement: "bottom right",
        render: ({ id }) => (
          <Toast nativeID={id} action="error">
            <ToastTitle>{error.message || "Failed to decline coaching request."}</ToastTitle>
          </Toast>
        ),
      })
    }
  }

  return (
    <SafeAreaView className="flex-1 bg-background-0">
      <AppBar title="Inbox" />
      
      <ScrollView className="flex-1 px-4 py-6">
        <VStack space="lg">
          {/* Header */}
          <HStack className="items-center" space="sm">
            <Icon as={InboxIcon} size="lg" className="text-primary-600" />
            <VStack>
              <Text className="text-xl font-bold text-typography-900">
                Coaching Requests
              </Text>
              <Text className="text-sm text-typography-600">
                Manage your incoming coaching invitations
              </Text>
            </VStack>
          </HStack>

          {/* Content */}
          {loading ? (
            <Text className="text-center text-typography-500 py-8">Loading requests...</Text>
          ) : requests.length === 0 ? (
            <Box className="py-16">
              <VStack className="items-center" space="lg">
                                 <Icon as={InboxIcon} size="xl" className="text-typography-300" />
                <VStack className="items-center" space="sm">
                  <Text className="text-center text-typography-600 font-medium">
                    No pending coaching requests
                  </Text>
                  <Text className="text-center text-typography-400 text-sm max-w-64">
                    When coaches send you requests, they'll appear here for you to accept or decline
                  </Text>
                </VStack>
              </VStack>
            </Box>
          ) : (
            <VStack space="md">
              <Text className="text-sm font-medium text-typography-700">
                Pending Requests ({requests.length})
              </Text>
              {requests.map((request: any) => (
                <InboxMessageCard
                  key={request.id_}
                  request={request}
                  onAccept={() => handleAcceptRequest(request.coach.id_)}
                  onReject={() => handleRejectRequest(request.coach.id_)}
                />
              ))}
            </VStack>
          )}
        </VStack>
      </ScrollView>
    </SafeAreaView>
  )
} 