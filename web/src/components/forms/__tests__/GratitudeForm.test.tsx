import { render, screen, waitFor } from '@testing-library/react'
import { MockedProvider } from '@apollo/client/testing'
import { GratitudeForm } from '../GratitudeForm'
import { JOURNAL_ENTRY_EXISTS_TODAY } from '../../../../lib/graphql/queries'

// Mock the tradition context
jest.mock('../../../../lib/tradition-context', () => ({
  useTradition: () => ({
    selectedTradition: 'canon-default'
  })
}))

const mocks = [
  {
    request: {
      query: JOURNAL_ENTRY_EXISTS_TODAY,
      variables: { entryType: 'gratitude' }
    },
    result: {
      data: { journalEntryExistsToday: false }
    }
  }
]

describe('GratitudeForm', () => {
  it('renders the form title and description', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GratitudeForm />
      </MockedProvider>
    )

    // Wait for the form to load (after Apollo query completes)
    await waitFor(() => {
      expect(screen.getByText('Morning Gratitude')).toBeInTheDocument()
    })
    
    expect(screen.getByText(/Start your day by reflecting/)).toBeInTheDocument()
  })

  it('renders all form sections', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GratitudeForm />
      </MockedProvider>
    )

    // Wait for loading to finish and form to appear
    await waitFor(() => {
      expect(screen.getByText('What are you grateful for today?')).toBeInTheDocument()
    })
    
    expect(screen.getByText('What are you excited about?')).toBeInTheDocument()
    expect(screen.getByText('Focus Areas')).toBeInTheDocument()
    expect(screen.getByText('How are you feeling?')).toBeInTheDocument()
  })

  it('renders the submit button', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <GratitudeForm />
      </MockedProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Save Gratitude Entry')).toBeInTheDocument()
    })
  })
}) 