from datetime import datetime
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

    for scheduledTime in self.jsonData[currentDayOfWeek][bossName]:
      timeToCheck = scheduledTime.split(':')
      timeToCheck = now.replace(hour=int(timeToCheck[0]),
                                minute=int(timeToCheck[1]),
                                second=0,
                                microsecond=0)
      if now < timeToCheck:
        return timeToCheck, relativedelta(timeToCheck, now)

