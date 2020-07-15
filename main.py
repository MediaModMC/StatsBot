from discord.ext import tasks
import discord
import aiohttp
import json

client = discord.Client()
token = ""
channel = 0

with open("config.json") as file:
    data = json.load(file)
    token = data["token"]
    channel = int(data["channel"])


@tasks.loop(minutes=1)
async def check_status():
    print("Checking MediaMod status...")
    if not hasattr(client, "session") or client.session.closed:
        client.session = aiohttp.ClientSession(raise_for_status=True)
    if not hasattr(client, "message"):
        client.message = None
    try:
        json = await (await client.session.get("https://mediamodapi.cbyrne.dev/stats")).json()

        embed = discord.Embed(
            title="MediaMod Stats",
            description="How many people are using MediaMod? (Note: this is only people with snooper enabled)",
            color=0x00ff00
        ).add_field(
            name="Online Users",
            value=json["allOnlineUsers"],
            inline=False
        ).add_field(
            name="All Users",
            value=json["allUsers"],
            inline=False
        )

        if not client.message:
            client.message = await client.get_channel(channel).send(embed=embed)
        else:
            await client.message.edit(embed=embed)
        print("Done!")

    except aiohttp.ClientResponseError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    check_status.start()

if token and channel:
    client.run(token)
else:
    print('Missing "token" and "channel" values in config.json')
    quit()