import discord
import json
import requests
import time

from requests.exceptions import HTTPError

client = discord.Client()
token = ""

with open("config.json") as file: 
    data = json.load(file)
    token = data['token']

async def checkStatus():
    print("Checking MediaMod status...")
    try:
        response = requests.get('https://mediamodapi.cbyrne.dev/stats')
        response.raise_for_status()
        json = response.json()
        
        embedVar = discord.Embed(title="MediaMod Stats", description="How many people are using MediaMod? (Note: this is only people with snooper enabled)", color=0x00ff00)
        embedVar.add_field(name="Online Users", value=json["allOnlineUsers"], inline=False)
        embedVar.add_field(name="All Users", value=json["allUsers"], inline=False)

        print("Done!")

        channel = await client.fetch_channel(732583083953618965)
        id = channel.last_message_id
        if id is None:
            await channel.send(embed = embedVar)
        else:
            previous = await channel.fetch_message(id)
            await previous.edit(embed = embedVar)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    time.sleep(60)

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    while True:
        await checkStatus()

client.run(token)