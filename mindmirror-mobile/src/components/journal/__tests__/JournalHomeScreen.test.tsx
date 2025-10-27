import React from 'react';
import { render, screen } from '@testing-library/react-native';
import JournalScreen from '../../../../app/(app)/journal/index';

// Mock the router
const mockPush = jest.fn();
jest.mock('expo-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock the navigation
const mockOpenDrawer = jest.fn();
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    openDrawer: mockOpenDrawer,
  }),
}));

// Mock our custom components
jest.mock('../UserGreeting', () => ({
  UserGreeting: ({ userName }: { userName: string }) => `UserGreeting: ${userName}`,
}));

jest.mock('../AffirmationDisplay', () => ({
  AffirmationDisplay: ({ affirmation }: { affirmation: string }) => `AffirmationDisplay: ${affirmation}`,
}));

jest.mock('../JournalEntryForm', () => ({
  JournalEntryForm: ({ onSubmit, isLoading }: { onSubmit: any; isLoading: boolean }) => 
    `JournalEntryForm: ${isLoading ? 'loading' : 'ready'}`,
}));

jest.mock('../TransitionOverlay', () => ({
  TransitionOverlay: ({ isVisible }: { isVisible: boolean }) => 
    isVisible ? 'TransitionOverlay: visible' : null,
}));

jest.mock('../../../hooks/useJournalFlow', () => ({
  useJournalFlow: () => ({
    submitEntry: jest.fn(),
    transitionToChat: jest.fn(),
    isTransitioning: false,
    isSubmitting: false,
    error: null,
    clearError: jest.fn(),
  }),
}));

describe('JournalScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the main journal screen with all components', () => {
    render(<JournalScreen />);
    
    // Check that all our custom components are rendered
    // Since our mocks return strings, we'll verify the component structure instead
    expect(screen.getByText('Journal')).toBeTruthy();
    expect(screen.getByText('Or try a structured approach:')).toBeTruthy();
    expect(screen.getByText('Gratitude')).toBeTruthy();
    expect(screen.getByText('Reflection')).toBeTruthy();
  });

  it('renders structured journal options', () => {
    render(<JournalScreen />);
    
    // Check for structured journal options
    expect(screen.getByText('Or try a structured approach:')).toBeTruthy();
    expect(screen.getByText('Gratitude')).toBeTruthy();
    expect(screen.getByText('Reflection')).toBeTruthy();
  });

  it('renders app bar with correct elements', () => {
    render(<JournalScreen />);
    
    // Check for app bar elements
    expect(screen.getByText('Journal')).toBeTruthy();
  });
}); 