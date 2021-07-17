from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from json import load
from os.path import join
import pandas as pd
from pytz import timezone

def readCsvSchedule(folderPath : str) -> pd.DataFrame:
  """Read the CSV CCG Schedule.
  
  :param folderPath: Path to the CSV CCG Schedule
  
  :return: CSV file loaded into memory as a DataFrame object
  """
  csvScheduleFilePath = join(folderPath, 'ccg_schedule_ascending_times.csv')
  return pd.read_csv(csvScheduleFilePath)

def readJsonSchedule(folderPath : str) -> dict:
  """Read the JSON CCG Schedule.

  :param folderPath: Path to the JSON CCG Schedule

  :return: JSON Dict for the JSON CCG Schedule
  """
  jsonScheduleFilePath = join(folderPath, 'ccg_schedule.json')
  jsonScheduleFile = open(jsonScheduleFilePath, 'r')
  jsonData = load(jsonScheduleFile)
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
    self.pathToSchedules = join('schedules')
    self.csvDf = readCsvSchedule(self.pathToSchedules)
    self.jsonData = readJsonSchedule(self.pathToSchedules)

  def findAllRuns(self) -> pd.DataFrame:
    """Find all runs for today.
    """
    now = datetime.now(timezone('US/Pacific'))
    currentDayOfWeek = now.strftime('%A')

    todaysRuns = self.csvDf.loc[self.csvDf['day_of_week'] == currentDayOfWeek]

    dateTimeList = []
    for scheduledRunTime in todaysRuns['scheduled_run_time']:
      dateTimeList.append(convertBasicTimeToDateTime(scheduledRunTime, now))

    dateTimeSeries = pd.Series(dateTimeList)

    todaysRuns.reset_index(drop=True, inplace=True)

    todaysRuns = todaysRuns.assign(date_time=dateTimeSeries)
    print("date is:", todaysRuns)
    return todaysRuns.loc[todaysRuns['date_time'] >= now]

  def findNextBossRunOfAnyType(self) -> tuple[tuple[pd.DataFrame, datetime], relativedelta]:
    """Find the next boss run from the current time irregardless of boss type.

    :return: DataFrame row about the next boss run
    :return: The DateTime associated with the next boss run
    :return: The time delta from now until the next boss run
    """
    now = datetime.now(timezone('US/Pacific'))
    currentDayOfWeek = now.strftime('%A')

    # Loop through scheduled runs for today (sorted by ascending time)
    for row in self.csvDf.loc[self.csvDf['day_of_week'] == currentDayOfWeek].itertuples():
      timeToCheck = convertBasicTimeToDateTime(row.scheduled_run_time, now)

      # Find the next run time
      if now < timeToCheck:
        nextRunInfo = (row, timeToCheck)
        break
  
    return nextRunInfo, relativedelta(nextRunInfo[-1], now)

  def findNextBossRun(self, bossName : str) -> tuple[dict, relativedelta]:
    """Given a boss type, find the next run from the current time.

    :param bossName: The next boss run to find.
                     Acceptable values are: 'VP', 'CFO', 'CJ', 'CEO'

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
    
