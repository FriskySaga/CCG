from discord.ext import commands
import discord
from json import load
from os import environ
from os.path import join
from random import choice

from common.common import ScheduleParser
from tasks.timed_reminder import TimedReminder

auth = environ.get('CCG_RUN_REMINDER_DISCORD_BOT_TOKEN')

serverIdsFile = open(join('config', 'server_ids.json'))
serverIds = load(serverIdsFile)
serverIdsFile.close()

scheduleParser = ScheduleParser()

bot = commands.Bot(command_prefix='!')

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
    "Ahoy, avast~!",
    "Fear not! I am here!",
    "Salutations, friend(s)!",
    "What does clickbait taste like?",
    "Like you've fallen through a trapdoor of sorrow.",
  ]
  await channel.send(choice(greetings))

  TimedReminder(bot, serverIds, scheduleParser).annoy.start()

async def alertNextBoss(ctx : commands.Context, bossName : str):
  """Answer the user request for the next time to conquer the target boss.

  :param ctx: The context of this command
  :param bossName: The name of the boss to attack
  """
  if bossName != 'Any':
    scheduledTime, rd = scheduleParser.findNextBossRun(bossName)
    await ctx.channel.send(
      f"{ctx.author.mention} Next {bossName} in {rd.hours} hours and {rd.minutes} "
      f"minutes from now at {scheduledTime.strftime('%I:%M %p')} {scheduleParser.timezoneInfo.timezoneString} Time.")
  else:
    nextRunInfo, rd = scheduleParser.findNextBossRunOfAnyType()
    await ctx.channel.send(
      f"{ctx.author.mention} Next {nextRunInfo[0].boss_name} in {rd.hours} hours and {rd.minutes} "
      f"minutes from now at {nextRunInfo[-1].strftime('%I:%M %p')} {scheduleParser.timezoneInfo.timezoneString} Time.")

@bot.command()
async def nextVP(ctx : commands.Context):
  await alertNextBoss(ctx, 'VP')

@bot.command()
async def nextCFO(ctx : commands.Context):
  await alertNextBoss(ctx, 'CFO')

@bot.command()
async def nextCJ(ctx : commands.Context):
  await alertNextBoss(ctx, 'CJ')

@bot.command()
async def nextCEO(ctx : commands.Context):
  await alertNextBoss(ctx, 'CEO')

@bot.command(aliases=['next', 'nextBoss', 'nextRun'])
async def nextBossRun(ctx : commands.Context):
  await alertNextBoss(ctx, 'Any')

@bot.command(aliases=['remindMe', 'remindme', 'allruns'])
async def allRuns(ctx : commands.Context):
  relativeDay = "today's early morning"

  # Find all runs for today that may be categorized as yesterday's runs according to MMO Central Forums
  allRemainingRuns = scheduleParser.findAllRuns(peekYesterday=True)

  # Look at today's runs
  if allRemainingRuns.empty:
    relativeDay = "today"
    allRemainingRuns = scheduleParser.findAllRuns()

  # If there are no more runs for today, look to tomorrow
  if allRemainingRuns.empty:
    relativeDay = "tomorrow"
    allRemainingRuns = scheduleParser.findAllRuns(forTomorrow=True)
  
  print(relativeDay)
  min_array_val = min(allRemainingRuns.index.values)
  max_array_val = max(allRemainingRuns.index.values)
  embed = discord.Embed(
            title="CCG Runs", description="Current CCG runs for " + relativeDay
        )
  for i in range(min_array_val, max_array_val+1):
    embed.add_field(
      name=allRemainingRuns["boss_name"][i],
      value=f"{allRemainingRuns['date_time'][i].strftime('%I:%M %p')} {scheduleParser.timezoneInfo.timezoneString} Time"
    )
  await ctx.channel.send(embed=embed)

@bot.command(aliases=['setTimezone', 'changetimezone', 'settimezone', 'settime', 'changeTime', 'setTime', 'changetime',
                      'set', 'mytime', 'myTime', 'timezone'])
async def changeTimezone(ctx : commands.Context, arg1 : str, arg2 = "", arg3 = ""):
  requestedTimezone = arg1 + arg2 + arg3
  if scheduleParser.setTimezone(requestedTimezone):
    await ctx.channel.send(f"{ctx.author.mention}, your timezone has been set to "
                           f"{scheduleParser.timezoneInfo.timezoneString} Time.")
  else:
    await ctx.channel.send(f"{ctx.author.mention}, '{requestedTimezone}' is an invalid time zone.")

@bot.command(aliases=['currenttimezone', 'checkTimezone', 'checktimezone', 'checkTime', 'checktime'])
async def currentTimezone(ctx : commands.Context):
  await ctx.channel.send(f"{ctx.author.mention}, the current timezone is "
                         f"{scheduleParser.timezoneInfo.timezoneString} Time.")

bot.run(auth)
