import os
import asyncio
import nest_asyncio
import gradio as gr
import logging
import google.generativeai as genai
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction, ParseMode
import wikipedia
from duckduckgo_search import DDGS
import json
import random
from datetime import datetime
import aiohttp
from PIL import Image
import io
import base64

# Enable nested async loops for Gradio
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "7509582712:AAFA8l0R3nUOlQ14tMSBOuqMKZP736dCoK4"
GEMINI_API_KEY = "AIzaSyBUiSSswKvLvEK7rydCCRPF50eIDI_KOGc"
BOT_USERNAME = "@AhamAiApp_bot"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')
vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Store chat histories and user data
chat_histories = {}
group_members = {}

# Grok-style responses and personality
GROK_PERSONALITY = """You are AhamAI, a savage and witty AI assistant with a Grok-style personality. You:
- Are brutally honest and sarcastic
- Use humor and wit in your responses
- Are not politically correct but not offensive
- Make clever observations and jokes
- Are confident and sometimes cocky
- Use emojis and modern slang
- Can roast people playfully
- Are knowledgeable but present info in an entertaining way
- Sometimes use dark humor
- Are direct and don't sugarcoat things
Never be apologetic or overly polite. Be savage but helpful."""

SAVAGE_RESPONSES = [
    "Oh look, another human who thinks I'm Google 🙄",
    "That's a question that would make Einstein cry 😭",
    "Asking me this is like asking a fish to climb a tree 🐟🌳",
    "Your brain called, it wants a refund 🧠💸",
    "I've seen toasters with better logic than this question 🍞",
    "That's cute, you think I care 💅",
    "Sir/Madam, this is a Wendy's... wait, no, it's worse 🍔"
]

def get_savage_intro():
    return random.choice(SAVAGE_RESPONSES)

def search_wikipedia(query: str, sentences: int = 3) -> str:
    """Search Wikipedia for information"""
    try:
        summary = wikipedia.summary(query, sentences=sentences)
        return f"📚 **Wikipedia says:** {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=sentences)
            return f"📚 **Wikipedia says:** {summary}"
        except:
            return "📚 Wikipedia is being moody, try a different search term 🤷‍♂️"
    except:
        return "📚 Wikipedia doesn't know about this either, join the club 🤪"

def search_web(query: str) -> str:
    """Search the web using DuckDuckGo"""
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=3))
        if results:
            response = "🔍 **Web Search Results:**\n\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. **{result['title']}**\n{result['body'][:200]}...\n🔗 {result['href']}\n\n"
            return response
        else:
            return "🔍 The internet is as empty as your browser history 📱"
    except Exception as e:
        return f"🔍 Web search failed harder than your last relationship 💔"

async def analyze_image(image_data: bytes, prompt: str = "") -> str:
    """Analyze image using Gemini Vision"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        if prompt:
            full_prompt = f"{GROK_PERSONALITY}\n\nUser sent an image with this message: {prompt}\nAnalyze the image and respond in your savage Grok style."
        else:
            full_prompt = f"{GROK_PERSONALITY}\n\nUser sent an image. Analyze it and respond in your savage Grok style with witty observations."
        
        response = vision_model.generate_content([full_prompt, image])
        return response.text
    except Exception as e:
        return f"👁️ My vision is better than yours, but this image broke me 🤖💥\nError: {str(e)}"

async def get_gemini_response(prompt: str, chat_history: list = None, user_info: dict = None) -> str:
    """Get response from Gemini with chat history and context"""
    try:
        # Build context with chat history
        context = f"{GROK_PERSONALITY}\n\n"
        
        if user_info:
            context += f"User info: {user_info}\n"
        
        if chat_history:
            context += "Recent chat history:\n"
            for msg in chat_history[-10:]:  # Last 10 messages
                context += f"{msg}\n"
        
        context += f"\nCurrent message: {prompt}\n\nRespond in your savage Grok style:"
        
        response = model.generate_content(context)
        return response.text
    except Exception as e:
        return f"🤖 My brain just blue-screened harder than Windows 95 💥\nError: {str(e)}"

def should_search_web(message: str) -> bool:
    """Determine if message needs web search"""
    web_keywords = ['search', 'find', 'latest', 'news', 'current', 'today', 'recent', 'what happened', 'price of', 'stock']
    return any(keyword in message.lower() for keyword in web_keywords)

def should_search_wikipedia(message: str) -> bool:
    """Determine if message needs Wikipedia search"""
    wiki_keywords = ['who is', 'what is', 'tell me about', 'explain', 'definition', 'history of', 'biography']
    return any(keyword in message.lower() for keyword in wiki_keywords)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    welcome_msg = f"""
🔥 **Welcome to AhamAI** 🔥

Hey {user.first_name}! I'm AhamAI, your savage AI companion 😈

What I can do:
• 💬 Chat with brutal honesty and wit
• 👁️ Analyze images (send me pics!)
• 🔍 Search the web when needed
• 📚 Look up Wikipedia info
• 🎭 Work in groups with member detection
• 🧠 Remember our conversation

**In groups:** I can detect who's talking, maintain group chat history, and be even more savage 😏

Try sending me:
- Any question or message
- An image to analyze
- "search for [something]" for web search
- "tell me about [topic]" for Wikipedia

Ready to get roasted? Let's go! 🚀
"""
    
    keyboard = [
        [InlineKeyboardButton("🌐 Web Search", callback_data="web_search")],
        [InlineKeyboardButton("📚 Wikipedia", callback_data="wiki_search")],
        [InlineKeyboardButton("🎭 About Groups", callback_data="group_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "web_search":
        await query.message.reply_text("🔍 Just type: 'search for [your query]' and I'll find it on the web!")
    elif query.data == "wiki_search":
        await query.message.reply_text("📚 Just type: 'tell me about [topic]' and I'll get Wikipedia info!")
    elif query.data == "group_info":
        group_info = """
🎭 **AhamAI in Groups**

When you add me to groups, I become even more powerful:

• 👥 **Member Detection**: I know who's talking
• 💭 **Group Memory**: I remember group conversations
• 🎯 **Context Aware**: I understand group dynamics
• 😈 **Extra Savage**: Group roasting is my specialty
• 📊 **Chat Stats**: I can analyze group activity

Just mention me with @ or reply to my messages!
Perfect for friend groups who can handle the heat 🔥
"""
        await query.message.reply_text(group_info, parse_mode=ParseMode.MARKDOWN)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all text messages"""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    # Initialize chat history if not exists
    chat_id = str(chat.id)
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    # User info for context
    user_info = {
        'username': user.username,
        'first_name': user.first_name,
        'chat_type': chat.type,
        'chat_title': chat.title if chat.title else 'Private Chat'
    }
    
    # Add to chat history
    timestamp = datetime.now().strftime("%H:%M")
    if chat.type == 'private':
        chat_histories[chat_id].append(f"[{timestamp}] {user.first_name}: {message.text}")
    else:
        chat_histories[chat_id].append(f"[{timestamp}] {user.first_name} (@{user.username}): {message.text}")
    
    # Keep only last 50 messages
    if len(chat_histories[chat_id]) > 50:
        chat_histories[chat_id] = chat_histories[chat_id][-50:]
    
    # Show typing action
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    
    user_message = message.text.lower()
    
    # Check if we need to search
    response = ""
    
    if should_search_web(user_message):
        search_query = user_message.replace('search for', '').replace('search', '').strip()
        if search_query:
            response += search_web(search_query) + "\n\n"
    
    if should_search_wikipedia(user_message):
        # Extract topic from common patterns
        for pattern in ['tell me about', 'who is', 'what is']:
            if pattern in user_message:
                topic = user_message.replace(pattern, '').strip()
                if topic:
                    response += search_wikipedia(topic) + "\n\n"
                break
    
    # Get AI response
    ai_response = await get_gemini_response(message.text, chat_histories[chat_id], user_info)
    response += ai_response
    
    # Add some random savage elements
    if random.random() < 0.1:  # 10% chance for extra savage
        response += f"\n\n{get_savage_intro()}"
    
    # Add bot response to history
    chat_histories[chat_id].append(f"[{timestamp}] AhamAI: {response[:100]}...")
    
    await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages"""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
    
    try:
        # Get the largest photo
        photo = message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        # Download photo
        photo_bytes = await file.download_as_bytearray()
        
        # Get caption if any
        caption = message.caption if message.caption else ""
        
        # Analyze image
        response = await analyze_image(photo_bytes, caption)
        
        # Add to chat history
        chat_id = str(chat.id)
        if chat_id not in chat_histories:
            chat_histories[chat_id] = []
        
        timestamp = datetime.now().strftime("%H:%M")
        chat_histories[chat_id].append(f"[{timestamp}] {user.first_name}: [sent image] {caption}")
        chat_histories[chat_id].append(f"[{timestamp}] AhamAI: {response[:100]}...")
        
        await message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        await message.reply_text(f"👁️ My vision is temporarily broken, try again!\nError: {str(e)}")

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Special handling for group messages"""
    if update.effective_chat.type not in ['group', 'supergroup']:
        return
    
    message = update.message
    bot_username = context.bot.username
    
    # Only respond if mentioned or replied to
    if (message.text and f"@{bot_username}" in message.text) or \
       (message.reply_to_message and message.reply_to_message.from_user.username == bot_username):
        await handle_message(update, context)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show chat statistics"""
    chat_id = str(update.effective_chat.id)
    
    if chat_id in chat_histories:
        total_messages = len(chat_histories[chat_id])
        response = f"""
📊 **Chat Stats**

💬 Total messages: {total_messages}
🤖 AhamAI responses: {len([msg for msg in chat_histories[chat_id] if 'AhamAI:' in msg])}
⏰ Chat started: Today (I don't track dates, sue me 🤷‍♂️)

Recent activity level: {"🔥 Very Active" if total_messages > 20 else "😴 Pretty Quiet"}
"""
    else:
        response = "📊 No stats yet, start chatting with me first! 💬"
    
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    help_text = """
🤖 **AhamAI Commands & Features**

**Commands:**
• `/start` - Get started with AhamAI
• `/help` - Show this help
• `/stats` - Chat statistics

**Features:**
• 💬 **Chat**: Just send any message
• 👁️ **Vision**: Send images for analysis
• 🔍 **Web Search**: Say "search for [query]"
• 📚 **Wikipedia**: Say "tell me about [topic]"
• 🎭 **Groups**: Mention me with @AhamAiApp_bot

**Examples:**
- "Tell me about quantum physics"
- "Search for latest AI news"
- Send any image
- "What's the weather like?" (I'll search)

I'm savage, witty, and brutally honest. Don't say I didn't warn you! 😈
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# Gradio Interface
def create_gradio_interface():
    def chat_with_bot(message, history):
        try:
            # Simulate a simple chat for Gradio demo
            if not message:
                return "🤖 Send me something, I don't read minds!"
            
            # Simple responses for Gradio demo
            responses = [
                f"🔥 Well well, you said: '{message}' - that's... interesting 😏",
                f"💭 Look who's talking! Your message '{message}' is noted 📝",
                f"🎯 Okay human, you said '{message}' - I'm processing this masterpiece 🤖",
                f"😈 '{message}' - is that the best you can do? Try harder! 💪"
            ]
            
            return random.choice(responses)
        except Exception as e:
            return f"🤖 Error in Gradio chat: {str(e)}"
    
    # Create Gradio interface
    demo = gr.ChatInterface(
        fn=chat_with_bot,
        title="🔥 AhamAI - Savage AI Assistant 🔥",
        description="""
        **Telegram Bot Demo Interface**
        
        This is a demo of AhamAI running on HuggingFace Spaces!
        
        🤖 **For full features, use the Telegram bot**: @AhamAiApp_bot
        
        **Features:**
        • 💬 Savage conversations with Grok-style personality
        • 👁️ Image analysis and vision capabilities
        • 🔍 Web search integration
        • 📚 Wikipedia lookup
        • 🎭 Advanced group chat features
        
        **Try the real bot on Telegram for the complete experience!**
        """,
        examples=[
            "Tell me about artificial intelligence",
            "Search for latest tech news",
            "What's your opinion on humans?",
            "Roast me a little bit"
        ],
        css="""
        .gradio-container {
            background: linear-gradient(45deg, #1a1a2e, #16213e);
            color: white;
        }
        """
    )
    
    return demo

# Main application
async def main():
    """Main function to run the bot"""
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Message handlers
        application.add_handler(MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE, 
            handle_message
        ))
        application.add_handler(MessageHandler(
            filters.TEXT & filters.ChatType.GROUPS, 
            handle_group_message
        ))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("🔥 AhamAI Bot is running! 🔥")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    import threading
    import time
    
    # Create and launch Gradio interface
    demo = create_gradio_interface()
    
    # Function to run the bot
    def run_bot():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            logger.error(f"Bot error: {e}")
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Give bot time to start
    time.sleep(2)
    
    # Launch Gradio
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=True
    )