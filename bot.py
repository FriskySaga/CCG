# External imports
from discord.ext import commands
from json import load
from os import environ
from os.path import join
from random import choice

# Project imports
from cogs.notify_daily_runs import NotifyDailyRuns
from common.common import ScheduleParser
from tasks.timed_reminder import TimedReminder

auth = environ.get('CCG_RUN_REMINDER_DISCORD_BOT_TOKEN')

serverIdsFile = open(join('config', 'server_ids.json'))
serverIds = load(serverIdsFile)
serverIdsFile.close()

scheduleParser = ScheduleParser()

bot = commands.Bot(command_prefix='!', case_insensitive=True)

@bot.event
async def on_ready():
  """Start the bot."""
  print(f"{bot.user} has connected to Discord!")
  channel = bot.get_channel(serverIds['Channel'])

  greetings = [
    "Sleep is for the weak...",
    "I SHAN'T GO TO SLEEP",
    "I have been awakened from my slumber...",
    "What's the craic?",
    "How hops it?",
    "Ahoy, avast!",
    "Fear not! I am here!",
    "Salutations, friend(s)!",
    "What does clickbait taste like?",
    "Like you've fallen through a trapdoor of sorrow.",
  ]
  await channel.send(choice(greetings))

  TimedReminder(bot, serverIds, scheduleParser).annoy.start()


bot.add_cog(NotifyDailyRuns(bot, scheduleParser))
bot.run(auth)
