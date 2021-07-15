from pprint import pprint

class ScheduledRunTime:
  def __init__(self, dayOfWeek : str, typeOfBoss : str, scheduledRunTime : str):
    self.dayOfWeek = dayOfWeek
    self.typeOfBoss = typeOfBoss
    self.scheduledRunTime = scheduledRunTime
  
  def __str__(self):
    return f'{self.dayOfWeek}, {self.scheduledRunTime}, {self.typeOfBoss}'
  
  def __repr__(self):
    return self.__str__()

def convertTo24Hour(timeToConvert : str, amOrPm : str):
  """Convert 12 hour time format to 24 hour time format.

  :param timeToConvert: 12 hour time format with a colon, e.g., '5:00'
  :param amOrPm: This string should say either 'AM' or 'PM'

  :raises RuntimeError: When amOrPm is not a valid string
  :raises RuntimeError: When the converted time is invalid
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
with open('ccg-schedule-raw.txt', 'r') as inputFile:
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
        scheduledRunTime = convertTo24Hour(contentsGrouping[10], contentsGrouping[11])
        runTimesByDayByBoss[-1][-1].append(scheduledRunTime)
      # Append to existing boss list within the day
      else:
        # Find the matching boss list
        for item in runTimesByDayByBoss[-1]:
          if contentsGrouping[0] in item:
            # Convert 12 hour time format to 24 hour time format
            scheduledRunTime = convertTo24Hour(contentsGrouping[10], contentsGrouping[11])
            item.append(scheduledRunTime)
      allScheduledRunTimes.append(
        ScheduledRunTime(dayOfWeek=runTimesByDayByBoss[-1][0],
                         typeOfBoss=contentsGrouping[0],
                         scheduledRunTime=scheduledRunTime
      ))

# pprint(runTimesByDayByBoss)
pprint(allScheduledRunTimes)
import json

# Load template file
templateFile = open('ccg-schedule-template.json', 'r')
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
import os
jsonOutputFilePath = os.path.join('..', 'ccg-schedule.json')
with open(jsonOutputFilePath, 'w', encoding='utf-8') as outputFile:
  json.dump(jsonData, outputFile, ensure_ascii=False, indent=2)

# Build a CSV file sorted by ascending time
csvOutputFilePath = os.path.join('..', 'ccg-schedule-ascending-times.csv')
with open(csvOutputFilePath, 'w') as csvOutputFile:
  for line in allScheduledRunTimes:
    csvOutputFile.write(line.__str__() + '\n')
