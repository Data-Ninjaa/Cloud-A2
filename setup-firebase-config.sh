#!/bin/sh

# Replace the Firebase configuration in the built index.html to use emulator
CONFIG_START="<script>var firebaseConfig = {"
CONFIG_END="};</script>"

# Find and replace Firebase configuration
if [ "$NODE_ENV" = "production" ]; then
  echo "Using production Firebase settings"
else
  echo "Setting up Firebase emulator configuration"
  # Replace any references to the real Firebase project with emulator settings
  sed -i 's|firebase.initializeApp(firebaseConfig);|firebase.initializeApp(firebaseConfig); \
  if(typeof connectFirestoreEmulator === "function") { \
    connectFirestoreEmulator(getFirestore(), "firebase-emulator", 9199); \
    connectAuthEmulator(getAuth(), "http://firebase-emulator:9099"); \
  }|g' /usr/share/nginx/html/static/js/*.js
fi

# Start nginx
exec nginx -g 'daemon off;'
