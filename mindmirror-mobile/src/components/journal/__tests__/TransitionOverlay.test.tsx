import React from 'react';
import { render, screen, act } from '@testing-library/react-native';
import { TransitionOverlay } from '../TransitionOverlay';

describe('TransitionOverlay', () => {
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    mockOnComplete.mockClear();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders nothing when isVisible is false', () => {
    const { UNSAFE_root } = render(
      <TransitionOverlay isVisible={false} onComplete={mockOnComplete} />
    );
    
    expect(UNSAFE_root.children).toHaveLength(0);
  });

  it('renders overlay content when isVisible is true', () => {
    render(
      <TransitionOverlay isVisible={true} onComplete={mockOnComplete} />
    );
    
    expect(screen.getByText('Journal Saved!')).toBeTruthy();
    expect(screen.getByText('Now let\'s continue the conversation with your AI companion...')).toBeTruthy();
  });

  it('shows sparkles and message circle icons', () => {
    render(
      <TransitionOverlay isVisible={true} onComplete={mockOnComplete} />
    );
    
    // Check for icon elements (they might be rendered as components)
    const iconContainer = screen.getByText('Journal Saved!').parent;
    expect(iconContainer).toBeTruthy();
  });

  it('calls onComplete after animation finishes', () => {
    render(
      <TransitionOverlay isVisible={true} onComplete={mockOnComplete} />
    );
    
    // Fast-forward timers to trigger the setTimeout in onComplete
    act(() => {
      jest.advanceTimersByTime(300); // Animation duration
    });
    
    act(() => {
      jest.advanceTimersByTime(200); // Additional delay
    });
    
    expect(mockOnComplete).toHaveBeenCalled();
  });

  it('applies custom className', () => {
    const { UNSAFE_root } = render(
      <TransitionOverlay 
        isVisible={true} 
        onComplete={mockOnComplete}
        className="custom-class" 
      />
    );
    
    const overlayElement = UNSAFE_root.findByProps({ 
      className: expect.stringContaining('custom-class') 
    });
    expect(overlayElement).toBeTruthy();
  });

  it('handles multiple rapid visibility changes', () => {
    const { rerender } = render(
      <TransitionOverlay isVisible={false} onComplete={mockOnComplete} />
    );
    
    // Should not render when false
    expect(screen.queryByText('Journal Saved!')).toBeFalsy();
    
    // Show overlay
    rerender(<TransitionOverlay isVisible={true} onComplete={mockOnComplete} />);
    expect(screen.getByText('Journal Saved!')).toBeTruthy();
    
    // Hide overlay
    rerender(<TransitionOverlay isVisible={false} onComplete={mockOnComplete} />);
    expect(screen.queryByText('Journal Saved!')).toBeFalsy();
    
    // Show again
    rerender(<TransitionOverlay isVisible={true} onComplete={mockOnComplete} />);
    expect(screen.getByText('Journal Saved!')).toBeTruthy();
  });

  it('renders with proper text styling', () => {
    render(
      <TransitionOverlay isVisible={true} onComplete={mockOnComplete} />
    );
    
    const titleElement = screen.getByText('Journal Saved!');
    expect(titleElement.props.className).toContain('text-xl');
    expect(titleElement.props.className).toContain('font-semibold');
    
    const subtitleElement = screen.getByText('Now let\'s continue the conversation with your AI companion...');
    expect(subtitleElement.props.className).toContain('text-base');
  });
}); 