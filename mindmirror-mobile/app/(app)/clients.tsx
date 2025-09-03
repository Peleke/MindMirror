import React, { useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Button, ButtonText } from '@/components/ui/button'
import { Pressable } from '@/components/ui/pressable'
import { AppBar } from '@/components/common/AppBar'
import { useMyClients, useRequestCoaching, useSearchUsers } from '@/services/api/users'
import { useRouter } from 'expo-router'
import { Modal, ModalBackdrop, ModalContent, ModalHeader, ModalCloseButton, ModalBody, ModalFooter } from '@/components/ui/modal'
import { Heading } from '@/components/ui/heading'
import { CloseIcon, Icon } from '@/components/ui/icon'
import { Alert, AlertIcon, AlertText } from '@/components/ui/alert'
import { CheckCircleIcon, AlertCircleIcon, UserIcon, SearchIcon } from 'lucide-react-native'
import { Toast, ToastTitle, useToast } from '@/components/ui/toast'
import { Avatar, AvatarFallbackText } from '@/components/ui/avatar'

export default function ClientsScreen() {
  const router = useRouter()
  const toast = useToast()
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [clientEmail, setClientEmail] = useState('')
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null)
  
  // Data fetching
  const { data: clientsData, loading, refetch } = useMyClients()
  const { data: searchData } = useSearchUsers(clientEmail)
  const [requestCoaching, { loading: requestLoading }] = useRequestCoaching()
  
  const clients = clientsData?.myClients || []
  const searchResults = searchData?.searchUsers || []
  
  // Filter clients based on search
  const filteredClients = clients.filter((client: any) =>
    client.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    `${client.firstName || ''} ${client.lastName || ''}`.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleAddClient = async () => {
    if (!clientEmail.trim()) {
              toast.show({
          placement: "bottom right",
          render: ({ id }) => (
            <Toast nativeID={id} action="error">
              <ToastTitle>Please enter a client email address.</ToastTitle>
            </Toast>
          ),
        })
      return
    }

    try {
      await requestCoaching({
        variables: { clientEmail: clientEmail.trim() }
      })
      
      toast.show({
        placement: "bottom right",
        render: ({ id }) => (
          <Toast nativeID={id} action="success">
            <ToastTitle>Coaching request sent successfully!</ToastTitle>
          </Toast>
        ),
      })
      
      setClientEmail('')
      setSelectedUserId(null)
      setShowAddModal(false)
      await refetch()
    } catch (error: any) {
      toast.show({
        placement: "bottom right",
        render: ({ id }) => (
          <Toast nativeID={id} action="error">
            <ToastTitle>{error.message || "Failed to send coaching request."}</ToastTitle>
          </Toast>
        ),
      })
    }
  }

  const handleClientPress = (client: any) => {
    router.push(`/client/${client.id_}`)
  }

  return (
    <SafeAreaView className="flex-1 bg-background-0">
      <AppBar title="Clients" />
      
      <VStack className="flex-1 px-4 py-6" space="lg">
        {/* Search Bar */}
        <Box>
          <Input className="w-full">
            <InputField
              placeholder="Search clients by name or email..."
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </Input>
        </Box>

        {/* Add Client Button */}
        <Button
          onPress={() => setShowAddModal(true)}
          className="w-full"
        >
          <ButtonText>+ Add Client</ButtonText>
        </Button>

        {/* Clients List */}
        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
          <VStack space="md">
            {loading ? (
              <Text className="text-center text-typography-500 py-8">Loading clients...</Text>
            ) : filteredClients.length === 0 ? (
              <Box className="py-12">
                <VStack className="items-center" space="md">
                  <Icon as={UserIcon} size="xl" className="text-typography-300" />
                  <Text className="text-center text-typography-500">
                    {searchQuery ? 'No clients found matching your search.' : 'No clients yet. Add your first client to get started!'}
                  </Text>
                </VStack>
              </Box>
            ) : (
              filteredClients.map((client: any) => (
                <Pressable
                  key={client.id_}
                  onPress={() => handleClientPress(client)}
                  className="p-4 bg-background-50 border border-border-200 rounded-lg"
                >
                  <HStack className="items-center" space="md">
                    <Avatar size="md">
                      <AvatarFallbackText>
                        {(client.firstName?.[0] || client.email?.[0] || 'C').toUpperCase()}
                      </AvatarFallbackText>
                    </Avatar>
                    <VStack className="flex-1">
                      <Text className="font-semibold text-typography-900">
                        {client.firstName && client.lastName 
                          ? `${client.firstName} ${client.lastName}`
                          : (client.email || 'Unknown Client')
                        }
                      </Text>
                      {client.email && (
                        <Text className="text-sm text-typography-500">{client.email}</Text>
                      )}
                    </VStack>
                    <Icon as={UserIcon} size="sm" className="text-typography-400" />
                  </HStack>
                </Pressable>
              ))
            )}
          </VStack>
        </ScrollView>
      </VStack>

      {/* Add Client Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)}>
        <ModalBackdrop />
        <ModalContent className="w-[90%] max-w-md">
          <ModalHeader>
            <Heading size="lg">Add Client</Heading>
            <ModalCloseButton>
              <Icon as={CloseIcon} />
            </ModalCloseButton>
          </ModalHeader>
          
          <ModalBody>
            <VStack space="lg">
              <Text className="text-typography-600">
                Enter your client's email address to send them a coaching request.
              </Text>
              
              <Input>
                <InputField
                  placeholder="client@example.com"
                  value={clientEmail}
                  onChangeText={setClientEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </Input>

              {/* Search Results Preview */}
              {clientEmail.length > 2 && searchResults.length > 0 && (
                <Box className="max-h-40">
                  <Text className="text-sm font-medium text-typography-700 mb-2">Existing Users:</Text>
                  <ScrollView>
                    <VStack space="xs">
                      {searchResults.slice(0, 3).map((user: any) => (
                        <Pressable
                          key={user.id_}
                          onPress={() => {
                            setClientEmail(user.email || '')
                            setSelectedUserId(user.id_)
                          }}
                          className={`p-2 rounded border ${
                            selectedUserId === user.id_
                              ? 'bg-primary-50 border-primary-300 border-2'
                              : 'bg-background-100 border-border-200'
                          }`}
                        >
                          <Text className="text-sm">
                            {user.firstName && user.lastName 
                              ? `${user.firstName} ${user.lastName} (${user.email})`
                              : user.email
                            }
                          </Text>
                        </Pressable>
                      ))}
                    </VStack>
                  </ScrollView>
                </Box>
              )}
            </VStack>
          </ModalBody>
          
          <ModalFooter>
            <HStack space="md" className="w-full">
              <Button
                variant="outline"
                onPress={() => {
                  setShowAddModal(false)
                  setClientEmail('')
                  setSelectedUserId(null)
                }}
                className="flex-1"
              >
                <ButtonText>Cancel</ButtonText>
              </Button>
              <Button
                onPress={handleAddClient}
                disabled={requestLoading || !clientEmail.trim()}
                className="flex-1"
              >
                <ButtonText>
                  {requestLoading ? 'Sending...' : 'Send Request'}
                </ButtonText>
              </Button>
            </HStack>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </SafeAreaView>
  )
} 