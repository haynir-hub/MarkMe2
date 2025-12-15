#!/bin/bash
# Install FFmpeg on macOS

echo "🎬 Installing FFmpeg for Video Markme..."
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found!"
    echo ""
    echo "Please install Homebrew first by running:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    echo "After installing Homebrew, run this script again."
    exit 1
fi

echo "✅ Homebrew found"
echo ""

# Install FFmpeg
echo "📦 Installing FFmpeg via Homebrew..."
brew install ffmpeg

# Verify installation
if command -v ffmpeg &> /dev/null; then
    echo ""
    echo "✅ FFmpeg installed successfully!"
    echo ""
    echo "Version:"
    ffmpeg -version | head -n 1
    echo ""
    echo "🎉 You can now export videos with audio!"
else
    echo ""
    echo "❌ FFmpeg installation failed"
    echo "Please try installing manually with: brew install ffmpeg"
    exit 1
fi
