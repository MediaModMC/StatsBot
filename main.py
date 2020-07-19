from discord.ext import tasks
import discord
import aiohttp
import json

client = discord.Client()
token = ""
channel_id = 0

try:
    with open("config.json") as f:
        data = json.load(f)
        token = data["token"]
        channel_id = int(data["channel"])
except (FileNotFoundError, KeyError):
    print("Make sure you've created config.json and entered the correct information in it (see readme for more info)")
    quit()


@tasks.loop(minutes=1)
async def check_status(channel):
    print("Checking MediaMod status...")
    if not hasattr(client, "session") or client.session.closed:
        client.session = aiohttp.ClientSession(raise_for_status=True)
    if not hasattr(client, "message"):
        client.message = None
    try:
        json = await (await client.session.get("https://mediamodapi.cbyrne.dev/stats")).json()
        betaJson = await (await client.session.get("https://mediamodapi.conorthedev.me/stats")).json()

        embed = discord.Embed(
            title="MediaMod Stats",
            description="How many people are using MediaMod? (Note: this is only people with snooper enabled)",
            color=0x00ff00
        ).add_field(
            name="Stable Users",
            value="**Online Users**: " + str(json["allOnlineUsers"]) + "\n**All Users**: " + str(json["allUsers"]),
            inline=False
        ).add_field(
            name="Beta Users",
            value="**Online Users**: " + str(betaJson["allOnlineUsers"]) + "\n**All Users**: " + str(betaJson["allUsers"]),
            inline=False
        )

        try:
            if not client.message.embeds:
                client.message = await client.message.edit(content=None, embed=embed)
            else:
                previous = client.message.embeds[0]
                if previous.to_dict() != embed.to_dict():
                    await client.message.edit(embed=embed)
        except (discord.NotFound, AttributeError):
            client.message = await channel.send(embed=embed)
        print("Done!")

    except aiohttp.ClientResponseError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    channel = client.get_channel(channel_id)
    client.message = None
    async for m in channel.history(limit=5):
        if m.author.id == client.user.id and m.embeds:
            client.message = m
            break
    if not client.message:
        client.message = await channel.send('Loading stats...')
    check_status.start(channel)

if token and channel_id:
    client.run(token)
else:
    print('Missing "token" and "channel" values in config.json')
    quit()
