from discord.ext import commands
import json
from os import path

from common.common import ScheduleParser
from tasks.timed_reminder import TimedReminder

authFile = open(path.join('config', 'auth.json'))
auth = json.load(authFile)
authFile.close()

serverIdsFile = open(path.join('config', 'server_ids.json'))
serverIds = json.load(serverIdsFile)
serverIdsFile.close()

scheduleParser = ScheduleParser()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  channel = bot.get_channel(serverIds['Channel'])
  await channel.send("I have been awakened from my slumber...")
  TimedReminder(bot, serverIds).annoy.start()

@bot.command(name='nextVP')
async def nextVP(ctx : commands.Context):
  scheduledTime, rd = scheduleParser.findNextBossRun('VP')
  await ctx.channel.send(f"Next VP in {rd.hours} hours and {rd.minutes} "
                         f"minutes from now at {scheduledTime.strftime('%I:%M %p')} Pacific Time")

bot.run(auth['token'])
