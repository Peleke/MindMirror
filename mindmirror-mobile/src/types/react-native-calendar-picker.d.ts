declare module 'react-native-calendar-picker' {
  import * as React from 'react'
  import { ViewStyle, TextStyle } from 'react-native'

  export interface CalendarPickerProps {
    selectedStartDate?: Date | string
    selectedEndDate?: Date | string
    onDateChange?: (date: Date, type?: 'START_DATE' | 'END_DATE') => void
    startFromMonday?: boolean
    allowRangeSelection?: boolean
    minDate?: Date | string
    maxDate?: Date | string
    todayBackgroundColor?: string
    selectedDayColor?: string
    selectedDayTextColor?: string
    selectedDayStyle?: ViewStyle
    selectedDayTextStyle?: TextStyle
    weekdays?: string[]
    months?: string[]
    previousTitle?: string
    nextTitle?: string
    textStyle?: TextStyle
    // Additional styles supported by the library
    headerWrapperStyle?: ViewStyle
    monthYearHeaderWrapperStyle?: ViewStyle
    dayLabelsWrapper?: ViewStyle
    monthTitleStyle?: TextStyle
    yearTitleStyle?: TextStyle
  }

  export default class CalendarPicker extends React.Component<CalendarPickerProps> {}
} 