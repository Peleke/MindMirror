import { gql, useLazyQuery } from '@apollo/client'

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