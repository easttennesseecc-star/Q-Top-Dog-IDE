module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  transform: {
    "^.+\\.(ts|tsx)$": ["ts-jest", { tsconfig: "<rootDir>/tsconfig.json" }],
    "^.+\\.svg$": "<rootDir>/svgTransform.cjs",
  },
   moduleNameMapper: {
     '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
     '\\.svg$': '<rootDir>/svgTransform.cjs',
   },
};
