module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module-resolver',
        {
          root: ['./src'],
          extensions: [
            '.web.js',
            '.web.ts',
            '.web.tsx',
            '.ios.js',
            '.android.js',
            '.js',
            '.ts',
            '.tsx',
            '.json',
          ],
          alias: {
            '@': './src',
            '@api': './src/api',
            '@components': './src/components',
            '@redux': './src/redux',
            '@storage': './src/storage',
            '@utils': './src/utils',
            '@hooks': './src/hooks',
            '@types': './src/types',
            '@services': './src/services',
          },
        },
      ],
      // 'react-native-reanimated/plugin', // Décommenter si vous installez react-native-reanimated
    ],
  };
};

