#!/bin/bash
# AEGIS Redis Initialization Script
# Run after Redis container is up to set governance defaults

echo "Initializing AEGIS Redis governance keys..."

# Kill switch: true = system enabled, false = emergency stop
redis-cli SET gov:killswitch true
echo "✅ Set gov:killswitch = true (System ENABLED)"

# Mode: observe | assist | execute
redis-cli SET gov:mode assist
echo "✅ Set gov:mode = assist (AI writes + human review)"

# Verify
echo ""
echo "📊 Current governance state:"
redis-cli GET gov:killswitch
redis-cli GET gov:mode

echo ""
echo "🛡️ AEGIS Redis initialized successfully!"
