import * as O from 'fp-ts/Option'
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'
import AsyncStorage from '@react-native-async-storage/async-storage'

// Option utilities for React Native
export const fromNullable = <A>(value: A | null | undefined): O.Option<A> =>
  value === null || value === undefined ? O.none : O.some(value)

export const fromPromise = <A>(promise: Promise<A>): Promise<O.Option<A>> =>
  promise
    .then(O.some)
    .catch(() => O.none)

export const mapNullable = <A, B>(
  f: (a: A) => B | null | undefined
) => (fa: O.Option<A>): O.Option<B> =>
  pipe(fa, O.map(f), O.chain(fromNullable))

// React Native specific option utilities
export const fromAsyncStorage = (key: string): Promise<O.Option<string>> =>
  fromPromise(AsyncStorage.getItem(key))

export const toAsyncStorage = (key: string) => (value: string): Promise<O.Option<void>> =>
  fromPromise(AsyncStorage.setItem(key, value))

// Helper functions for common Option operations
export const getOrElse = <A>(defaultValue: A) => (fa: O.Option<A>): A =>
  pipe(fa, O.getOrElse(() => defaultValue))

export const fold = <A, B>(
  onNone: () => B,
  onSome: (a: A) => B
) => (fa: O.Option<A>): B =>
  pipe(fa, O.fold(onNone, onSome))

// Safe navigation helpers
export const safeProp = <K extends keyof any, A>(key: K) => (obj: A): O.Option<A[K]> =>
  pipe(
    fromNullable(obj),
    O.chain(obj => fromNullable((obj as any)[key]))
  )

export const safeIndex = <A>(index: number) => (arr: A[]): O.Option<A> =>
  pipe(
    fromNullable(arr),
    O.chain(arr => fromNullable(arr[index]))
  )

// AsyncStorage helpers with Option
export const getFromStorage = async <T>(key: string, defaultValue: T): Promise<T> => {
  const result = await fromAsyncStorage(key)
  return pipe(
    result,
    O.chain(value => {
      try {
        return O.some(JSON.parse(value) as T)
      } catch {
        return O.none
      }
    }),
    getOrElse(defaultValue)
  )
}

export const setToStorage = async <T>(key: string, value: T): Promise<void> => {
  const jsonValue = JSON.stringify(value)
  await pipe(
    toAsyncStorage(key)(jsonValue),
    O.getOrElse(() => Promise.resolve())
  )
} 