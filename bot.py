import discord
from discord import app_commands
import requests
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Discord setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# 🔹 Function: Ask Groq API
def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Error: {str(e)}"


# 🔹 Function: Split long messages (Discord limit = 2000)
def split_message(text, max_length=2000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


# 🔹 Event: Bot Ready
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot is online as {client.user}")


# 🔥 SLASH COMMAND
@tree.command(name="obot", description="Ask AI anything")
async def obot(interaction: discord.Interaction, message: str):

    # Show "thinking..."
    await interaction.response.defer()

    # Get AI reply
    reply = ask_groq(message)

    # Split long response
    parts = split_message(reply)

    # Send each part
    for part in parts:
        await interaction.followup.send(part)


# Run bot
client.run(DISCORD_TOKEN)