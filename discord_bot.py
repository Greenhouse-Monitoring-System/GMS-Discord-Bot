import discord
import toml
import aiohttp
import asyncio
import os

with open('config.toml', 'r') as f:
    config = toml.load(f)

token = config["discord"]["APP_KEY"]
lastTime = None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

async def download_image(image_url, save_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                # Save the image to the local path
                with open(save_path, 'wb') as f:
                    f.write(await response.read())
                print(f"Image saved to {save_path}")
            else:
                print(f"Failed to download image: {response.status}")

async def fetch_conditions():
    global lastTime
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get("http://127.0.0.1:8080/get_current") as response:
                    if response.status == 200:
                        data = await response.json()
                        conditions = data["conditions"]
                        image_url = data["image_url"]

                        if conditions['time'] != lastTime:

                            await download_image(image_url, "static/now.jpg")

                            file = discord.File("static/now.jpg")
                            lastTime = conditions['time']

                            print(f"Fetched conditions: {conditions}")
                            # You can send this data to a user or process it as needed
                            # Example: Sending data to a specific user
                            user = await client.fetch_user("480182798989393950")
                            embed = discord.Embed(title="Greenhouse Monitor System", description="Current Stats", color=0x42d642)
                            embed.set_thumbnail(url="attachment://now.jpg")
                            embed.add_field(name="Temperature", value=f"{conditions['temperature']} C", inline=True)
                            embed.add_field(name="Humidity", value=f"{conditions['humidity']} %", inline=True)
                            embed.add_field(name='\u200b', value='\u200b', inline=False)
                            embed.add_field(name="Soil Moisture", value=f"{conditions['soil_moisture']}", inline=True)
                            embed.add_field(name="Water Level", value=f"{conditions['water_level']}", inline=True)
                            await user.send(file = file,embed=embed)
            except Exception as e:
                print(f"Error fetching conditions: {e}")
            await asyncio.sleep(10)  # Wait 10 seconds before the next request

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    user = await client.fetch_user("480182798989393950")
    client.loop.create_task(fetch_conditions())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

async def message_member(user_id, msg):
    user = await client.fetch_user(user_id)
    await user.send(msg)

def start_bot():
    client.run(token)

if __name__ == "__main__":
    start_bot()