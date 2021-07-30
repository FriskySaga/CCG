# External imports
from discord import Embed
from discord.ext import commands

# Project imports
from common.common import ScheduleParser

class NotifyDailyRuns(commands.Cog):
  def __init__(self, bot : commands.Bot, scheduleParser : ScheduleParser):
    self.bot = bot
    self.scheduleParser = scheduleParser

  @commands.command(aliases=['remindMe'])
  async def allRuns(self, ctx : commands.Context):
    relativeDay = "today's early morning"

    # Find all runs for today that may be categorized as yesterday's runs according to MMO Central Forums
    allRemainingRuns = self.scheduleParser.findAllRuns(peekYesterday=True)

    # Look at today's runs
    if allRemainingRuns.empty:
      relativeDay = "today"
      allRemainingRuns = self.scheduleParser.findAllRuns()

    # If there are no more runs for today, look to tomorrow
    if allRemainingRuns.empty:
      relativeDay = "tomorrow"
      allRemainingRuns = self.scheduleParser.findAllRuns(forTomorrow=True)
    
    min_array_val = min(allRemainingRuns.index.values)
    max_array_val = max(allRemainingRuns.index.values)
    embed = Embed(title="CCG Runs", description="Current CCG runs for " + relativeDay)
    for i in range(min_array_val, max_array_val+1):
      embed.add_field(
        name=allRemainingRuns["boss_name"][i],
        value=f"<t:{allRemainingRuns['date_time'][i]}:F>"
      )
    await ctx.channel.send(embed=embed)

  @commands.command(aliases=['next', 'nextBoss', 'nextRun'])
  async def nextBossRun(self, ctx : commands.Context):
    await self.alertNextBoss(ctx, 'Any')

  @commands.command()
  async def nextVP(self, ctx : commands.Context):
    await self.alertNextBoss(ctx, 'VP')

  @commands.command()
  async def nextCFO(self, ctx : commands.Context):
    await self.alertNextBoss(ctx, 'CFO')

  @commands.command()
  async def nextCJ(self, ctx : commands.Context):
    await self.alertNextBoss(ctx, 'CJ')

  @commands.command()
  async def nextCEO(self, ctx : commands.Context):
    await self.alertNextBoss(ctx, 'CEO')
  
  async def alertNextBoss(self, ctx : commands.Context, bossName : str):
    """Answer the user request for the next time to conquer the target boss.

    :param ctx: The context of this command
    :param bossName: The name of the boss to attack
    """
    if bossName != 'Any':
      timestamp, rd = self.scheduleParser.findNextBossRun(bossName)
      await ctx.channel.send(
        f"{ctx.author.mention} Next {bossName} in {rd.hours} hours and {rd.minutes} minutes "
        f"from now at <t:{timestamp}:t>"
      )
    else:
      nextRunInfo, rd = self.scheduleParser.findNextBossRunOfAnyType()
      await ctx.channel.send(
        f"{ctx.author.mention} Next {nextRunInfo[0].boss_name} in {rd.hours} hours and {rd.minutes} minutes "
        f"from now at <t:{nextRunInfo[-1]}:t>"
      )