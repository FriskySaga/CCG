from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
from os import path
from pytz import timezone

def readJsonSchedule(folderPath : str) -> dict:
  """Read the JSON CCG Schedule.

  :param folderPath: Path to the JSON CCG Schedule

  :return: JSON Dict for the JSON CCG Schedule
  """
  jsonScheduleFilePath = path.join(folderPath, 'ccg_schedule.json')
  jsonScheduleFile = open(jsonScheduleFilePath, 'r')
  jsonData = json.load(jsonScheduleFile)
  jsonScheduleFile.close()
  return jsonData

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

class ScheduleParser:
  def __init__(self):
    self.pathToSchedules = path.join('schedules')
    self.jsonData = readJsonSchedule(self.pathToSchedules)

  def findNextBossRun(self, bossName : str) -> tuple[dict, relativedelta]:
    """Find the next boss run from the current time.

    :param bossName: VP, CFO, CJ, CEO

    :return: The next boss time
    :return: Relative delta info until the next boss
    """
    now = datetime.now(timezone('US/Pacific'))
    currentDayOfWeek = now.strftime('%A')

    # Look for the next boss run of this type for today
    for scheduledTime in self.jsonData[currentDayOfWeek][bossName]:
      timeToCheck = convertBasicTimeToDateTime(scheduledTime, now)
      if now <= timeToCheck:
        return timeToCheck, relativedelta(timeToCheck, now)
    
    # Move onto the next day if there are no more runs for the day
    nowIsTomorrow = now + timedelta(days=1)
    tomorrowDayOfWeek = nowIsTomorrow.strftime('%A')
    nextBasicRunTime = self.jsonData[tomorrowDayOfWeek][bossName][0]
    nextDtRunTime = convertBasicTimeToDateTime(nextBasicRunTime, nowIsTomorrow)
    return nextDtRunTime, relativedelta(nextDtRunTime, now)
    
