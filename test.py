from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import os
import pandas as pd
from pprint import pprint
from pytz import timezone

def convertBasicTimeToDateTime(basicTime : str, now : datetime) -> datetime:
  """Convert a basic time format, (e.g., 13:00), to today's datetime format.

  :param basicTime: Hours and minutes separated by a colon
  :param now: Current time

  :return: Today's datetime format with the basicTime
  """
  timeToCheck = basicTime.split(':')
  return now.replace(hour=int(timeToCheck[0]),
                     minute=int(timeToCheck[1]),
                     second=0,
                     microsecond=0)

def testCSV():
  now = datetime.now(timezone('US/Pacific'))
  currentDayOfWeek = now.strftime('%A')

  nextRunInfo = None

  csvScheduleFilePath = os.path.join('schedules', 'ccg_schedule_ascending_times.csv')
  csvDf = pd.read_csv(csvScheduleFilePath)
  dfScheduledRunsForToday = csvDf.loc[csvDf['day_of_week'] == currentDayOfWeek]
  for row in dfScheduledRunsForToday.itertuples():
    timeToCheck = convertBasicTimeToDateTime(row.scheduled_run_time, now)
    if now < timeToCheck:
      nextRunInfo = (row, timeToCheck)
      break

  nextRunTime = nextRunInfo[-1]

  if (now >= nextRunTime - timedelta(minutes=180)
      and now <= nextRunTime):
    print(f"{nextRunInfo[0].boss_name} within the next 180 minutes at {nextRunTime.strftime('%I:%M %p')} PT")

def testJSON():
  jsonScheduleFilePath = os.path.join('schedules', 'ccg_schedule.json')
  jsonScheduleFile = open(jsonScheduleFilePath, 'r')
  jsonData = json.load(jsonScheduleFile)
  jsonScheduleFile.close()

  now = datetime.now(timezone('US/Pacific'))
  currentDayOfWeek = now.strftime('%A')

  bossName = 'CFO'

  for scheduledTime in jsonData[currentDayOfWeek][bossName]:
    timeToCheck = convertBasicTimeToDateTime(scheduledTime, now)
    if now < timeToCheck:
      print(scheduledTime)
      rd = relativedelta(timeToCheck, now)
      print(f"{bossName} in {rd.hours} hours and {rd.minutes} minutes from now")
      break
  
  nowIsTomorrow = now + timedelta(days=1)
  tomorrowDayOfWeek = nowIsTomorrow.strftime('%A')
  nextBasicRunTime = jsonData[tomorrowDayOfWeek][bossName][0]
  nextDtRunTime = convertBasicTimeToDateTime(nextBasicRunTime, nowIsTomorrow)
  print(now, nextDtRunTime)
  rd = relativedelta(nextDtRunTime, now)
  print(f"{bossName} in {rd.hours} hours and {rd.minutes} minutes from now")

if __name__ == '__main__':
  testCSV()
  # testJSON()
