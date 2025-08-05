import { Button, ButtonText } from '@/components/ui/button';

interface DiscussMemoryButtonProps {
  onPress: () => void;
}

export function DiscussMemoryButton({ onPress }: DiscussMemoryButtonProps) {
  return (
    <Button
      onPress={onPress}
      className="mt-6 bg-primary-500"
      variant="solid"
    >
      <ButtonText className="text-white font-medium">
        💬 Discuss this memory...
      </ButtonText>
    </Button>
  );
} 