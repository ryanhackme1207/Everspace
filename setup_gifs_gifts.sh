#!/bin/bash
# Quick setup script for GIFs and Gifts
# Run this manually if needed: bash setup_gifs_gifts.sh

echo "🚀 Setting up Gifts and GIFs..."

python manage.py setup_gifts_and_gifs --reset

echo "✅ Setup complete!"
echo "Visit your app and check:"
echo "  - Click the GIF button to see GIFs"
echo "  - Click the gift button to see gifts"
