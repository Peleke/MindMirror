'use client';
import { vars } from 'nativewind';

export const config = {
  light: vars({
    '--color-primary-0': '179 179 179',
    '--color-primary-50': '153 153 153',
    '--color-primary-100': '128 128 128',
    '--color-primary-200': '115 115 115',
    '--color-primary-300': '102 102 102',
    '--color-primary-400': '82 82 82',
    '--color-primary-500': '51 51 51',
    '--color-primary-600': '41 41 41',
    '--color-primary-700': '31 31 31',
    '--color-primary-800': '13 13 13',
    '--color-primary-900': '10 10 10',
    '--color-primary-950': '8 8 8',

    /* Secondary  */
    '--color-secondary-0': '253 253 253',
    '--color-secondary-50': '251 251 251',
    '--color-secondary-100': '246 246 246',
    '--color-secondary-200': '242 242 242',
    '--color-secondary-300': '237 237 237',
    '--color-secondary-400': '230 230 231',
    '--color-secondary-500': '217 217 219',
    '--color-secondary-600': '198 199 199',
    '--color-secondary-700': '189 189 189',
    '--color-secondary-800': '177 177 177',
    '--color-secondary-900': '165 164 164',
    '--color-secondary-950': '157 157 157',

    /* Tertiary */
    '--color-tertiary-0': '255 250 245',
    '--color-tertiary-50': '255 242 229',
    '--color-tertiary-100': '255 233 213',
    '--color-tertiary-200': '254 209 170',
    '--color-tertiary-300': '253 180 116',
    '--color-tertiary-400': '251 157 75',
    '--color-tertiary-500': '231 129 40',
    '--color-tertiary-600': '215 117 31',
    '--color-tertiary-700': '180 98 26',
    '--color-tertiary-800': '130 73 23',
    '--color-tertiary-900': '108 61 19',
    '--color-tertiary-950': '84 49 18',

    /* Error */
    '--color-error-0': '254 233 233',
    '--color-error-50': '254 226 226',
    '--color-error-100': '254 202 202',
    '--color-error-200': '252 165 165',
    '--color-error-300': '248 113 113',
    '--color-error-400': '239 68 68',
    '--color-error-500': '230 53 53',
    '--color-error-600': '220 38 38',
    '--color-error-700': '185 28 28',
    '--color-error-800': '153 27 27',
    '--color-error-900': '127 29 29',
    '--color-error-950': '83 19 19',

    /* Success */
    '--color-success-0': '228 255 244',
    '--color-success-50': '202 255 232',
    '--color-success-100': '162 241 192',
    '--color-success-200': '132 211 162',
    '--color-success-300': '102 181 132',
    '--color-success-400': '72 151 102',
    '--color-success-500': '52 131 82',
    '--color-success-600': '42 121 72',
    '--color-success-700': '32 111 62',
    '--color-success-800': '22 101 52',
    '--color-success-900': '20 83 45',
    '--color-success-950': '27 50 36',

    /* Warning */
    '--color-warning-0': '255 249 245',
    '--color-warning-50': '255 244 236',
    '--color-warning-100': '255 231 213',
    '--color-warning-200': '254 205 170',
    '--color-warning-300': '253 173 116',
    '--color-warning-400': '251 149 75',
    '--color-warning-500': '231 120 40',
    '--color-warning-600': '215 108 31',
    '--color-warning-700': '180 90 26',
    '--color-warning-800': '130 68 23',
    '--color-warning-900': '108 56 19',
    '--color-warning-950': '84 45 18',

    /* Info */
    '--color-info-0': '236 248 254',
    '--color-info-50': '199 235 252',
    '--color-info-100': '162 221 250',
    '--color-info-200': '124 207 248',
    '--color-info-300': '87 194 246',
    '--color-info-400': '50 180 244',
    '--color-info-500': '13 166 242',
    '--color-info-600': '11 141 205',
    '--color-info-700': '9 115 168',
    '--color-info-800': '7 90 131',
    '--color-info-900': '5 64 93',
    '--color-info-950': '3 38 56',

    /* Typography */
    '--color-typography-0': '254 254 255',
    '--color-typography-50': '245 245 245',
    '--color-typography-100': '229 229 229',
    '--color-typography-200': '219 219 220',
    '--color-typography-300': '212 212 212',
    '--color-typography-400': '163 163 163',
    '--color-typography-500': '140 140 140',
    '--color-typography-600': '115 115 115',
    '--color-typography-700': '82 82 82',
    '--color-typography-800': '64 64 64',
    '--color-typography-900': '38 38 39',
    '--color-typography-950': '23 23 23',

    /* Outline */
    '--color-outline-0': '253 254 254',
    '--color-outline-50': '243 243 243',
    '--color-outline-100': '230 230 230',
    '--color-outline-200': '221 220 219',
    '--color-outline-300': '211 211 211',
    '--color-outline-400': '165 163 163',
    '--color-outline-500': '140 141 141',
    '--color-outline-600': '115 116 116',
    '--color-outline-700': '83 82 82',
    '--color-outline-800': '65 65 65',
    '--color-outline-900': '39 38 36',
    '--color-outline-950': '26 23 23',

    /* Background */
    '--color-background-0': '255 255 255',
    '--color-background-50': '246 246 246',
    '--color-background-100': '242 241 241',
    '--color-background-200': '220 219 219',
    '--color-background-300': '213 212 212',
    '--color-background-400': '162 163 163',
    '--color-background-500': '142 142 142',
    '--color-background-600': '116 116 116',
    '--color-background-700': '83 82 82',
    '--color-background-800': '65 64 64',
    '--color-background-900': '39 38 37',
    '--color-background-950': '18 18 18',

    /* Background Special */
    '--color-background-error': '254 241 241',
    '--color-background-warning': '255 243 234',
    '--color-background-success': '237 252 242',
    '--color-background-muted': '247 248 247',
    '--color-background-info': '235 248 254',

    /* Focus Ring Indicator  */
    '--color-indicator-primary': '55 55 55',
    '--color-indicator-info': '83 153 236',
    '--color-indicator-error': '185 28 28',

    /* Border (alias of outline for default light) */
    '--color-border-0': '253 254 254',
    '--color-border-50': '243 243 243',
    '--color-border-100': '230 230 230',
    '--color-border-200': '221 220 219',
    '--color-border-300': '211 211 211',
    '--color-border-400': '165 163 163',
    '--color-border-500': '140 141 141',
    '--color-border-600': '115 116 116',
    '--color-border-700': '83 82 82',
    '--color-border-800': '65 65 65',
    '--color-border-900': '39 38 36',
    '--color-border-950': '26 23 23',
  }),
  dark: vars({
    '--color-primary-0': '166 166 166',
    '--color-primary-50': '175 175 175',
    '--color-primary-100': '186 186 186',
    '--color-primary-200': '197 197 197',
    '--color-primary-300': '212 212 212',
    '--color-primary-400': '221 221 221',
    '--color-primary-500': '230 230 230',
    '--color-primary-600': '240 240 240',
    '--color-primary-700': '250 250 250',
    '--color-primary-800': '253 253 253',
    '--color-primary-900': '254 249 249',
    '--color-primary-950': '253 252 252',

    /* Secondary  */
    '--color-secondary-0': '20 20 20',
    '--color-secondary-50': '23 23 23',
    '--color-secondary-100': '31 31 31',
    '--color-secondary-200': '39 39 39',
    '--color-secondary-300': '44 44 44',
    '--color-secondary-400': '56 57 57',
    '--color-secondary-500': '63 64 64',
    '--color-secondary-600': '86 86 86',
    '--color-secondary-700': '110 110 110',
    '--color-secondary-800': '135 135 135',
    '--color-secondary-900': '150 150 150',
    '--color-secondary-950': '164 164 164',

    /* Tertiary */
    '--color-tertiary-0': '84 49 18',
    '--color-tertiary-50': '108 61 19',
    '--color-tertiary-100': '130 73 23',
    '--color-tertiary-200': '180 98 26',
    '--color-tertiary-300': '215 117 31',
    '--color-tertiary-400': '231 129 40',
    '--color-tertiary-500': '251 157 75',
    '--color-tertiary-600': '253 180 116',
    '--color-tertiary-700': '254 209 170',
    '--color-tertiary-800': '255 233 213',
    '--color-tertiary-900': '255 242 229',
    '--color-tertiary-950': '255 250 245',

    /* Error */
    '--color-error-0': '83 19 19',
    '--color-error-50': '127 29 29',
    '--color-error-100': '153 27 27',
    '--color-error-200': '185 28 28',
    '--color-error-300': '220 38 38',
    '--color-error-400': '230 53 53',
    '--color-error-500': '239 68 68',
    '--color-error-600': '249 97 96',
    '--color-error-700': '229 91 90',
    '--color-error-800': '254 202 202',
    '--color-error-900': '254 226 226',
    '--color-error-950': '254 233 233',

    /* Success */
    '--color-success-0': '27 50 36',
    '--color-success-50': '20 83 45',
    '--color-success-100': '22 101 52',
    '--color-success-200': '32 111 62',
    '--color-success-300': '42 121 72',
    '--color-success-400': '52 131 82',
    '--color-success-500': '72 151 102',
    '--color-success-600': '102 181 132',
    '--color-success-700': '132 211 162',
    '--color-success-800': '162 241 192',
    '--color-success-900': '202 255 232',
    '--color-success-950': '228 255 244',

    /* Warning */
    '--color-warning-0': '84 45 18',
    '--color-warning-50': '108 56 19',
    '--color-warning-100': '130 68 23',
    '--color-warning-200': '180 90 26',
    '--color-warning-300': '215 108 31',
    '--color-warning-400': '231 120 40',
    '--color-warning-500': '251 149 75',
    '--color-warning-600': '253 173 116',
    '--color-warning-700': '254 205 170',
    '--color-warning-800': '255 231 213',
    '--color-warning-900': '255 244 237',
    '--color-warning-950': '255 249 245',

    /* Info */
    '--color-info-0': '3 38 56',
    '--color-info-50': '5 64 93',
    '--color-info-100': '7 90 131',
    '--color-info-200': '9 115 168',
    '--color-info-300': '11 141 205',
    '--color-info-400': '13 166 242',
    '--color-info-500': '50 180 244',
    '--color-info-600': '87 194 246',
    '--color-info-700': '124 207 248',
    '--color-info-800': '162 221 250',
    '--color-info-900': '199 235 252',
    '--color-info-950': '236 248 254',

    /* Typography */
    '--color-typography-0': '23 23 23',
    '--color-typography-50': '38 38 39',
    '--color-typography-100': '64 64 64',
    '--color-typography-200': '82 82 82',
    '--color-typography-300': '115 115 115',
    '--color-typography-400': '140 140 140',
    '--color-typography-500': '163 163 163',
    '--color-typography-600': '212 212 212',
    '--color-typography-700': '219 219 220',
    '--color-typography-800': '229 229 229',
    '--color-typography-900': '245 245 245',
    '--color-typography-950': '254 254 255',

    /* Outline */
    '--color-outline-0': '26 23 23',
    '--color-outline-50': '39 38 36',
    '--color-outline-100': '65 65 65',
    '--color-outline-200': '83 82 82',
    '--color-outline-300': '115 116 116',
    '--color-outline-400': '140 141 141',
    '--color-outline-500': '165 163 163',
    '--color-outline-600': '211 211 211',
    '--color-outline-700': '221 220 219',
    '--color-outline-800': '230 230 230',
    '--color-outline-900': '243 243 243',
    '--color-outline-950': '253 254 254',

    /* Background */
    '--color-background-0': '18 18 18',
    '--color-background-50': '39 38 37',
    '--color-background-100': '65 64 64',
    '--color-background-200': '83 82 82',
    '--color-background-300': '116 116 116',
    '--color-background-400': '142 142 142',
    '--color-background-500': '162 163 163',
    '--color-background-600': '213 212 212',
    '--color-background-700': '229 228 228',
    '--color-background-800': '242 241 241',
    '--color-background-900': '246 246 246',
    '--color-background-950': '255 255 255',

    /* Background Special */
    '--color-background-error': '66 43 43',
    '--color-background-warning': '65 47 35',
    '--color-background-success': '28 43 33',
    '--color-background-muted': '51 51 51',
    '--color-background-info': '26 40 46',

    /* Focus Ring Indicator  */
    '--color-indicator-primary': '247 247 247',
    '--color-indicator-info': '161 199 245',
    '--color-indicator-error': '232 70 69',

    /* Border (alias of outline for default dark) */
    '--color-border-0': '26 23 23',
    '--color-border-50': '39 38 36',
    '--color-border-100': '65 65 65',
    '--color-border-200': '83 82 82',
    '--color-border-300': '115 116 116',
    '--color-border-400': '140 141 141',
    '--color-border-500': '165 163 163',
    '--color-border-600': '211 211 211',
    '--color-border-700': '221 220 219',
    '--color-border-800': '230 230 230',
    '--color-border-900': '243 243 243',
    '--color-border-950': '253 254 254',
  }),
  variants: {
    classic: vars({
      /* Primary remapped to Tailwind Indigo for pre-polish look */
      '--color-primary-50': '238 242 255',
      '--color-primary-100': '224 231 255',
      '--color-primary-200': '199 210 254',
      '--color-primary-300': '165 180 252',
      '--color-primary-400': '129 140 248',
      '--color-primary-500': '99 102 241',
      '--color-primary-600': '79 70 229',
      '--color-primary-700': '67 56 202',
      '--color-primary-800': '55 48 163',
      '--color-primary-900': '49 46 129',
      '--color-primary-950': '30 27 75',
    }),
    autumnHarvest: vars({
      /* Background */
      '--color-background-0': '237 224 212', /* #ede0d4 */
      '--color-background-50': '230 204 178', /* #e6ccb2 */
      '--color-background-100': '240 221 197',
      '--color-background-200': '246 230 207',

      /* Typography */
      '--color-typography-900': '127 85 57',   /* #7f5539 */
      '--color-typography-800': '140 94 62',
      '--color-typography-700': '156 102 68',  /* #9c6644 */

      /* Primary (brand accent) around #b08968 */
      '--color-primary-50': '253 246 240',
      '--color-primary-100': '249 238 230',
      '--color-primary-200': '242 225 213',
      '--color-primary-300': '233 210 192',
      '--color-primary-400': '214 182 157',
      '--color-primary-500': '176 137 104', /* #b08968 */
      '--color-primary-600': '153 117 89',
      '--color-primary-700': '127 94 70',
      '--color-primary-800': '101 75 56',
      '--color-primary-900': '79 57 40',
      '--color-primary-950': '52 37 26',

      /* Border tuned to brand neutrals */
      '--color-border-200': '214 182 157',
      '--color-border-300': '200 166 142',
      '--color-border-700': '127 94 70',
    }),
    brightGreens: vars({
      /* Bright Greens palette: [#132a13,#31572c,#4f772d,#90a955,#ecf39e] */
      /* Background (lightest) */
      '--color-background-0': '236 243 158', /* #ecf39e */
      '--color-background-50': '223 236 138',
      '--color-background-100': '209 229 123',
      '--color-background-200': '190 217 110',
      '--color-background-300': '169 204 95',
      '--color-background-700': '121 163 66',

      /* Typography (very dark green) */
      '--color-typography-900': '19 42 19',   /* #132a13 */
      '--color-typography-800': '30 64 30',
      '--color-typography-700': '49 87 44',   /* #31572c */
      '--color-typography-600': '79 119 45',  /* #4f772d */

      /* Primary (leafy accents) spanning #4f772d and #90a955 */
      '--color-primary-50': '232 245 193',
      '--color-primary-100': '221 240 173',
      '--color-primary-200': '198 229 140',
      '--color-primary-300': '165 209 109',
      '--color-primary-400': '144 169 85',   /* #90a955 slightly darkened for contrast */
      '--color-primary-500': '79 119 45',    /* #4f772d */
      '--color-primary-600': '60 96 36',
      '--color-primary-700': '49 87 44',     /* #31572c */
      '--color-primary-800': '30 64 30',
      '--color-primary-900': '19 42 19',     /* #132a13 */
      '--color-primary-950': '12 28 12',

      /* Border tuned to greens */
      '--color-border-200': '198 229 140',
      '--color-border-300': '165 209 109',
      '--color-border-700': '49 87 44',
    }),
    freshGreens: vars({
      /* Fresh Greens palette: [#d8f3dc,#b7e4c7,#95d5b2,#74c69d,#52b788,#40916c,#2d6a4f,#1b4332,#081c15] */
      /* Background */
      '--color-background-0': '216 243 220', /* #d8f3dc */
      '--color-background-50': '183 228 199', /* #b7e4c7 */
      '--color-background-100': '149 213 178', /* #95d5b2 */
      '--color-background-200': '116 198 157', /* #74c69d */
      '--color-background-300': '82 183 136',  /* #52b788 */
      '--color-background-700': '64 145 108',  /* #40916c */

      /* Typography */
      '--color-typography-900': '8 28 21',     /* #081c15 */
      '--color-typography-800': '27 67 50',    /* #1b4332 */
      '--color-typography-700': '45 106 79',   /* #2d6a4f */

      /* Primary */
      '--color-primary-50': '216 243 220',     /* #d8f3dc */
      '--color-primary-100': '183 228 199',    /* #b7e4c7 */
      '--color-primary-200': '149 213 178',    /* #95d5b2 */
      '--color-primary-300': '116 198 157',    /* #74c69d */
      '--color-primary-400': '82 183 136',     /* #52b788 */
      '--color-primary-500': '64 145 108',     /* #40916c */
      '--color-primary-600': '45 106 79',      /* #2d6a4f */
      '--color-primary-700': '27 67 50',       /* #1b4332 */
      '--color-primary-800': '19 52 39',
      '--color-primary-900': '8 28 21',        /* #081c15 */

      /* Border */
      '--color-border-200': '183 228 199',
      '--color-border-300': '149 213 178',
      '--color-border-700': '27 67 50',
    }),
  },
};
