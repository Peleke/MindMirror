const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');
  
const config = getDefaultConfig(__dirname, { isCSSEnabled: true });

// Ensure Metro recognizes .lottie animation bundles
config.resolver = config.resolver || {};
config.resolver.assetExts = config.resolver.assetExts || [];
if (!config.resolver.assetExts.includes('lottie')) {
  config.resolver.assetExts.push('lottie');
}
  
module.exports = withNativeWind(config, { input: './global.css' });