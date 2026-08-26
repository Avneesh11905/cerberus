// @ts-check

import { tanstackConfig } from '@tanstack/eslint-config'

export default [
  ...tanstackConfig,
  {
    files: ['**/*.{ts,tsx,mts,cts}'],
    rules: {
      'import/no-cycle': 'off',
      'import/order': 'off',
      'sort-imports': 'off',
      '@typescript-eslint/array-type': 'off',
      '@typescript-eslint/require-await': 'off',
      'pnpm/json-enforce-catalog': 'off',
      '@typescript-eslint/no-unnecessary-condition': 'error',
      'no-shadow': 'error',
    },
  },
  {
    ignores: [
    'eslint.config.js',
    'prettier.config.js',
    '.vercel/**',
    'dist/**',
    'node_modules/**',
  ],
  },
]
