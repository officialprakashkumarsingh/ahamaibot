#!/usr/bin/env python3
"""
Simple launcher for AhamAI Bot - for testing purposes
"""

import sys
import os
import asyncio
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required imports work"""
    try:
        import telegram
        print("✅ python-telegram-bot imported successfully")
        
        import google.generativeai as genai
        print("✅ google-generativeai imported successfully")
        
        import gradio as gr
        print("✅ gradio imported successfully")
        
        import wikipedia
        print("✅ wikipedia imported successfully")
        
        from duckduckgo_search import DDGS
        print("✅ duckduckgo-search imported successfully")
        
        import nest_asyncio
        print("✅ nest-asyncio imported successfully")
        
        from PIL import Image
        print("✅ Pillow imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test bot configuration"""
    try:
        from config import BOT_TOKEN, GEMINI_API_KEY, BOT_USERNAME
        print("✅ Configuration imported successfully")
        
        if BOT_TOKEN and GEMINI_API_KEY:
            print("✅ API keys are configured")
        else:
            print("⚠️ Some API keys might be missing")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_bot_creation():
    """Test basic bot creation"""
    try:
        from telegram import Bot
        from config import BOT_TOKEN
        
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot connected successfully: @{me.username}")
        return True
    except Exception as e:
        print(f"❌ Bot connection error: {e}")
        return False

def main():
    """Main test function"""
    print("🔥 AhamAI Bot - System Test 🔥")
    print("=" * 40)
    
    # Test imports
    print("\n📦 Testing imports...")
    if not test_imports():
        print("❌ Import test failed!")
        return False
    
    # Test configuration
    print("\n⚙️ Testing configuration...")
    if not test_configuration():
        print("❌ Configuration test failed!")
        return False
    
    # Test bot connection
    print("\n🤖 Testing bot connection...")
    try:
        result = asyncio.run(test_bot_creation())
        if not result:
            print("❌ Bot connection test failed!")
            return False
    except Exception as e:
        print(f"❌ Async test error: {e}")
        return False
    
    print("\n🎉 All tests passed! Bot is ready to deploy!")
    print("\n🚀 To run the full bot, execute: python3 app.py")
    return True

if __name__ == "__main__":
    main()