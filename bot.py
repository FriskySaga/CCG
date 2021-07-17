from discord.ext import commands
import json
from os import path
from random import choice

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

  TimedReminder(bot, serverIds).annoy.start()

async def alertNextBoss(ctx : commands.Context, bossName : str):
  """Answer the user request for the next time to conquer the target boss.

  :param ctx: The context of this command
  :param bossName: The name of the boss to attack
  """
  scheduledTime, rd = scheduleParser.findNextBossRun(bossName)
  await ctx.channel.send(
    f"{ctx.author.mention} Next {bossName} in {rd.hours} hours and {rd.minutes} "
    f"minutes from now at {scheduledTime.strftime('%I:%M %p')} Pacific Time")

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

@bot.command(aliases=['killYourself', 'gokys', 'gokyspls', 'godie', 'goToBed', 'godieinahole', 'vanishThineExistence'])
async def kys(ctx : commands.Context):
  endings = [
    "nooo rusttyyyyy",
    "Committing sudoku",
    "actually dying",
    "seppuku i shall",
    "why are you doing this to me",
    "Goodnight! <3",
    "i'm actually kinda tired from all this programming",
  ]
  await ctx.channel.send(choice(endings))
  await bot.close()

bot.run(auth['token'])
