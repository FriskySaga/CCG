from discord.ext import commands
from json import load
from os.path import join
from random import choice

from common.common import ScheduleParser
from tasks.timed_reminder import TimedReminder

authFile = open(join('config', 'auth.json'))
auth = load(authFile)
authFile.close()

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
    "I SHALL NOT GO TO SLEEP",
    "I have been awakened from my slumber...",
    "Are you tired? You've been running around my mind all day.",
    "What's the craic?",
    "How hops it?",
    "Ahoy, avast~!",
    "Luffy's mom is Croco-boy",
    "Fear not! I am here!",
    "DETROIT SMAAAAASH",
    "Salutations, friend(s)!",
    "Ohayogozaimasu, o genki desu ka?",
    "Wanna know edgy?",
    "What does clickbait taste like?",
    "Like you've fallen through a trapdoor of sorrow.",
  ]
  await channel.send(choice(greetings))

  TimedReminder(bot, serverIds, scheduleParser).annoy.start()

disconnectAliases = ['kys', 'killYourself', 'gokys', 'gokyspls', 'godie', 'goToBed', 'godieinahole',
                     'vanishThineExistence', 'quit', 'die', 'begone', 'disconnect']

@bot.command(aliases=disconnectAliases)
async def disconnect(ctx : commands.Context):
  """Disconnect the bot."""
  endings = [
    "nooo rusttyyyyy",
    "Committing sudoku",
    "actually dying",
    "seppuku i shall",
    "why are you doing this to me",
    "Goodnight! <3",
  ]
  print(f"{bot.user} is disconnecting.")
  await ctx.channel.send(f"{ctx.author.mention} {choice(endings)}")
  await bot.close()

@bot.command(aliases=['howkill', 'howtokill', 'howKill'])
async def howToKill(ctx : commands.Context):
  await ctx.channel.send(f"{ctx.author.mention} {disconnectAliases}")

async def alertNextBoss(ctx : commands.Context, bossName : str):
  """Answer the user request for the next time to conquer the target boss.

  :param ctx: The context of this command
  :param bossName: The name of the boss to attack
  """
  if bossName != 'Any':
    scheduledTime, rd = scheduleParser.findNextBossRun(bossName)
    await ctx.channel.send(
      f"{ctx.author.mention} Next {bossName} in {rd.hours} hours and {rd.minutes} "
      f"minutes from now at {scheduledTime.strftime('%I:%M %p')} Pacific Time")
  else:
    nextRunInfo, rd = scheduleParser.findNextBossRunOfAnyType()
    await ctx.channel.send(
      f"{ctx.author.mention} Next {nextRunInfo[0].boss_name} in {rd.hours} hours and {rd.minutes} "
      f"minutes from now at {nextRunInfo[-1].strftime('%I:%M %p')} Pacific Time")

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

@bot.command(aliases=['next', 'nextBoss', 'remindMe', 'remindme'])
async def nextBossRun(ctx : commands.Context):
  await alertNextBoss(ctx, 'Any')

bot.run(auth['token'])
