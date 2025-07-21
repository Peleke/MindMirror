import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { JournalEntryForm } from '../JournalEntryForm';
import { JournalType } from '../JournalTypeSelector';

describe('JournalEntryForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders form with correct placeholder', () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    expect(screen.getByText('Your Thoughts')).toBeTruthy();
    expect(screen.getByPlaceholderText("What's on your mind today? Write freely about your thoughts, feelings, or experiences...")).toBeTruthy();
    expect(screen.getByText('Save & Continue')).toBeTruthy();
  });

  it('shows character count', () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    expect(screen.getByText('0/2000 characters')).toBeTruthy();
  });

  it('updates character count when typing', () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const textarea = screen.getByPlaceholderText("What's on your mind today? Write freely about your thoughts, feelings, or experiences...");
    fireEvent.changeText(textarea, 'Hello world');
    
    expect(screen.getByText('11/2000 characters')).toBeTruthy();
  });

  it('shows error when submitting empty content', async () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const submitButton = screen.getByText('Save & Continue');
    fireEvent.press(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please write something in your journal')).toBeTruthy();
    });
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('shows error when content is too short', async () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const textarea = screen.getByPlaceholderText("What's on your mind today? Write freely about your thoughts, feelings, or experiences...");
    fireEvent.changeText(textarea, 'Hi');
    
    const submitButton = screen.getByText('Save & Continue');
    fireEvent.press(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please write at least 10 characters')).toBeTruthy();
    });
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('calls onSubmit with correct content when valid', async () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const textarea = screen.getByPlaceholderText("What's on your mind today? Write freely about your thoughts, feelings, or experiences...");
    fireEvent.changeText(textarea, 'I am grateful for my family and friends who support me every day.');
    
    const submitButton = screen.getByText('Save & Continue');
    fireEvent.press(submitButton);
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('I am grateful for my family and friends who support me every day.');
    });
  });

  it('shows loading state when isLoading is true', () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
        isLoading={true} 
      />
    );
    
    expect(screen.getByText('Saving...')).toBeTruthy();
  });

  it('disables submit button when loading', () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
        isLoading={true} 
      />
    );
    
    const submitButton = screen.getByText('Saving...');
    expect(submitButton.props.disabled).toBe(true);
  });

  it('disables submit button when content is empty', () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const submitButton = screen.getByText('Save & Continue');
    expect(submitButton.props.disabled).toBe(true);
  });

  it('enables submit button when content is valid', () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const textarea = screen.getByPlaceholderText("What's on your mind today? Write freely about your thoughts, feelings, or experiences...");
    fireEvent.changeText(textarea, 'This is a valid journal entry with enough characters.');
    
    const submitButton = screen.getByText('Save & Continue');
    expect(submitButton.props.disabled).toBe(false);
  });

  it('clears error when user starts typing', async () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    // Trigger error
    const submitButton = screen.getByText('Save & Continue');
    fireEvent.press(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please write something in your journal')).toBeTruthy();
    });
    
    // Start typing to clear error
    const textarea = screen.getByPlaceholderText("What's on your mind today? Write freely about your thoughts, feelings, or experiences...");
    fireEvent.changeText(textarea, 'Hello');
    
    await waitFor(() => {
      expect(screen.queryByText('Please write something in your journal')).toBeFalsy();
    });
  });

    it('applies custom className', () => {
    const { UNSAFE_root } = render(
      <JournalEntryForm
        onSubmit={mockOnSubmit}
        className="custom-class"
      />
    );

    const mainContainer = UNSAFE_root.findByProps({
      className: expect.stringContaining('custom-class')
    });
    expect(mainContainer).toBeTruthy();
  });

  it('trims whitespace from content before submission', async () => {
    render(
      <JournalEntryForm 
        onSubmit={mockOnSubmit} 
      />
    );
    
    const textarea = screen.getByPlaceholderText("What's on your mind today? Write freely about your thoughts, feelings, or experiences...");
    fireEvent.changeText(textarea, '   Valid content with whitespace   ');
    
    const submitButton = screen.getByText('Save & Continue');
    fireEvent.press(submitButton);
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Valid content with whitespace');
    });
  });
}); 