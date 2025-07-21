import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { JournalTypeSelector, JournalType } from '../JournalTypeSelector';

describe('JournalTypeSelector', () => {
  const mockOnGratitudePress = jest.fn();
  const mockOnReflectionPress = jest.fn();

  beforeEach(() => {
    mockOnGratitudePress.mockClear();
    mockOnReflectionPress.mockClear();
  });

  it('renders both journal type options', () => {
    render(
      <JournalTypeSelector 
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
      />
    );
    
    expect(screen.getByText('Gratitude')).toBeTruthy();
    expect(screen.getByText('Reflection')).toBeTruthy();
    expect(screen.getByText('What are you grateful for?')).toBeTruthy();
    expect(screen.getByText('Reflect on your day')).toBeTruthy();
  });

  it('calls onGratitudePress when gratitude button is pressed', () => {
    render(
      <JournalTypeSelector 
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
      />
    );
    
    fireEvent.press(screen.getByText('Gratitude'));
    expect(mockOnGratitudePress).toHaveBeenCalled();
  });

  it('calls onReflectionPress when reflection button is pressed', () => {
    render(
      <JournalTypeSelector 
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
      />
    );
    
    fireEvent.press(screen.getByText('Reflection'));
    expect(mockOnReflectionPress).toHaveBeenCalled();
  });

    it('applies custom className', () => {
    const { UNSAFE_root } = render(
      <JournalTypeSelector
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
        className="custom-class"
      />
    );

    const mainContainer = UNSAFE_root.findByProps({
      className: expect.stringContaining('custom-class')
    });
    expect(mainContainer).toBeTruthy();
  });

  it('has proper accessibility structure', () => {
    const { UNSAFE_root } = render(
      <JournalTypeSelector 
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
      />
    );
    
    // Check that buttons are pressable
    const pressableElements = UNSAFE_root.findAllByProps({ 
      onPress: expect.any(Function) 
    });
    expect(pressableElements.length).toBe(2);
  });

  it('renders with consistent styling', () => {
    render(
      <JournalTypeSelector 
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
      />
    );
    
    // Check gratitude button styling
    const gratitudeButton = screen.getByText('Gratitude').parent;
    expect(gratitudeButton.props.className).toContain('bg-blue-50');
    
    // Check reflection button styling
    const reflectionButton = screen.getByText('Reflection').parent;
    expect(reflectionButton.props.className).toContain('bg-indigo-50');
  });
}); 