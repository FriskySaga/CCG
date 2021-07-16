from discord.ext import commands
import json
from os import path

import tasks.timed_reminder as timed_reminder

authFile = open(path.join('config', 'auth.json'))
auth = json.load(authFile)
authFile.close()

serverIdsFile = open(path.join('config', 'server_ids.json'))
serverIds = json.load(serverIdsFile)
serverIdsFile.close()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  generalChannel = bot.get_channel(serverIds['Channel'])
  await generalChannel.send("I have been awakened from my slumber...")
  timed_reminder.TimedReminder(bot, serverIds).annoy.start()

bot.run(auth['token'])
