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

