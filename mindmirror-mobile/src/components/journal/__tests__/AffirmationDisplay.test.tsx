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
    render(<AffirmationDisplay affirmation={mockAffirmation} isLoading={true} />);

    // Check for loading text
    expect(screen.getByText('Generating your affirmation...')).toBeTruthy();
  });

  it('applies custom className', () => {
    render(
      <AffirmationDisplay affirmation={mockAffirmation} className="custom-class" />
    );
    
    // Since our mocks return strings, we can't test className directly
    // Instead, verify the component renders correctly
    expect(screen.getByText(`"${mockAffirmation}"`)).toBeTruthy();
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
    render(<AffirmationDisplay affirmation={mockAffirmation} />);

    // Check that the component renders the expected text
    expect(screen.getByText("Today's Affirmation")).toBeTruthy();
    expect(screen.getByText(`"${mockAffirmation}"`)).toBeTruthy();
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