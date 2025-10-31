import React, { useState } from 'react';
import { Text } from '@/components/ui/text';
import { Box } from '@/components/ui/box';
import { VStack } from '@/components/ui/vstack';
import { HStack } from '@/components/ui/hstack';
import { Button, ButtonText } from '@/components/ui/button';
import { Textarea, TextareaInput } from '@/components/ui/textarea';
import { Icon } from '@/components/ui/icon';
import { Send } from 'lucide-react-native';
import { JournalType } from './JournalTypeSelector';
import { FormControl, FormControlLabel, FormControlLabelText } from '@/components/ui/form-control';

export interface JournalEntryFormProps {
  // The original onSubmit is now onSaveAndChat
  onSaveAndChat: (content: string) => void;
  // A new handler for just saving
  onSave: (content: string) => void;
  isLoading?: boolean;
  className?: string;
}

export function JournalEntryForm({
  onSaveAndChat,
  onSave,
  isLoading = false,
  className = '',
}: JournalEntryFormProps) {
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSaveAndChat = () => {
    const trimmedContent = content.trim();
    
    if (!trimmedContent) {
      setError('Please write something in your journal');
      return;
    }

    if (trimmedContent.length < 10) {
      setError('Please write at least 10 characters');
      return;
    }

    setError(null);
    onSaveAndChat(trimmedContent);
  };

  const handleSave = () => {
    const trimmedContent = content.trim();
    
    if (!trimmedContent) {
      setError('Please write something in your journal');
      return;
    }

    if (trimmedContent.length < 10) {
      setError('Please write at least 10 characters');
      return;
    }

    setError(null);
    onSave(trimmedContent);
  };

  const handleContentChange = (text: string) => {
    setContent(text);
    if (error) {
      setError(null);
    }
  };

  return (
    <VStack className={`space-y-4 ${className}`}>
      <Box className="bg-white dark:bg-gray-800 rounded-lg border border-border-200 dark:border-border-700 p-4">
        <VStack className="space-y-3">
          <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
            Your Thoughts
          </Text>
          <Textarea className="bg-background-50 dark:bg-background-100 flex-1">
                              <TextareaInput
                    placeholder="What's on your mind today? Write freely about your thoughts, feelings, or experiences..."
                    value={content}
                    onChangeText={handleContentChange}
                    numberOfLines={8}
                    textAlignVertical="top"
                    style={{ 
                      flex: 1, 
                      minHeight: 200,
                      fontSize: 16,
                      lineHeight: 24
                    }}
                    multiline
                    maxLength={2000}
                  />
          </Textarea>
          
          {error && (
            <Box className="p-3 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-700">
              <Text className="text-red-700 dark:text-red-300 text-sm">
                {error}
              </Text>
            </Box>
          )}

          <VStack space="sm">
            <Text className="text-xs text-typography-500 dark:text-gray-400">
              {content.length}/2000 characters
            </Text>
            <HStack space="sm">
              <Button onPress={handleSave} className="flex-1 bg-green-600" isDisabled={isLoading || !content.trim()}>
                <ButtonText>Save</ButtonText>
              </Button>
              <Button onPress={handleSaveAndChat} className="flex-1 bg-green-700" isDisabled={isLoading || !content.trim()}>
                <ButtonText>Save and Chat</ButtonText>
              </Button>
            </HStack>
          </VStack>
        </VStack>
      </Box>
    </VStack>
  );
} 