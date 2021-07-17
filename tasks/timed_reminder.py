from csv import reader
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord.ext.commands.bot import Bot
from os import path
from pytz import timezone

from common.common import convertBasicTimeToDateTime

PATH_TO_SCHEDULES = path.join('schedules')

class TimedReminder(commands.Cog):
  def __init__(self, bot : Bot, serverIds : dict):
    self.bot = bot
    self.serverIds = serverIds
    self.annoyed = False
    self.prevRunInfo = self.nextRunInfo = None

  @tasks.loop(seconds=60)
  async def annoy(self):
    """Ping peeps some number of minutes before a boss run.
    """
    ccgGuild = self.bot.get_guild(self.serverIds['Guild'])
    ccgRunRemindee = ccgGuild.get_role(self.serverIds['Role'])
    channel = self.bot.get_channel(self.serverIds['Channel'])

    now = datetime.now(timezone('US/Pacific'))
    currentDayOfWeek = now.strftime('%A')

    csvFilePath = path.join(PATH_TO_SCHEDULES, 'ccg_schedule_ascending_times.csv')

    with open(csvFilePath, 'r') as csvFile:
      csvReader = reader(csvFile)
      # Loop through ascending times
      for row in csvReader:
        if currentDayOfWeek == row[0]:
          timeToCheck = convertBasicTimeToDateTime(row[1], now)

          # Find the next run time
          if now < timeToCheck:
            self.nextRunInfo = row
            self.nextRunInfo[1] = timeToCheck
            break

    # If this is a new run, enable the bot to send a message
    if self.prevRunInfo != self.nextRunInfo:
      self.annoyed = False
      self.prevRunInfo = self.nextRunInfo

    minutesBeforeEventToRemind = 5
    nextRunTime = self.nextRunInfo[1]

    # Send the message for this run if it hasn't yet been sent
    if (not self.annoyed
        and now >= nextRunTime - timedelta(minutes=minutesBeforeEventToRemind)
        and now <= nextRunTime):
      await channel.send(
        f"{ccgRunRemindee.mention} {self.nextRunInfo[2]} within the next "
        f"{minutesBeforeEventToRemind} minutes at "
        f"{nextRunTime.strftime('%I:%M %p')} Pacific Time")
      self.annoyed = True

