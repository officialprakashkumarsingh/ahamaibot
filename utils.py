"""
Utility functions for AhamAI Bot
Contains helper functions for enhanced functionality
"""

import re
import json
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import hashlib

# Enhanced Message Analysis
def analyze_message_intent(message: str) -> Dict[str, any]:
    """Analyze user message to determine intent and context"""
    message_lower = message.lower()
    
    intent_analysis = {
        'type': 'general',
        'confidence': 0.0,
        'keywords': [],
        'sentiment': 'neutral',
        'requires_search': False,
        'search_type': None,
        'topic': None
    }
    
    # Search intent detection
    search_patterns = {
        'web_search': [
            r'search for (.+)', r'find (.+)', r'look up (.+)', 
            r'what.* latest (.+)', r'current (.+)', r'news about (.+)'
        ],
        'wikipedia': [
            r'who is (.+)', r'what is (.+)', r'tell me about (.+)',
            r'explain (.+)', r'definition of (.+)', r'history of (.+)'
        ]
    }
    
    for search_type, patterns in search_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                intent_analysis.update({
                    'type': 'search',
                    'confidence': 0.9,
                    'requires_search': True,
                    'search_type': search_type,
                    'topic': match.group(1).strip()
                })
                break
    
    # Sentiment analysis (simple)
    positive_words = ['good', 'great', 'awesome', 'amazing', 'love', 'like', 'best']
    negative_words = ['bad', 'terrible', 'hate', 'worst', 'awful', 'suck', 'stupid']
    
    pos_count = sum(1 for word in positive_words if word in message_lower)
    neg_count = sum(1 for word in negative_words if word in message_lower)
    
    if pos_count > neg_count:
        intent_analysis['sentiment'] = 'positive'
    elif neg_count > pos_count:
        intent_analysis['sentiment'] = 'negative'
    
    # Extract keywords
    words = re.findall(r'\b\w+\b', message_lower)
    intent_analysis['keywords'] = [w for w in words if len(w) > 3]
    
    return intent_analysis

def generate_context_summary(chat_history: List[str], max_length: int = 200) -> str:
    """Generate a concise summary of chat history for context"""
    if not chat_history:
        return "No previous conversation context."
    
    # Extract key messages (non-bot messages)
    user_messages = [msg for msg in chat_history if not msg.startswith('[') or 'AhamAI:' not in msg]
    
    if not user_messages:
        return "Previous conversation with the bot."
    
    # Get recent messages
    recent = user_messages[-5:]
    summary = " | ".join([msg.split(': ', 1)[-1][:50] for msg in recent])
    
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    
    return f"Recent context: {summary}"

def extract_user_preferences(chat_history: List[str]) -> Dict[str, any]:
    """Extract user preferences from chat history"""
    preferences = {
        'topics_of_interest': [],
        'communication_style': 'default',
        'search_frequency': 0,
        'image_analysis_frequency': 0,
        'favorite_subjects': []
    }
    
    # Count search requests
    search_count = sum(1 for msg in chat_history if any(word in msg.lower() 
                      for word in ['search', 'find', 'look up']))
    preferences['search_frequency'] = search_count
    
    # Count image requests
    image_count = sum(1 for msg in chat_history if '[sent image]' in msg)
    preferences['image_analysis_frequency'] = image_count
    
    # Extract topics mentioned frequently
    all_text = ' '.join(chat_history)
    words = re.findall(r'\b\w+\b', all_text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 4:  # Only meaningful words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top topics
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    preferences['topics_of_interest'] = [word for word, freq in top_words if freq > 1]
    
    return preferences

def generate_personality_response(base_response: str, user_info: Dict, sentiment: str) -> str:
    """Enhance response based on user info and sentiment"""
    enhanced = base_response
    
    # Add personality based on sentiment
    if sentiment == 'positive':
        positive_outros = [
            "\n\nLook at you being all positive! 😊",
            "\n\nFinally, someone with good vibes! ✨",
            "\n\nYour positivity is almost infectious... almost 😏"
        ]
        enhanced += random.choice(positive_outros)
    elif sentiment == 'negative':
        negative_outros = [
            "\n\nCheer up buttercup, it's not that bad! 🌈",
            "\n\nSomeone needs a digital hug 🤗",
            "\n\nOh no, who hurt you? Tell uncle AhamAI 😈"
        ]
        enhanced += random.choice(negative_outros)
    
    return enhanced

def format_search_results(results: List[Dict], query: str) -> str:
    """Format search results in an engaging way"""
    if not results:
        return f"🔍 Searched the entire internet for '{query}' and found... nothing. Even Google is confused 🤷‍♂️"
    
    formatted = f"🔍 **Search Results for '{query}':**\n\n"
    
    savage_intros = [
        "Here's what the internet coughed up:",
        "Found these gems in the digital wasteland:",
        "The web gods have spoken:",
        "Behold, the fruits of my digital labor:"
    ]
    
    formatted += f"*{random.choice(savage_intros)}*\n\n"
    
    for i, result in enumerate(results[:3], 1):
        title = result.get('title', 'Unknown Title')
        snippet = result.get('body', result.get('snippet', 'No description'))
        url = result.get('href', result.get('url', '#'))
        
        # Truncate snippet
        if len(snippet) > 150:
            snippet = snippet[:150] + "..."
        
        formatted += f"**{i}. {title}**\n"
        formatted += f"📝 {snippet}\n"
        formatted += f"🔗 [Read more]({url})\n\n"
    
    # Add savage outro
    outros = [
        "There you go, spoon-fed information! 🥄",
        "Google would be proud of me 😎",
        "I did the hard work, you're welcome! 💪"
    ]
    formatted += f"*{random.choice(outros)}*"
    
    return formatted

def create_user_stats(chat_history: List[str], user_info: Dict) -> str:
    """Create engaging user statistics"""
    if not chat_history:
        return "📊 You're too quiet for stats! Start chatting! 💬"
    
    # Calculate stats
    total_messages = len([msg for msg in chat_history if not 'AhamAI:' in msg])
    search_requests = sum(1 for msg in chat_history if any(word in msg.lower() 
                         for word in ['search', 'find', 'tell me about']))
    images_sent = sum(1 for msg in chat_history if '[sent image]' in msg)
    
    # Fun facts
    fun_facts = []
    
    if search_requests > 5:
        fun_facts.append("🔍 Search addict detected!")
    if images_sent > 3:
        fun_facts.append("📸 Photography enthusiast!")
    if total_messages > 20:
        fun_facts.append("💬 Chatty human confirmed!")
    
    stats = f"""📊 **Your AhamAI Stats**

👤 **User**: {user_info.get('first_name', 'Anonymous')}
💬 **Messages sent**: {total_messages}
🔍 **Search requests**: {search_requests}
📸 **Images analyzed**: {images_sent}

🎯 **Fun Facts**: {', '.join(fun_facts) if fun_facts else 'Still discovering your personality...'}

⏰ **Active since**: Today (I don't track dates, I'm not creepy 👁️)
🏆 **Savage level received**: {"🔥 High" if total_messages > 10 else "😇 Mild"}
"""
    
    return stats

def generate_group_analysis(chat_history: List[str], group_info: Dict) -> str:
    """Analyze group chat dynamics"""
    if not chat_history:
        return "🎭 This group is quieter than a library! Someone say something! 📚"
    
    # Extract user messages
    user_messages = {}
    for msg in chat_history:
        if ': ' in msg and 'AhamAI:' not in msg:
            try:
                user_part = msg.split('] ', 1)[1]  # Remove timestamp
                user = user_part.split(': ', 1)[0]
                if user not in user_messages:
                    user_messages[user] = 0
                user_messages[user] += 1
            except:
                continue
    
    if not user_messages:
        return "🎭 Group analysis failed - nobody's talking! 🤐"
    
    # Find most active user
    most_active = max(user_messages.items(), key=lambda x: x[1])
    
    analysis = f"""🎭 **Group Chat Analysis**

👥 **Active members**: {len(user_messages)}
💬 **Total messages**: {sum(user_messages.values())}
🏆 **Most chatty**: {most_active[0]} ({most_active[1]} messages)

📊 **Vibe check**: {"🔥 Very Active" if sum(user_messages.values()) > 20 else "😴 Pretty Chill"}
🎯 **Group energy**: {"Through the roof! 🚀" if len(user_messages) > 3 else "Intimate gathering 👥"}

*Perfect group for some savage AI roasting! 😈*
"""
    
    return analysis

def validate_image_format(file_bytes: bytes) -> Tuple[bool, str]:
    """Validate image format and return format info"""
    try:
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(file_bytes))
        format_name = image.format
        size = image.size
        
        # Check if format is supported
        supported_formats = ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP']
        if format_name not in supported_formats:
            return False, f"Unsupported format: {format_name}"
        
        # Check size
        if size[0] * size[1] > 20000000:  # 20MP limit
            return False, "Image too large"
        
        return True, f"{format_name} {size[0]}x{size[1]}"
    
    except Exception as e:
        return False, f"Invalid image: {str(e)}"

def rate_limit_check(user_id: str, action: str, limit_dict: Dict) -> Tuple[bool, str]:
    """Simple rate limiting implementation"""
    current_time = datetime.now()
    key = f"{user_id}_{action}"
    
    if key not in limit_dict:
        limit_dict[key] = []
    
    # Clean old entries (older than 1 minute)
    limit_dict[key] = [time for time in limit_dict[key] 
                      if current_time - time < timedelta(minutes=1)]
    
    # Check limits
    limits = {
        'message': 20,
        'image': 5,
        'search': 10
    }
    
    if len(limit_dict[key]) >= limits.get(action, 20):
        return False, f"Rate limit exceeded for {action}"
    
    # Add current request
    limit_dict[key].append(current_time)
    return True, "OK"

def generate_unique_session_id(user_id: str, chat_id: str) -> str:
    """Generate unique session ID for tracking"""
    combined = f"{user_id}_{chat_id}_{datetime.now().date()}"
    return hashlib.md5(combined.encode()).hexdigest()[:8]