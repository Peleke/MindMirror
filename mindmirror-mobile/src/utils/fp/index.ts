// Option utilities
export {
  fromNullable,
  mapNullable,
  safeProp,
  safeIndex,
} from './option'

export {
  fromPromise as fromPromiseOption,
  fromAsyncStorage as fromAsyncStorageOption,
  toAsyncStorage as toAsyncStorageOption,
  getOrElse as getOrElseOption,
  fold as foldOption,
  getFromStorage as getFromStorageOption,
  setToStorage as setToStorageOption,
} from './option'

// Either utilities
export {
  fromPromise as fromPromiseEither,
  fromApiCall,
  fromAsyncStorage as fromAsyncStorageEither,
  toAsyncStorage as toAsyncStorageEither,
  getOrElse as getOrElseEither,
  fold as foldEither,
  mapError,
  orElse,
  getFromStorage as getFromStorageEither,
  setToStorage as setToStorageEither,
  handleNetworkError,
  handleApiResponse,
} from './either' 