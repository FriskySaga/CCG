import csv, json
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from pprint import pprint
from pytz import timezone

authFile = open('auth.json')
auth = json.load(authFile)
authFile.close()

annoyed = False
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  generalChannel = bot.get_channel(863494908668542979)
  await generalChannel.send("I have been awakened from my slumber...")
  annoy.start()

@tasks.loop(seconds=60)
async def annoy():
  global annoyed
  ccgGuild = bot.get_guild(863494908668542976)
  ccgRunRemindee = ccgGuild.get_role(863839003623030784)
  generalChannel = bot.get_channel(863494908668542979)

  now = datetime.now(timezone('US/Pacific'))
  currentDayOfWeek = now.strftime('%A')

  nextRunInfo = None

  with open('ccg-schedule-ascending-times.csv', 'r') as csvFile:
    csvReader = csv.reader(csvFile)
    # Loop through ascending times
    for row in csvReader:
      if currentDayOfWeek == row[0]:
        timeToCheck = row[1].split(':')
        timeToCheck = now.replace(hour=int(timeToCheck[0]),
                                  minute=int(timeToCheck[1]),
                                  second=0,
                                  microsecond=0)
        # Find the next run time
        if now < timeToCheck:
          nextRunInfo = row
          nextRunInfo[1] = timeToCheck
          break

  nextRunTime = nextRunInfo[1]

  if (not annoyed
      and now >= nextRunTime - timedelta(minutes=45)
      and now <= nextRunTime):
    await generalChannel.send(
      f"{ccgRunRemindee.mention} within the next 180 minutes at {nextRunTime.strftime('%I:%M %p')} PT")
    annoyed = True

  # # Current time
  # now = datetime.datetime.now()

  # # Target time
  # targetTime = now.replace(hour=15, minute=45)

  # # Check that we are within 5 minutes until target time
  # if now <= targetTime and now >= targetTime - datetime.timedelta(minutes=5) and not annoyed:
  #   await generalChannel.send(f'{ccgRunRemindee.mention} CFO within the next 5 minutes at 3:45 PM today')
  #   annoyed = True

bot.run(auth['token'])
