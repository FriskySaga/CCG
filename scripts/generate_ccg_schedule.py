import os
from pprint import pprint

PATH_TO_SCHEDULES = os.path.join('..', 'schedules')

"""Hard-coded indices for various timezones :)
Central - 1,2,3
Eastern - 4,5,6
Mountain - 7,8,9
Pacific - 10,11,12
Greenwich Mean - 13,14,15
British Summer - 16,17,18
"""
TIMEZONE_SUFFIX = 'british_summer'
TIME_INDEX = 16
AM_OR_PM_INDEX = 17
TIMEZONE_INDEX = 18

class ScheduledRunTime:
  def __init__(self, dayOfWeek : str, typeOfBoss : str, scheduledRunTime : str):
    self.dayOfWeek = dayOfWeek
    self.typeOfBoss = typeOfBoss
    self.scheduledRunTime = scheduledRunTime
  
  def __str__(self) -> str:
    return f'{self.dayOfWeek},{self.scheduledRunTime},{self.typeOfBoss}'
  
  def __repr__(self) -> str:
    return self.__str__()

def convertTo24Hour(timeToConvert : str, amOrPm : str, timezone : str) -> str:
  """Convert 12 hour time format to 24 hour time format.

  :param timeToConvert: 12 hour time format with a colon, e.g., '5:00'
  :param amOrPm: This string should say either 'AM' or 'PM'
  :param timezone: Capital two-letter abbreviation for the timezone

  :raises RuntimeError: When amOrPm is not a valid string
  :raises RuntimeError: When the converted time is invalid

  :return: The 24 hour time format
  """
  if amOrPm == 'AM':
    isAM = True
  elif amOrPm == 'PM':
    isAM = False
  else:
    raise RuntimeError(f'convertTo24Hour() - Failed to convert {timeToConvert} {amOrPm}')

  hoursAndMinutes = timeToConvert.split(':')
  hourToConvert = int(hoursAndMinutes[0])
  if hourToConvert == 12:
    convertedHour = 0 if isAM else 12
  else:
    convertedHour = hourToConvert if isAM else hourToConvert + 12
  
  if convertedHour < 0 or convertedHour >= 24:
    raise RuntimeError(f'convertTo24Hour() - Invalid converted hour {convertedHour} '
                       f'after converting {timeToConvert} {amOrPm}')
  
  convertedTime = str(convertedHour) + ':' + hoursAndMinutes[-1]
  return convertedTime

# Example format:
# [['Sunday',
#  ['VP', '5:00 AM', '12:00 PM'],
#  ['CFO', '5:45 AM', '12:45 PM']],
#  ['Monday', etc.]]
allScheduledRunTimes = []
runTimesByDayByBoss = []

rawCcgSchedulePath = os.path.join(PATH_TO_SCHEDULES, 'raw_ccg_schedule.txt')

with open(rawCcgSchedulePath, 'r') as inputFile:
  for line in inputFile:
    lineText = line.rstrip()
    if not lineText:
      continue
    if lineText.endswith('day'):
      runTimesByDayByBoss.append([lineText])
    elif 'Battle' not in lineText:
      contentsGrouping = lineText.split()
      # Create new boss list within the day
      if len(runTimesByDayByBoss[-1]) < 5:
        # Append boss name
        runTimesByDayByBoss[-1].append([contentsGrouping[0]])
        # Convert 12 hour time format to 24 hour time format
        scheduledRunTime = convertTo24Hour(contentsGrouping[TIME_INDEX],
                                           contentsGrouping[AM_OR_PM_INDEX],
                                           contentsGrouping[TIMEZONE_INDEX])
        runTimesByDayByBoss[-1][-1].append(scheduledRunTime)
      # Append to existing boss list within the day
      else:
        # Find the matching boss list
        for item in runTimesByDayByBoss[-1]:
          if contentsGrouping[0] in item:
            # Convert 12 hour time format to 24 hour time format
            scheduledRunTime = convertTo24Hour(contentsGrouping[TIME_INDEX],
                                               contentsGrouping[AM_OR_PM_INDEX],
                                               contentsGrouping[TIMEZONE_INDEX])
            item.append(scheduledRunTime)
      allScheduledRunTimes.append(
        ScheduledRunTime(dayOfWeek=runTimesByDayByBoss[-1][0],
                         typeOfBoss=contentsGrouping[0],
                         scheduledRunTime=scheduledRunTime
      ))

# pprint(runTimesByDayByBoss)
# pprint(allScheduledRunTimes)
import json

# Load template file
ccgScheduleTemplatePath = os.path.join(PATH_TO_SCHEDULES, 'template_ccg_schedule.json')

templateFile = open(ccgScheduleTemplatePath, 'r')
jsonData = json.load(templateFile)
templateFile.close()

allRunTimes = []

# Fill out the boss times for the JSON file.
# Also sort the times for the CSV file.
for day in runTimesByDayByBoss:
  dayKey = None
  allRunTimes.append([])
  for item in day:
    if isinstance(item, str):
      dayKey = item
    elif isinstance(item, list):
      bossKey = item[0]
      scheduledRunTimes = item[1:]
      jsonData[dayKey][bossKey] = scheduledRunTimes
      allRunTimes[-1].extend(scheduledRunTimes)
    else:
      raise RuntimeError(f'Built my list wrong: {item}')

# Create the JSON CCG Schedule file
jsonOutputFilePath = os.path.join(PATH_TO_SCHEDULES, f'ccg_schedule_{TIMEZONE_SUFFIX}.json')
with open(jsonOutputFilePath, 'w', encoding='utf-8') as outputFile:
  json.dump(jsonData, outputFile, ensure_ascii=False, indent=2)

# Build a CSV file sorted by ascending time
csvOutputFilePath = os.path.join(PATH_TO_SCHEDULES, f'ccg_schedule_ascending_times_{TIMEZONE_SUFFIX}.csv')
with open(csvOutputFilePath, 'w') as csvOutputFile:
  csvOutputFile.write('day_of_week,scheduled_run_time,boss_name\n')
  for line in allScheduledRunTimes:
    csvOutputFile.write(line.__str__() + '\n')
