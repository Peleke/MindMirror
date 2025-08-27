import { gql, useQuery } from '@apollo/client'

export const QUERY_TODAYS_SCHEDULABLES = gql`
  query TodaysSchedulables($userId: ID!, $date: Date!) {
    schedulablesForUserOnDate(userId: $userId, eventDate: $date) {
      id_
      name
      description
      completed
      date
      service_id
      entity_id
      __typename
    }
  }
`

export const useTodaysSchedulables = (vars: { userId: string; date: string }, skip?: boolean) =>
  useQuery(QUERY_TODAYS_SCHEDULABLES, {
    variables: vars,
    fetchPolicy: 'cache-and-network',
    skip: !!skip,
  }) 