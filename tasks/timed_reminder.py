from datetime import timedelta
from discord.ext import commands, tasks
from discord.ext.commands.bot import Bot

from common.common import ScheduleParser

class TimedReminder(commands.Cog):
  def __init__(self, bot : Bot, serverIds : dict, scheduleParser : ScheduleParser):
    self.bot = bot
    self.serverIds = serverIds
    self.scheduleParser = scheduleParser

    self.annoyed = False
    self.prevRunInfo = self.nextRunInfo = None

  @tasks.loop(seconds=60)
  async def annoy(self):
    """Ping peeps some number of minutes before a boss run.
    """
    ccgGuild = self.bot.get_guild(self.serverIds['Guild'])
    ccgRunRemindee = ccgGuild.get_role(self.serverIds['Role'])
    channel = self.bot.get_channel(self.serverIds['Channel'])

    # now = datetime.now(timezone('US/Pacific'))
    # currentDayOfWeek = now.strftime('%A')

    # csvFilePath = path.join(PATH_TO_SCHEDULES, 'ccg_schedule_ascending_times.csv')

    # with open(csvFilePath, 'r') as csvFile:
    #   csvReader = reader(csvFile)
    #   # Loop through ascending times
    #   for row in csvReader:
    #     if currentDayOfWeek == row[0]:
    #       timeToCheck = convertBasicTimeToDateTime(row[1], now)

    #       # Find the next run time
    #       if now < timeToCheck:
    #         self.nextRunInfo = row
    #         self.nextRunInfo[1] = timeToCheck
    #         break
    self.nextRunInfo, rd = self.scheduleParser.findNextBossRunOfAnyType()

    # If this is a new run, enable the bot to send a message
    if self.prevRunInfo != self.nextRunInfo:
      self.annoyed = False
      self.prevRunInfo = self.nextRunInfo

    minutesBeforeEventToRemind = 5
    nextRunTime = self.nextRunInfo[-1]

    # Send the message for this run if it hasn't yet been sent
    if not self.annoyed and rd.minutes <= minutesBeforeEventToRemind and rd.minutes >= 0:
      await channel.send(
        f"{ccgRunRemindee.mention} {self.nextRunInfo[0].boss_name} within the next "
        f"{minutesBeforeEventToRemind} minutes at "
        f"{nextRunTime.strftime('%I:%M %p')} Pacific Time")
      self.annoyed = True

