import discord
from discord import app_commands
import openai
import os
import asyncio  # potrebné pre sleep

# načítanie tokenov z environment premenných
TOKEN = os.getenv("TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

openai.api_key = OPENAI_KEY

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.event
async def on_ready():
    print(f"✅ Prihlásený ako {client.user}")

@client.tree.command(name="idea", description="Vygeneruje AI nápad na zadanú tému")
async def idea(interaction: discord.Interaction, tema: str):
    await interaction.response.defer(thinking=True)

    # cooldown 1,5 sekundy pred volaním API
    await asyncio.sleep(1.5)

    prompt = f"Vymysli kreatívny nápad na tému: {tema}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        idea_text = response["choices"][0]["message"]["content"]
        await interaction.followup.send(f"💡 Nápad na *{tema}*:\n{idea_text}")
    except openai.error.RateLimitError:
        await interaction.followup.send("⚠️ Príliš veľa požiadaviek naraz, skúste o chvíľu znova.")
    except Exception as e:
        await interaction.followup.send(f"❌ Chyba pri generovaní nápadu: {e}")

client.run(TOKEN)
