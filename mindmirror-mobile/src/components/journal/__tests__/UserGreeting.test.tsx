import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { UserGreeting } from '../UserGreeting';

// Mock the date to have consistent test results
const mockDate = new Date('2024-01-15T10:00:00Z');
const originalDate = global.Date;

beforeAll(() => {
  global.Date = class extends Date {
    constructor(...args: any[]) {
      if (args.length === 0) {
        return mockDate;
      }
      return new originalDate(...args);
    }
  } as DateConstructor;
});

afterAll(() => {
  global.Date = originalDate;
});

describe('UserGreeting', () => {
  it('renders morning greeting without user name', () => {
    render(<UserGreeting />);
    
    expect(screen.getByText('Good morning')).toBeTruthy();
    expect(screen.getByText('Ready to start your journaling journey?')).toBeTruthy();
  });

  it('renders greeting with user name', () => {
    render(<UserGreeting userName="John" />);
    
    expect(screen.getByText('Good morning, John')).toBeTruthy();
  });

  it('shows appropriate message when no last entry date', () => {
    render(<UserGreeting userName="Jane" />);
    
    expect(screen.getByText('Ready to start your journaling journey?')).toBeTruthy();
  });

  it('shows "day" message for entries from yesterday', () => {
    const yesterday = new Date('2024-01-14T10:00:00Z');
    render(<UserGreeting userName="Bob" lastEntryDate={yesterday} />);
    
    expect(screen.getByText("Welcome back! It's been a day since your last entry.")).toBeTruthy();
  });

  it('shows "days" message for entries from multiple days ago', () => {
    const threeDaysAgo = new Date('2024-01-12T10:00:00Z');
    render(<UserGreeting userName="Alice" lastEntryDate={threeDaysAgo} />);
    
    expect(screen.getByText("Welcome back! It's been 3 days since your last entry.")).toBeTruthy();
  });

  it('shows generic message for entries from more than a week ago', () => {
    const tenDaysAgo = new Date('2024-01-05T10:00:00Z');
    render(<UserGreeting userName="Charlie" lastEntryDate={tenDaysAgo} />);
    
    expect(screen.getByText("Welcome back! It's been a while since your last entry.")).toBeTruthy();
  });

  it('applies custom className', () => {
    const { getByText } = render(<UserGreeting className="custom-class" />);
    
    const greetingElement = getByText('Good morning');
    expect(greetingElement.props.className).toContain('custom-class');
  });

  it('handles different times of day correctly', () => {
    // Test afternoon
    const afternoonDate = new Date('2024-01-15T14:00:00Z');
    global.Date = class extends Date {
      constructor() {
        return afternoonDate;
      }
    } as DateConstructor;

    const { rerender } = render(<UserGreeting />);
    expect(screen.getByText('Good afternoon')).toBeTruthy();

    // Test evening
    const eveningDate = new Date('2024-01-15T20:00:00Z');
    global.Date = class extends Date {
      constructor() {
        return eveningDate;
      }
    } as DateConstructor;

    rerender(<UserGreeting />);
    expect(screen.getByText('Good evening')).toBeTruthy();
  });
}); 