import { gql, useMutation, useQuery } from '@apollo/client'

// Queries
export const QUERY_TODAYS_WORKOUTS = gql`
  query TodaysWorkouts($onDate: Date) {
    todaysWorkouts(onDate: $onDate) {
      id_
      date
      title
      prescriptions { movements { name movement { id_ } sets { reps loadValue loadUnit } } }
    }
  }
`

export const QUERY_WORKOUTS = gql`
  query Workouts($dateFrom: Date, $dateTo: Date, $dates: [Date!], $programId: ID, $status: String) {
    workouts(dateFrom: $dateFrom, dateTo: $dateTo, dates: $dates, programId: $programId, status: $status) {
      id_
      date
      title
      completed_at
      template_id
    }
  }
`

export const QUERY_PROGRAM_TEMPLATES = gql`
  query Programs {
    programs { id_ name description level tags { name } practice_links { sequence_order practice_template { id_ title } } }
  }
`

// Mutations
export const MUTATION_CREATE_ADHOC_WORKOUT = gql`
  mutation CreateAdHocWorkout($input: PracticeInstanceCreateStandaloneInput!) {
    createAdHocWorkout(input: $input) { id_ date title }
  }
`

export const MUTATION_SCHEDULE_WORKOUT = gql`
  mutation ScheduleWorkout($templateId: ID!, $date: Date!) {
    scheduleWorkout(template_id: $templateId, date: $date) { id_ date title }
  }
`

export const MUTATION_ENROLL_IN_PROGRAM = gql`
  mutation EnrollInProgram($programId: ID!) {
    enrollInProgram(program_id: $programId) { id_ program_id user_id status }
  }
`

// Hooks
export const useTodaysWorkouts = (onDate?: string) => useQuery(QUERY_TODAYS_WORKOUTS, { variables: { onDate }, fetchPolicy: 'cache-and-network' })
export const useWorkouts = (vars: { dateFrom?: string, dateTo?: string, dates?: string[], programId?: string, status?: string }) => useQuery(QUERY_WORKOUTS, { variables: vars, fetchPolicy: 'cache-and-network' })
export const usePrograms = () => useQuery(QUERY_PROGRAM_TEMPLATES, { fetchPolicy: 'cache-and-network' })

export const useCreateAdHocWorkout = () => useMutation(MUTATION_CREATE_ADHOC_WORKOUT)
export const useScheduleWorkout = () => useMutation(MUTATION_SCHEDULE_WORKOUT)
export const useEnrollInProgram = () => useMutation(MUTATION_ENROLL_IN_PROGRAM) 