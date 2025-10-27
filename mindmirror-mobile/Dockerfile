FROM node:20-slim

WORKDIR /app

# Install Expo CLI globally
RUN npm install -g expo-cli @expo/ngrok@^4.1.0

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (use legacy peer deps for React 19 compatibility)
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Expose ports
# 8081 - Metro bundler (React Native)
# 19000 - Expo DevTools
# 19001 - Expo DevTools (secure)
# 19002 - Expo DevTools (secure)
EXPOSE 8081 19000 19001 19002

# Start Expo with clear cache
# Use --lan to make it accessible from other machines on the network
CMD ["npx", "expo", "start", "--clear", "--lan"]
