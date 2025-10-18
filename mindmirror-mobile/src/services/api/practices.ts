import { gql, useMutation, useQuery } from '@apollo/client'

// Queries
export const QUERY_TODAYS_WORKOUTS = gql`
  query TodaysWorkouts($onDate: Date) {
    todaysWorkouts(onDate: $onDate) {
      id_
      date
      title
      description
      completedAt
      prescriptions {
        id_
        name
        block
        position
        movements {
          id_
          name
          description
          restDuration
          videoUrl
          position
          movement {
            id_
            name
            description
            description
            shortVideoUrl
            longVideoUrl
            difficulty
            bodyRegion
            archetype
            equipment
            primaryMuscles
            secondaryMuscles
            movementPatterns
            planesOfMotion
            tags
          }
          sets { id_ position reps loadValue loadUnit restDuration complete movementInstanceId }
        }
      }
    }
  }
`

export const QUERY_SEARCH_MOVEMENTS = gql`
  query SearchMovements($term: String!, $limit: Int) {
    searchMovements(searchTerm: $term, limit: $limit) {
      id_
      name
      difficulty
      bodyRegion
      equipment
      shortVideoUrl
      description
    }
  }
`

export const QUERY_WORKOUTS = gql`
  query Workouts($dateFrom: Date, $dateTo: Date, $dates: [Date!], $programId: ID, $status: String) {
    workouts(dateFrom: $dateFrom, dateTo: $dateTo, dates: $dates, programId: $programId, status: $status) {
      id_
      date
      title
      completedAt
      templateId
    }
  }
`

export const QUERY_PROGRAM_TEMPLATES = gql`
  query Programs {
    programs { id_ name description level tags { name } practiceLinks { sequenceOrder intervalDaysAfter practiceTemplate { id_ title } } }
  }
`

export const QUERY_PRACTICE_TEMPLATES = gql`
  query PracticeTemplates {
    practiceTemplates { id_ title description }
  }
`

export const QUERY_SEARCH_PRACTICE_TEMPLATES = gql`
  query SearchPracticeTemplates($term: String!, $limit: Int) {
    searchPracticeTemplates(searchTerm: $term, limit: $limit) { id_ title description }
  }
`

export const QUERY_PRACTICE_TEMPLATE = gql`
  query PracticeTemplate($id: ID!) {
    practiceTemplate(id: $id) {
      id_
      title
      description
      prescriptions {
        id_
        name
        block
        position
        movements {
          id_
          name
          description
          metric_unit: metricUnit
          metric_value: metricValue
          movement_class: movementClass
          prescribed_sets: prescribedSets
          rest_duration: restDuration
          video_url: videoUrl
          exercise_id: exerciseId
          movement_id: movementId
          movement {
            id_
            name
            description
            shortVideoUrl
            longVideoUrl
            difficulty
            bodyRegion
            archetype
            equipment
            primaryMuscles
            secondaryMuscles
            movementPatterns
            planesOfMotion
            tags
          }
          sets {
            id_
            position
            reps
            duration
            rest_duration: restDuration
            load_value: loadValue
            load_unit: loadUnit
            movement_template_id: movementTemplateId
          }
        }
      }
    }
  }
`

export const QUERY_MOVEMENT_TEMPLATE = gql`
  query MovementTemplate($id: ID!) {
    movementTemplate(id: $id) {
      id_
      name
      description
      metric_unit: metricUnit
      metric_value: metricValue
      movement_class: movementClass
      prescribed_sets: prescribedSets
      rest_duration: restDuration
      video_url: videoUrl
      exercise_id: exerciseId
      movement_id: movementId
      movement {
        id_
        name
        shortVideoUrl
        longVideoUrl
        difficulty
        bodyRegion
        archetype
        equipment
        primaryMuscles
        secondaryMuscles
        movementPatterns
        planesOfMotion
        tags
      }
      sets { id_ position reps duration rest_duration: restDuration load_value: loadValue load_unit: LoadUnit movement_template_id: movementTemplateId }
    }
  }
`

export const QUERY_PRACTICE_INSTANCE = gql`
  query PracticeInstance($id: ID!) {
    practiceInstance: practice_instance(id: $id) {
      id_
      date
      title
      description
      completedAt
      prescriptions {
        id_
        name
        block
        position
        movements {
          id_
          name
          description
          restDuration
          videoUrl
          position
          movement { id_ name description shortVideoUrl }
          sets { id_ position reps loadValue loadUnit restDuration complete movementInstanceId }
        }
      }
    }
  }
`

export const QUERY_PROGRAM = gql`
  query Program($id: ID!) {
    program(id: $id) {
      id_
      name
      description
      level
      habitsProgramTemplateId
      tags { name }
      practiceLinks { sequenceOrder intervalDaysAfter practiceTemplate { id_ title } }
    }
  }
`

export const QUERY_MY_UPCOMING_PRACTICES = gql`
  query MyUpcomingPractices {
    my_upcoming_practices: myUpcomingPractices { 
      id_ 
      enrollment_id: enrollmentId 
      practice_id: practiceId 
      practice_instance_id: practiceInstanceId
      scheduled_date: scheduledDate 
    }
  }
`

export const QUERY_MY_UPCOMING_PRACTICES_IN_PROGRAM = gql`
  query MyUpcomingPracticesInProgram($programId: ID!) {
    my_upcoming_practices_in_program: myUpcomingPracticesInProgram(programId: $programId) { id_ enrollment_id: enrollmentId practice_id: practiceId scheduled_date: scheduledDate }
  }
`

export const QUERY_MY_ENROLLMENTS = gql`
  query Enrollments($userId: ID!) {
    enrollments(userId: $userId) {
      id_
      program_id: programId
      status
    }
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
    scheduleWorkout(templateId: $templateId, date: $date) { id_ date title }
  }
`

export const MUTATION_ENROLL_IN_PROGRAM = gql`
  mutation EnrollInProgram($input: EnrollInProgramInput!) {
    enrollInProgram(input: $input) { id_ programId userId status }
  }
`

export const MUTATION_ENROLL_USER_IN_PROGRAM = gql`
  mutation EnrollUserInProgram($input: EnrollUserInProgramInput!) {
    enrollUserInProgram(input: $input) { id_ programId userId status }
  }
`

export const MUTATION_ATTACH_LESSONS_TO_PROGRAM_ENROLLMENT = gql`
  mutation AttachLessonsToProgramEnrollment($input: AttachLessonsToProgramEnrollmentInput!) {
    attachLessonsToProgramEnrollment(input: $input)
  }
`

export const QUERY_LESSON_TEMPLATES = gql`
  query LessonTemplates {
    lessonTemplates {
      id
      slug
      title
      summary
      segments {
        id
        label
        selector
      }
      defaultSegment
    }
  }
`

export const QUERY_LESSON_TEMPLATE_BY_SLUG = gql`
  query LessonTemplateBySlug($slug: String!) {
    lessonTemplateBySlug(slug: $slug) {
      id
      slug
      title
      summary
      segments {
        id
        label
        selector
      }
      defaultSegment
    }
  }
`

export const MUTATION_UPDATE_ENROLLMENT_STATUS = gql`
  mutation UpdateEnrollmentStatus($enrollmentId: ID!, $status: EnrollmentStatusGQL!) {
    updateEnrollmentStatus(enrollmentId: $enrollmentId, status: $status) {
      id_
      status
    }
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

export const MUTATION_CREATE_PRACTICE_TEMPLATE = gql`
  mutation CreatePracticeTemplate($input: PracticeTemplateCreateInput!) {
    createPracticeTemplate(input: $input) { id_ title description }
  }
`

export const MUTATION_CREATE_PROGRAM = gql`
  mutation CreateProgram($input: ProgramCreateInput!) {
    createProgram(input: $input) {
      id_
      name
      description
      level
      habitsProgramTemplateId
      tags { name }
      practiceLinks { sequenceOrder intervalDaysAfter practiceTemplate { id_ title } }
    }
  }
`

export const MUTATION_DELETE_PROGRAM = gql`
  mutation DeleteProgram($id: ID!) {
    deleteProgram(id: $id)
  }
`

export const MUTATION_ASSIGN_PROGRAM_TO_CLIENT = gql`
  mutation AssignProgramToClient($programId: ID!, $clientId: ID!, $campaign: String) {
    assignProgramToClient(programId: $programId, clientId: $clientId, campaign: $campaign)
  }
`

export const QUERY_WORKOUTS_FOR_USER = gql`
  query WorkoutsForUser($userId: ID!, $dateFrom: String, $dateTo: String, $status: String) {
    workoutsForUser(userId: $userId, dateFrom: $dateFrom, dateTo: $dateTo, status: $status) {
      id_
      date
      title
      description
      completedAt
      templateId
    }
  }
`

// TypeScript interfaces for the new GraphQL types
export interface EnrollInProgramInput {
  programId: string
  repeatCount?: number
  lessons?: AttachLessonsToProgramEnrollmentInput[]
}

export interface EnrollUserInProgramInput {
  programId: string
  userId: string
  repeatCount?: number
  lessons?: AttachLessonsToProgramEnrollmentInput[]
}

export interface AttachLessonsToProgramEnrollmentInput {
  enrollmentId: string
  lessonTemplateSlug: string
  dayOffset: number
  onWorkoutDay?: boolean
  segmentIds?: string[]
}

export interface LessonTemplate {
  id: string
  slug: string
  title: string
  summary?: string
  segments?: LessonSegment[]
  defaultSegment?: string
}

export interface LessonSegment {
  id: string
  label: string
  selector: string
}

export const MUTATION_DEFER_PRACTICE = gql`
  mutation DeferPractice($enrollmentId: ID!, $mode: String!) {
    deferPractice(enrollmentId: $enrollmentId, mode: $mode)
  }
`

// Hooks
export const useTodaysWorkouts = (onDate?: string) => useQuery(QUERY_TODAYS_WORKOUTS, { variables: { onDate }, fetchPolicy: 'cache-and-network' })
export const useSearchMovements = (term: string, limit = 1) => useQuery(QUERY_SEARCH_MOVEMENTS, { variables: { term, limit }, skip: !term, fetchPolicy: 'cache-and-network' })
export const useWorkouts = (vars: { dateFrom?: string, dateTo?: string, dates?: string[], programId?: string, status?: string }) => useQuery(QUERY_WORKOUTS, { variables: vars, fetchPolicy: 'cache-and-network' })
export const usePrograms = () => useQuery(QUERY_PROGRAM_TEMPLATES, { fetchPolicy: 'cache-and-network' })
export const usePracticeTemplates = () => useQuery(QUERY_PRACTICE_TEMPLATES, { fetchPolicy: 'cache-and-network' })
// Proper lazy query hook for practice template search
import { useLazyQuery } from '@apollo/client'
export const useLazySearchPracticeTemplates = () => useLazyQuery(QUERY_SEARCH_PRACTICE_TEMPLATES, { fetchPolicy: 'cache-and-network' })
export const useProgram = (id: string) => useQuery(QUERY_PROGRAM, { variables: { id }, fetchPolicy: 'cache-and-network', skip: !id })
export const usePracticeTemplate = (id: string) => useQuery(QUERY_PRACTICE_TEMPLATE, { variables: { id }, fetchPolicy: 'cache-and-network', skip: !id })
export const useMovementTemplate = (id: string) => useQuery(QUERY_MOVEMENT_TEMPLATE, { variables: { id }, fetchPolicy: 'cache-and-network', skip: !id })
export const usePracticeInstance = (id: string) => useQuery(QUERY_PRACTICE_INSTANCE, { variables: { id }, fetchPolicy: 'cache-and-network', skip: !id })
export const useMyUpcomingPractices = () => useQuery(QUERY_MY_UPCOMING_PRACTICES, { fetchPolicy: 'cache-and-network' })
export const useMyUpcomingPracticesInProgram = (programId: string) => useQuery(QUERY_MY_UPCOMING_PRACTICES_IN_PROGRAM, { variables: { programId }, skip: !programId, fetchPolicy: 'cache-and-network' })
export const useMyEnrollments = (userId?: string) => useQuery(QUERY_MY_ENROLLMENTS, { variables: { userId }, skip: !userId, fetchPolicy: 'cache-and-network' })

export const useCreateAdHocWorkout = () => useMutation(MUTATION_CREATE_ADHOC_WORKOUT)
export const useScheduleWorkout = () => useMutation(MUTATION_SCHEDULE_WORKOUT)
export const useEnrollInProgram = () => useMutation(MUTATION_ENROLL_IN_PROGRAM)
export const useEnrollUserInProgram = () => useMutation(MUTATION_ENROLL_USER_IN_PROGRAM)
export const useUpdateEnrollmentStatus = () => useMutation(MUTATION_UPDATE_ENROLLMENT_STATUS)
export const useDeletePracticeInstance = () => useMutation(MUTATION_DELETE_PRACTICE_INSTANCE)
export const useCompleteWorkout = () => useMutation(MUTATION_COMPLETE_WORKOUT)
export const useUpdateSetInstance = () => useMutation(MUTATION_UPDATE_SET_INSTANCE)
export const useCompleteSetInstance = () => useMutation(MUTATION_COMPLETE_SET_INSTANCE)
export const useCreateSetInstance = () => useMutation(MUTATION_CREATE_SET_INSTANCE)
export const useCreateProgram = () => useMutation(MUTATION_CREATE_PROGRAM)
export const useCreatePracticeTemplate = () => useMutation(MUTATION_CREATE_PRACTICE_TEMPLATE)
export const useDeleteProgram = () => useMutation(MUTATION_DELETE_PROGRAM)
export const useDeferPractice = () => useMutation(MUTATION_DEFER_PRACTICE)
export const useAssignProgramToClient = () => useMutation(MUTATION_ASSIGN_PROGRAM_TO_CLIENT)
export const useWorkoutsForUser = (userId: string, dateFrom?: string, dateTo?: string, status?: string) => {
  return useQuery(QUERY_WORKOUTS_FOR_USER, {
    variables: { userId, dateFrom, dateTo, status },
    skip: !userId,
    fetchPolicy: 'cache-and-network',
  })
}

export const QUERY_HABITS_PROGRAM_TEMPLATES = gql`
  query ListProgramTemplates {
    programTemplates {
      id
      slug
      title
      description
      subtitle
    }
  }
`;

export const useHabitsProgramTemplates = () => {
  return useQuery(QUERY_HABITS_PROGRAM_TEMPLATES);
}; 