import { gql, useMutation, useQuery } from '@apollo/client'

// Queries
export const QUERY_TODAYS_WORKOUTS = gql`
  query TodaysWorkouts($onDate: Date) {
    todaysWorkouts(onDate: $onDate) {
      id_
      date
      title
      description
      prescriptions {
        id_
        name
        block
        movements {
          id_
          name
          restDuration
          movement { id_ }
          sets { id_ reps loadValue loadUnit restDuration complete movementInstanceId }
        }
      }
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

export const MUTATION_DELETE_PRACTICE_INSTANCE = gql`
  mutation DeletePracticeInstance($id: ID!) {
    deletePracticeInstance(id: $id)
  }
`

export const MUTATION_COMPLETE_WORKOUT = gql`
  mutation CompleteWorkout($id: ID!) {
    completeWorkout(id: $id) { id_ completedAt }
  }
`

export const MUTATION_UPDATE_SET_INSTANCE = gql`
  mutation UpdateSetInstance($id: ID!, $input: SetInstanceUpdateInput!) {
    updateSetInstance(id: $id, input: $input) { id_ reps loadValue duration complete }
  }
`

export const MUTATION_COMPLETE_SET_INSTANCE = gql`
  mutation CompleteSetInstance($id: ID!) {
    completeSetInstance(id: $id) { id_ complete completedAt }
  }
`

export const MUTATION_CREATE_SET_INSTANCE = gql`
  mutation CreateSetInstance($input: SetInstanceCreateInput!) {
    createSetInstance(input: $input) { id_ reps loadValue restDuration loadUnit complete movementInstanceId }
  }
`

// Hooks
export const useTodaysWorkouts = (onDate?: string) => useQuery(QUERY_TODAYS_WORKOUTS, { variables: { onDate }, fetchPolicy: 'cache-and-network' })
export const useWorkouts = (vars: { dateFrom?: string, dateTo?: string, dates?: string[], programId?: string, status?: string }) => useQuery(QUERY_WORKOUTS, { variables: vars, fetchPolicy: 'cache-and-network' })
export const usePrograms = () => useQuery(QUERY_PROGRAM_TEMPLATES, { fetchPolicy: 'cache-and-network' })

export const useCreateAdHocWorkout = () => useMutation(MUTATION_CREATE_ADHOC_WORKOUT)
export const useScheduleWorkout = () => useMutation(MUTATION_SCHEDULE_WORKOUT)
export const useEnrollInProgram = () => useMutation(MUTATION_ENROLL_IN_PROGRAM)
export const useDeletePracticeInstance = () => useMutation(MUTATION_DELETE_PRACTICE_INSTANCE)
export const useCompleteWorkout = () => useMutation(MUTATION_COMPLETE_WORKOUT)
export const useUpdateSetInstance = () => useMutation(MUTATION_UPDATE_SET_INSTANCE)
export const useCompleteSetInstance = () => useMutation(MUTATION_COMPLETE_SET_INSTANCE)
export const useCreateSetInstance = () => useMutation(MUTATION_CREATE_SET_INSTANCE) 