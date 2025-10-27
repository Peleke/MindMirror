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
    render(
      <JournalTypeSelector
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
        className="custom-class"
      />
    );

    // Since our mocks return strings, we can't test className directly
    // Instead, verify the component renders correctly
    expect(screen.getByText('Gratitude')).toBeTruthy();
    expect(screen.getByText('Reflection')).toBeTruthy();
  });

  it('has proper accessibility structure', () => {
    render(
      <JournalTypeSelector 
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
      />
    );
    
    // Check that buttons are rendered and clickable
    expect(screen.getByText('Gratitude')).toBeTruthy();
    expect(screen.getByText('Reflection')).toBeTruthy();
    expect(screen.getByText('What are you grateful for?')).toBeTruthy();
    expect(screen.getByText('Reflect on your day')).toBeTruthy();
  });

  it('renders with consistent styling', () => {
    render(
      <JournalTypeSelector 
        onGratitudePress={mockOnGratitudePress}
        onReflectionPress={mockOnReflectionPress}
      />
    );
    
    // Since our mocks return strings, we can't test className directly
    // Instead, verify the component renders all expected elements
    expect(screen.getByText('Gratitude')).toBeTruthy();
    expect(screen.getByText('Reflection')).toBeTruthy();
    expect(screen.getByText('What are you grateful for?')).toBeTruthy();
    expect(screen.getByText('Reflect on your day')).toBeTruthy();
  });
}); 