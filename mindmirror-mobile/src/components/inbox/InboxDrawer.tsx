import React from 'react'
import { Dimensions } from 'react-native'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Button, ButtonText } from '@/components/ui/button'
import { Pressable } from '@/components/ui/pressable'
import { ScrollView } from '@/components/ui/scroll-view'
import { Modal, ModalBackdrop, ModalContent } from '@/components/ui/modal'
import { Heading } from '@/components/ui/heading'
import { CloseIcon, Icon } from '@/components/ui/icon'
import { InboxIcon, XIcon } from 'lucide-react-native'
import { useMyPendingCoachingRequests, useAcceptCoaching } from '@/services/api/users'
import { useToast } from '@/components/ui/toast'
import InboxMessageCard from './InboxMessageCard'

interface InboxDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export default function InboxDrawer({ isOpen, onClose }: InboxDrawerProps) {
  const toast = useToast()
  const { data: requestsData, loading, refetch } = useMyPendingCoachingRequests()
  const [acceptCoaching] = useAcceptCoaching()
  
  const requests = requestsData?.myPendingCoachingRequests || []
  const screenWidth = Dimensions.get('window').width

  const handleAcceptRequest = async (coachUserId: string) => {
    try {
      await acceptCoaching({
        variables: { coachUserId }
      })
      
      toast.show({
        description: "Coaching request accepted!",
      })
      
      await refetch()
    } catch (error: any) {
      toast.show({
        description: error.message || "Failed to accept coaching request.",
        action: "error",
      })
    }
  }

  const handleRejectRequest = async (requestId: string) => {
    // TODO: Implement reject functionality
    toast.show({
      description: "Reject functionality coming soon.",
    })
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalBackdrop />
      <ModalContent 
        className="absolute right-0 top-0 h-full w-80 max-w-[85%] rounded-l-xl rounded-r-none m-0"
        style={{ 
          marginRight: 0,
          marginTop: 0,
          marginBottom: 0,
          width: Math.min(320, screenWidth * 0.85)
        }}
      >
        {/* Header */}
        <Box className="p-4 border-b border-border-200 bg-background-0">
          <HStack className="items-center justify-between">
            <HStack className="items-center" space="sm">
              <Icon as={InboxIcon} size="md" className="text-primary-600" />
              <Heading size="lg">Inbox</Heading>
            </HStack>
            <Pressable onPress={onClose} className="p-2">
              <Icon as={XIcon} size="md" className="text-typography-500" />
            </Pressable>
          </HStack>
        </Box>

        {/* Content */}
        <ScrollView className="flex-1 p-4">
          <VStack space="md">
            {loading ? (
              <Text className="text-center text-typography-500 py-8">Loading requests...</Text>
            ) : requests.length === 0 ? (
              <Box className="py-12">
                <VStack className="items-center" space="md">
                  <Icon as={InboxIcon} size="xl" className="text-typography-300" />
                  <Text className="text-center text-typography-500">
                    No pending coaching requests
                  </Text>
                  <Text className="text-center text-typography-400 text-sm">
                    When coaches send you requests, they'll appear here
                  </Text>
                </VStack>
              </Box>
            ) : (
              <>
                <Text className="text-sm font-medium text-typography-700 mb-2">
                  Pending Requests ({requests.length})
                </Text>
                {requests.map((request: any) => (
                  <InboxMessageCard
                    key={request.id_}
                    request={request}
                    onAccept={() => handleAcceptRequest(request.coach.id_)}
                    onReject={() => handleRejectRequest(request.id_)}
                  />
                ))}
              </>
            )}
          </VStack>
        </ScrollView>
      </ModalContent>
    </Modal>
  )
} 