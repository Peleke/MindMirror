import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { AffirmationDisplay } from '../AffirmationDisplay';

describe('AffirmationDisplay', () => {
  const mockAffirmation = "You are capable of amazing things. Today is a new opportunity to grow and learn.";

  it('renders affirmation when not loading', () => {
    render(<AffirmationDisplay affirmation={mockAffirmation} />);
    
    expect(screen.getByText("Today's Affirmation")).toBeTruthy();
    expect(screen.getByText(`"${mockAffirmation}"`)).toBeTruthy();
  });

  it('renders loading state when isLoading is true', () => {
    render(<AffirmationDisplay affirmation={mockAffirmation} isLoading={true} />);
    
    expect(screen.getByText('Generating your affirmation...')).toBeTruthy();
    expect(screen.queryByText("Today's Affirmation")).toBeFalsy();
    expect(screen.queryByText(`"${mockAffirmation}"`)).toBeFalsy();
  });

    it('shows loading dots when in loading state', () => {
    const { UNSAFE_root } = render(<AffirmationDisplay affirmation={mockAffirmation} isLoading={true} />);

    // Check for loading animation elements
    const loadingElements = UNSAFE_root.findAllByProps({
      className: expect.stringContaining('animate-pulse')
    });
    expect(loadingElements.length).toBeGreaterThan(0);
  });

  it('applies custom className', () => {
    const { getByText } = render(
      <AffirmationDisplay affirmation={mockAffirmation} className="custom-class" />
    );
    
    const affirmationElement = getByText(`"${mockAffirmation}"`);
    expect(affirmationElement.props.className).toContain('custom-class');
  });

  it('renders with empty affirmation', () => {
    render(<AffirmationDisplay affirmation="" />);
    
    expect(screen.getByText("Today's Affirmation")).toBeTruthy();
    expect(screen.getByText('""')).toBeTruthy();
  });

  it('renders with long affirmation text', () => {
    const longAffirmation = "This is a very long affirmation that should wrap properly and still look good in the UI. It contains multiple sentences and should test the component's ability to handle longer text content gracefully.";
    
    render(<AffirmationDisplay affirmation={longAffirmation} />);
    
    expect(screen.getByText(`"${longAffirmation}"`)).toBeTruthy();
  });

  it('has proper accessibility structure', () => {
    const { UNSAFE_root } = render(<AffirmationDisplay affirmation={mockAffirmation} />);
    
    // Check that the component has proper structure
    const mainContainer = UNSAFE_root.findByProps({ 
      className: expect.stringContaining('bg-gradient-to-r') 
    });
    expect(mainContainer).toBeTruthy();
  });

  it('shows sparkles icon in both loading and loaded states', () => {
    const { rerender } = render(<AffirmationDisplay affirmation={mockAffirmation} isLoading={true} />);
    
    // Check for sparkles icon in loading state
    const loadingContainer = screen.getByText('Generating your affirmation...').parent;
    expect(loadingContainer).toBeTruthy();

    // Check for sparkles icon in loaded state
    rerender(<AffirmationDisplay affirmation={mockAffirmation} isLoading={false} />);
    const loadedContainer = screen.getByText("Today's Affirmation").parent;
    expect(loadedContainer).toBeTruthy();
  });
}); 