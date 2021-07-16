from discord.ext import commands
from json import load

import tasks.timed_reminder as timed_reminder

authFile = open('auth.json')
auth = load(authFile)
authFile.close()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  generalChannel = bot.get_channel(863494908668542979)
  await generalChannel.send("I have been awakened from my slumber...")
  timed_reminder.TimedReminder(bot).annoy.start()

bot.run(auth['token'])
