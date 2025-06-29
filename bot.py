import os
import requests
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 Your keys here
TELEGRAM_BOT_TOKEN = ""
GROQ_API_KEY = ""
MODEL = "llama3-8b-8192"

# 🧠 Ask Groq
def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant. Reply clearly and briefly."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print("❌ Groq API Error:", response.text)
        return "Sorry, Main AI se reply nahi le pa raha."

# 🎧 Voice to Text
def voice_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        return "Sorry, Main samjhi nahi."

# ▶️ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎙️ Send me a voice message, and I’ll reply with my voice too!")

# 🗣️ Voice message handler
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = await update.message.voice.get_file()
    voice_path_ogg = "voice.ogg"
    voice_path_wav = "voice.wav"
    reply_path_mp3 = "reply.mp3"

    # Download and convert voice
    await voice.download_to_drive(voice_path_ogg)
    sound = AudioSegment.from_ogg(voice_path_ogg)
    sound.export(voice_path_wav, format="wav")

    # Convert to text
    user_text = voice_to_text(voice_path_wav)
    await update.message.reply_text(f"🗣️ Apne kaha: {user_text}")
    await update.message.reply_text("🤖 Soch rahi hu...")
    print(f"🧑‍💬 User said: {user_text}")


    # Get AI reply
    ai_reply = ask_groq(user_text)
    print(f"🤖 AI replied: {ai_reply}")
    await update.message.reply_text(ai_reply)  # 💬 Text reply



    # Send voice reply
    tts = gTTS(text=ai_reply, lang='en')
    tts.save(reply_path_mp3)
    with open(reply_path_mp3, "rb") as voice_reply:
        await update.message.reply_voice(voice=voice_reply)

# 💬 Text message handler (optional)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text("🤖 Soch rahi hu...")
    ai_reply = ask_groq(user_input)
    await update.message.reply_text(ai_reply)

# 🚀 Bot entry
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Rushang's AI Assitant is running for uhh...")
    app.run_polling()

if __name__ == "__main__":
    main()
