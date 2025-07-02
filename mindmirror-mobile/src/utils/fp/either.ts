import * as E from 'fp-ts/Either'
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'
import AsyncStorage from '@react-native-async-storage/async-storage'

// Either utilities for API calls
export const fromPromise = <A>(promise: Promise<A>): TE.TaskEither<Error, A> =>
  TE.tryCatch(
    () => promise,
    (error) => error instanceof Error ? error : new Error(String(error))
  )

export const fromApiCall = <A>(
  apiCall: () => Promise<A>
): TE.TaskEither<Error, A> =>
  TE.tryCatch(
    apiCall,
    (error) => error instanceof Error ? error : new Error(String(error))
  )

// React Native specific either utilities
export const fromAsyncStorage = (key: string): TE.TaskEither<Error, string | null> =>
  TE.tryCatch(
    () => AsyncStorage.getItem(key),
    (error) => error instanceof Error ? error : new Error(String(error))
  )

export const toAsyncStorage = (key: string) => (value: string): TE.TaskEither<Error, void> =>
  TE.tryCatch(
    () => AsyncStorage.setItem(key, value),
    (error) => error instanceof Error ? error : new Error(String(error))
  )

// Helper functions for common Either operations
export const getOrElse = <E, A>(defaultValue: A) => (fa: E.Either<E, A>): A =>
  pipe(fa, E.getOrElse(() => defaultValue))

export const fold = <E, A, B>(
  onLeft: (e: E) => B,
  onRight: (a: A) => B
) => (fa: E.Either<E, A>): B =>
  pipe(fa, E.fold(onLeft, onRight))

// Error handling helpers
export const mapError = <E, F>(f: (e: E) => F) => <A>(fa: E.Either<E, A>): E.Either<F, A> =>
  pipe(fa, E.mapLeft(f))

export const orElse = <E, A>(f: (e: E) => E.Either<E, A>) => (fa: E.Either<E, A>): E.Either<E, A> =>
  pipe(fa, E.orElse(f))

// AsyncStorage helpers with Either
export const getFromStorage = <T>(key: string, defaultValue: T): TE.TaskEither<Error, T> =>
  pipe(
    fromAsyncStorage(key),
    TE.chain(value => {
      if (value === null) {
        return TE.right(defaultValue)
      }
      try {
        return TE.right(JSON.parse(value) as T)
      } catch (error) {
        return TE.left(new Error(`Failed to parse stored value: ${error}`))
      }
    })
  )

export const setToStorage = <T>(key: string, value: T): TE.TaskEither<Error, void> =>
  pipe(
    TE.tryCatch(
      () => JSON.stringify(value),
      (error) => new Error(`Failed to stringify value: ${error}`)
    ),
    TE.chain(jsonValue => toAsyncStorage(key)(jsonValue))
  )

// Network error handling
export const handleNetworkError = (error: unknown): Error => {
  if (error instanceof Error) {
    return error
  }
  if (typeof error === 'string') {
    return new Error(error)
  }
  return new Error('An unknown error occurred')
}

// API response handling
export const handleApiResponse = <T>(response: Response): TE.TaskEither<Error, T> =>
  pipe(
    TE.tryCatch(
      () => response.json(),
      (error) => new Error(`Failed to parse response: ${error}`)
    ),
    TE.chain(data => {
      if (!response.ok) {
        return TE.left(new Error(`API Error: ${response.status} ${response.statusText}`))
      }
      return TE.right(data as T)
    })
  ) 