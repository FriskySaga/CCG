from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from json import load
from os.path import join
import pandas as pd
import pytz

class TimezoneInfo:
  def __init__(self, timezoneObject : pytz.timezone, timezoneFileNameString : str):
    """Hold timezone data.

    :param timezoneObject: The pytz timezone object
    :param timezoneFileString: The timezone string used for the CSV/JSON file names
    """
    self.timezoneObject = timezoneObject
    self.timezoneFileNameString = timezoneFileNameString
    self.timezoneString = self.cleanTimezoneFileNameString()
  
  def cleanTimezoneFileNameString(self) -> str:
    """Make the timezone file name string human-friendly.

    :return: Creature-friendly string
    """
    if self.timezoneFileNameString == 'greenwich_mean':
      return 'Greenwich Mean'
    elif self.timezoneFileNameString == 'british_summer':
      return 'British Summer'
    else:
      return self.timezoneFileNameString.capitalize()

def readCsvSchedule(folderPath : str, timezoneInfo : TimezoneInfo) -> pd.DataFrame:
  """Read the CSV CCG Schedule.
  
  :param folderPath: Path to the CSV CCG Schedule
  :param timezoneInfo: The timezone info object to indicate which file to read from
  
  :return: CSV file loaded into memory as a DataFrame object
  """
  csvScheduleFilePath = join(folderPath, f'ccg_schedule_ascending_times_{timezoneInfo.timezoneFileNameString}.csv')
  return pd.read_csv(csvScheduleFilePath)

def readJsonSchedule(folderPath : str, timezoneInfo : str) -> dict:
  """Read the JSON CCG Schedule.

  :param folderPath: Path to the JSON CCG Schedule
  :param timezoneInfo: The timezone info object to indicate which file to read from

  :return: JSON Dict for the JSON CCG Schedule
  """
  jsonScheduleFilePath = join(folderPath, f'ccg_schedule_{timezoneInfo.timezoneFileNameString}.json')
  jsonScheduleFile = open(jsonScheduleFilePath, 'r')
  jsonData = load(jsonScheduleFile)
  jsonScheduleFile.close()
  return jsonData

def convertBasicTimeToDateTime(basicTime : str, dateToUpdate : datetime) -> datetime:
  """Convert a basic time format, (e.g., 13:00), to today's datetime format.

  :param basicTime: Hours and minutes separated by a colon
  :param dateToUpdate: The date time object to update

  :return: Today's datetime format with the basicTime
  """
  timeToCheck = basicTime.split(':')
  return dateToUpdate.replace(hour=int(timeToCheck[0]),
                              minute=int(timeToCheck[1]),
                              second=0,
                              microsecond=0)

class ScheduleParser:
  def __init__(self):
    self.pathToSchedules = join('schedules')
    self.timezoneInfo = TimezoneInfo(pytz.timezone('US/Pacific'), 'pacific')
    self.readSchedules()

  def readSchedules(self):
    """Read the schedules for the given timezone."""
    self.csvDf = readCsvSchedule(self.pathToSchedules, self.timezoneInfo)
    self.jsonData = readJsonSchedule(self.pathToSchedules, self.timezoneInfo)

  def setTimezone(self, newTimezone : str) -> bool:
    """Set the timezone.

    :param newTimezone: Indicate the new timezone to use
    
    :return: Whether the requested timezone is supported
    """
    newTimezone = newTimezone.lower()
    if any(x in newTimezone for x in ['ct', 'cst', 'central']):
      self.timezoneInfo = TimezoneInfo(pytz.timezone('US/Central'), 'central')
    elif any(x in newTimezone for x in ['et', 'est', 'eastern']):
      self.timezoneInfo = TimezoneInfo(pytz.timezone('US/Eastern'), 'eastern')
    elif any(x in newTimezone for x in ['mt', 'mst', 'mountain']):
      self.timezoneInfo = TimezoneInfo(pytz.timezone('US/Mountain'), 'mountain')
    elif any(x in newTimezone for x in ['pt', 'pst', 'pacific']):
      self.timezoneInfo = TimezoneInfo(pytz.timezone('US/Pacific'), 'pacific')
    elif any(x in newTimezone for x in ['gmt', 'greenwich', 'mean']):
      self.timezoneInfo = TimezoneInfo(pytz.timezone('Greenwich'), 'greenwich_mean')
    elif any(x in newTimezone for x in ['bst', 'british', 'summer']):
      self.timezoneInfo = TimezoneInfo(pytz.timezone('Europe/London'), 'british_summer')
    else:
      return False
    
    # Load in the new timezone schedule data
    self.readSchedules()
    return True

  def findAllRuns(self, peekYesterday = False, forTomorrow = False) -> pd.DataFrame:
    """Find all remaining runs for today or tomorrow if there are no more runs left for today.

    :param peekYesterday: Whether to peek the runs that are assigned to yesterday per MCF schedule
    :param forTomorrow: Whether to find the runs for today or tomorrow

    :note: Both parameters should never be True at the same time

    :return: Info about all requested runs
    """
    now = datetime.now(self.timezoneInfo.timezoneObject)

    # Subtract a day if we are peeking yesterday, otherwise add a day if we are peeking tomorrow
    targetDay = now - timedelta(days=int(peekYesterday))
    targetDay = targetDay + timedelta(days=int(forTomorrow))

    dayOfWeek = targetDay.strftime('%A')

    remainingRuns = self.csvDf.loc[self.csvDf['day_of_week'] == dayOfWeek]

    dateTimeList = []
    for scheduledRunTime in remainingRuns['scheduled_run_time']:
      newTime = convertBasicTimeToDateTime(scheduledRunTime, targetDay)

      # If the new time is smaller than the previous time, then because we know
      # the CSV is sorted in ascending time, then we can make the assumption
      # that this new time is actually the next day (unlike what MCF suggests)
      if dateTimeList and newTime < dateTimeList[-1]:
        newTime = newTime + timedelta(days=1)

      dateTimeList.append(newTime)

    dateTimeSeries = pd.Series(dateTimeList)

    remainingRuns.reset_index(drop=True, inplace=True)

    remainingRuns = remainingRuns.assign(date_time=dateTimeSeries)
    remainingRuns = remainingRuns.loc[remainingRuns['date_time'] >= now]

    return remainingRuns

  def findNextBossRunOfAnyType(self) -> tuple[tuple[pd.DataFrame, datetime], relativedelta]:
    """Find the next boss run from the current time irregardless of boss type.

    :return: DataFrame row about the next boss run
    :return: The DateTime associated with the next boss run
    :return: The time delta from now until the next boss run
    """
    now = datetime.now(self.timezoneInfo.timezoneObject)
    prevParsedTimes = []

    # Loop through scheduled runs for yesterday (because of MCF schedule structure)
    nowWasYesterday = now - timedelta(days=1)
    yesterdayDayOfWeek = nowWasYesterday.strftime('%A')
    for row in self.csvDf.loc[self.csvDf['day_of_week'] == yesterdayDayOfWeek].itertuples():
      timeToCheck = convertBasicTimeToDateTime(row.scheduled_run_time, nowWasYesterday)

      # If the new time is smaller than the previous time, then because we know
      # the CSV is sorted in ascending time, then we can make the assumption
      # that this new time is actually the next day (unlike what MCF suggests)
      if prevParsedTimes and timeToCheck < prevParsedTimes[-1]:
        timeToCheck = timeToCheck + timedelta(days=1)

      prevParsedTimes.append(timeToCheck)

      # Find the next run time
      if now <= timeToCheck:
        nextRunInfo = (row, timeToCheck) 
        return nextRunInfo, relativedelta(nextRunInfo[-1], now)

    # Loop through scheduled runs for today (sorted by ascending time)
    prevParsedTimes = []
    currentDayOfWeek = now.strftime('%A')
    for row in self.csvDf.loc[self.csvDf['day_of_week'] == currentDayOfWeek].itertuples():
      timeToCheck = convertBasicTimeToDateTime(row.scheduled_run_time, now)

      # If the new time is smaller than the previous time, then because we know
      # the CSV is sorted in ascending time, then we can make the assumption
      # that this new time is actually the next day (unlike what MCF suggests)
      if prevParsedTimes and timeToCheck < prevParsedTimes[-1]:
        timeToCheck = timeToCheck + timedelta(days=1)
      
      prevParsedTimes.append(timeToCheck)

      # Find the next run time
      if now <= timeToCheck:
        nextRunInfo = (row, timeToCheck) 
        return nextRunInfo, relativedelta(nextRunInfo[-1], now)
    
    # If there are no more runs for today, then move onto the next day :P
    nowIsTomorrow = now + timedelta(days=1)
    tomorrowDayOfWeek = nowIsTomorrow.strftime('%A')
    for row in self.csvDf.loc[self.csvDf['day_of_week'] == tomorrowDayOfWeek].itertuples():
      timeToCheck = convertBasicTimeToDateTime(row.scheduled_run_time, nowIsTomorrow)

      # Find the next run time
      if now <= timeToCheck:
        nextRunInfo = (row, timeToCheck) 
        return nextRunInfo, relativedelta(nextRunInfo[-1], now)

  def findNextBossRun(self, bossName : str) -> tuple[dict, relativedelta]:
    """Given a boss type, find the next run from the current time.

    :param bossName: The next boss run to find.
                     Acceptable values are: 'VP', 'CFO', 'CJ', 'CEO'

    :return: The next boss time
    :return: Relative delta info until the next boss
    """
    now = datetime.now(self.timezoneInfo.timezoneObject)
    prevParsedTimes = []

    # Loop through scheduled runs for yesterday (because of MCF schedule structure)
    nowWasYesterday = now - timedelta(days=1)
    yesterdayDayOfWeek = nowWasYesterday.strftime('%A')
    for scheduledTime in self.jsonData[yesterdayDayOfWeek][bossName]:
      timeToCheck = convertBasicTimeToDateTime(scheduledTime, nowWasYesterday)

      # If the new time is smaller than the previous time, then because we know
      # the JSON is sorted in ascending time, then we can make the assumption
      # that this new time is actually the next day (unlike what MCF suggests)
      if prevParsedTimes and timeToCheck < prevParsedTimes[-1]:
        timeToCheck = timeToCheck + timedelta(days=1)

      prevParsedTimes.append(timeToCheck)

      # Find the next run time
      if now <= timeToCheck:
        return timeToCheck, relativedelta(timeToCheck, now)

    # Look for the next boss run of this type for today
    prevParsedTimes = []
    currentDayOfWeek = now.strftime('%A')
    for scheduledTime in self.jsonData[currentDayOfWeek][bossName]:
      timeToCheck = convertBasicTimeToDateTime(scheduledTime, now)

      # If the new time is smaller than the previous time, then because we know
      # the JSON is sorted in ascending time, then we can make the assumption
      # that this new time is actually the next day (unlike what MCF suggests)
      if prevParsedTimes and timeToCheck < prevParsedTimes[-1]:
        timeToCheck = timeToCheck + timedelta(days=1)

      prevParsedTimes.append(timeToCheck)

      # Find the next run time
      if now <= timeToCheck:
        return timeToCheck, relativedelta(timeToCheck, now)
    
    # Move onto the next day if there are no more runs for the day
    nowIsTomorrow = now + timedelta(days=1)
    tomorrowDayOfWeek = nowIsTomorrow.strftime('%A')
    nextBasicRunTime = self.jsonData[tomorrowDayOfWeek][bossName][0]
    nextDtRunTime = convertBasicTimeToDateTime(nextBasicRunTime, nowIsTomorrow)
    return nextDtRunTime, relativedelta(nextDtRunTime, now)
    
