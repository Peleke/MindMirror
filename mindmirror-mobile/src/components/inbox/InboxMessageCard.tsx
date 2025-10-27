import React from 'react'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Button, ButtonText } from '@/components/ui/button'
import { Avatar, AvatarFallbackText } from '@/components/ui/avatar'
import { Icon } from '@/components/ui/icon'
import { CheckIcon, XIcon } from 'lucide-react-native'

interface InboxMessageCardProps {
  request: {
    id_: string
    coach: {
      id_: string
      supabaseId: string
      email?: string
      firstName?: string
      lastName?: string
    }
    createdAt: string
  }
  onAccept: () => void
  onReject: () => void
}

export default function InboxMessageCard({ request, onAccept, onReject }: InboxMessageCardProps) {
  const coachName = request.coach.firstName && request.coach.lastName 
    ? `${request.coach.firstName} ${request.coach.lastName}`
    : request.coach.email || 'Unknown Coach'
    
  const coachInitials = request.coach.firstName && request.coach.lastName
    ? `${request.coach.firstName[0]}${request.coach.lastName[0]}`
    : request.coach.email?.[0] || 'C'

  const timeAgo = new Date(request.createdAt).toLocaleDateString()

  return (
    <Box className="p-4 bg-background-0 border border-border-200 rounded-lg shadow-sm">
      <VStack space="md">
        {/* Header with coach info */}
        <HStack className="items-center" space="md">
          <Avatar size="md" className="bg-primary-100">
            <AvatarFallbackText className="text-primary-700 font-semibold">
              {coachInitials}
            </AvatarFallbackText>
          </Avatar>
          
          <VStack className="flex-1">
            <Text className="font-semibold text-typography-900">
              Coaching Request
            </Text>
            <Text className="text-sm text-typography-600">
              from {coachName}
            </Text>
            <Text className="text-xs text-typography-400">
              {timeAgo}
            </Text>
          </VStack>
        </HStack>

        {/* Message */}
        <Box className="p-3 bg-background-50 rounded-md">
          <Text className="text-sm text-typography-700">
            {coachName} would like to be your coach. They'll be able to assign workout programs and track your progress.
          </Text>
        </Box>

        {/* Action Buttons */}
        <HStack space="sm">
          <Button
            variant="outline"
            onPress={onReject}
            className="flex-1 border-red-300"
          >
            <HStack className="items-center" space="xs">
              <Icon as={XIcon} size="sm" className="text-red-600" />
              <ButtonText className="text-red-600">Decline</ButtonText>
            </HStack>
          </Button>
          
          <Button
            onPress={onAccept}
            className="flex-1 bg-green-600"
          >
            <HStack className="items-center" space="xs">
              <Icon as={CheckIcon} size="sm" className="text-white" />
              <ButtonText className="text-white">Accept</ButtonText>
            </HStack>
          </Button>
        </HStack>
      </VStack>
    </Box>
  )
} 