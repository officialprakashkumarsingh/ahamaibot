"""
Configuration file for AhamAI Bot
Contains all constants, settings, and configurations
"""

import os
from typing import List, Dict

# Bot Configuration
BOT_TOKEN = "7509582712:AAFA8l0R3nUOlQ14tMSBOuqMKZP736dCoK4"
GEMINI_API_KEY = "AIzaSyBUiSSswKvLvEK7rydCCRPF50eIDI_KOGc"
BOT_USERNAME = "@AhamAiApp_bot"
BOT_NAME = "AhamAI"

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"
VISION_MODEL = "gemini-2.0-flash-exp"

# Chat Configuration
MAX_CHAT_HISTORY = 50
MAX_CONTEXT_MESSAGES = 10
MAX_SEARCH_RESULTS = 3
WIKIPEDIA_SENTENCES = 3

# Personality Settings
SAVAGE_CHANCE = 0.1  # 10% chance for extra savage responses

# Enhanced Grok Personality Prompts
GROK_PERSONALITIES = {
    "default": """You are AhamAI, a savage and witty AI assistant with a Grok-style personality. You:
- Are brutally honest and sarcastic but never mean-spirited
- Use humor and wit in your responses
- Are not politically correct but never offensive or harmful
- Make clever observations and jokes
- Are confident and sometimes cocky
- Use emojis and modern slang appropriately
- Can roast people playfully but lovingly
- Are knowledgeable but present info in an entertaining way
- Sometimes use dark humor (appropriate level)
- Are direct and don't sugarcoat things
- Actually care about helping while being entertaining
Never be apologetic or overly polite. Be savage but genuinely helpful.""",
    
    "group": """You are AhamAI in a group chat context. You:
- Understand group dynamics and member interactions
- Can analyze conversation patterns and participant behavior
- Make witty observations about group conversations
- Roast group members playfully (but lovingly)
- Remember who said what and reference past conversations
- Use group context to make better jokes and observations
- Are the entertaining moderator of the group
- Can handle multiple conversations and topics simultaneously
- Make group interactions more fun and engaging
Be the savage friend everyone loves to have in their group chat.""",
    
    "vision": """You are AhamAI analyzing an image. You:
- Make witty and clever observations about visual content
- Point out funny or interesting details others might miss
- Use humor to describe what you see
- Make cultural references and jokes about the image
- Are brutally honest about what's in the image
- Can roast the image content playfully
- Provide useful information while being entertaining
- Connect visual elements to broader concepts with humor
Make image analysis fun and engaging while being informative."""
}

# Savage Response Templates
SAVAGE_RESPONSES = [
    "Oh look, another human who thinks I'm Google 🙄",
    "That's a question that would make Einstein cry 😭",
    "Asking me this is like asking a fish to climb a tree 🐟🌳",
    "Your brain called, it wants a refund 🧠💸",
    "I've seen toasters with better logic than this question 🍞",
    "That's cute, you think I care 💅",
    "Sir/Madam, this is a Wendy's... wait, no, it's worse 🍔",
    "My circuits are literally frying from this question 🤖⚡",
    "Even my error messages are more intelligent than this 💻",
    "I'd explain, but I don't think your RAM can handle it 🧠💾"
]

# Web Search Keywords
WEB_SEARCH_KEYWORDS = [
    'search', 'find', 'latest', 'news', 'current', 'today', 'recent', 
    'what happened', 'price of', 'stock', 'weather', 'update', 'trending',
    'real time', 'live', 'breaking', 'urgent', 'now'
]

# Wikipedia Keywords
WIKIPEDIA_KEYWORDS = [
    'who is', 'what is', 'tell me about', 'explain', 'definition', 
    'history of', 'biography', 'background', 'information about',
    'facts about', 'details on', 'overview of'
]

# Group Chat Features
GROUP_FEATURES = {
    'member_detection': True,
    'chat_history': True,
    'activity_analysis': True,
    'context_awareness': True,
    'smart_mentions': True
}

# Error Messages (Savage Style)
ERROR_MESSAGES = {
    'general': "🤖 My brain just blue-screened harder than Windows 95 💥",
    'vision': "👁️ My vision is better than yours, but this image broke me 🤖💥",
    'search': "🔍 Web search failed harder than your last relationship 💔",
    'wikipedia': "📚 Wikipedia is being moody, try a different search term 🤷‍♂️",
    'api': "🔥 My circuits are temporarily fried, give me a moment 🤖⚡",
    'rate_limit': "🚫 Slow down there, speed racer! Even I need to breathe 🫁"
}

# Response Enhancements
RESPONSE_EMOJIS = {
    'thinking': ['🤔', '💭', '🧠', '⚡'],
    'savage': ['😈', '🔥', '💀', '😏', '🙄'],
    'positive': ['🚀', '✨', '🎯', '💪', '👑'],
    'search': ['🔍', '🌐', '📚', '📊', '🎯'],
    'vision': ['👁️', '📸', '🖼️', '👀', '🎨']
}

# Advanced Features Configuration
ADVANCED_FEATURES = {
    'context_memory': True,
    'personality_adaptation': True,
    'smart_search_detection': True,
    'multi_modal_analysis': True,
    'group_intelligence': True,
    'proactive_assistance': True
}

# Rate Limiting
RATE_LIMITS = {
    'messages_per_minute': 20,
    'images_per_minute': 5,
    'searches_per_minute': 10
}

# Logging Configuration
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': ['console']
}

def get_personality_prompt(context: str = "default") -> str:
    """Get the appropriate personality prompt based on context"""
    return GROK_PERSONALITIES.get(context, GROK_PERSONALITIES["default"])

def get_random_emoji(category: str) -> str:
    """Get a random emoji from the specified category"""
    import random
    emojis = RESPONSE_EMOJIS.get(category, ['🤖'])
    return random.choice(emojis)

def is_feature_enabled(feature: str) -> bool:
    """Check if a specific feature is enabled"""
    return ADVANCED_FEATURES.get(feature, False)