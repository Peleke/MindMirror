import { gql, useLazyQuery, useMutation } from '@apollo/client'

export const QUERY_SEARCH_MOVEMENTS = gql`
  query SearchMovements($searchTerm: String, $bodyRegion: String, $pattern: String, $equipment: String, $limit: Int = 25, $offset: Int = 0) {
    searchMovements(searchTerm: $searchTerm, bodyRegion: $bodyRegion, pattern: $pattern, equipment: $equipment, limit: $limit, offset: $offset) {
      id_
      name
      bodyRegion
      equipment
      difficulty
      shortVideoUrl
      isExternal
      externalId
    }
  }
`

export const useLazySearchMovements = () => useLazyQuery(QUERY_SEARCH_MOVEMENTS, { fetchPolicy: 'cache-and-network' })

export const MUTATION_IMPORT_EXTERNAL_MOVEMENT = gql`
  mutation ImportExternalMovement($externalId: String!) {
    importExternalMovement(externalId: $externalId) { id_ name bodyRegion equipment shortVideoUrl }
  }
`

export const useImportExternalMovement = () => useMutation(MUTATION_IMPORT_EXTERNAL_MOVEMENT)

export const MUTATION_CREATE_MOVEMENT = gql`
  mutation CreateMovement($input: MovementCreateInput!) {
    createMovement(input: $input) { id_ name bodyRegion equipment shortVideoUrl }
  }
`

export const useCreateMovement = () => useMutation(MUTATION_CREATE_MOVEMENT) 