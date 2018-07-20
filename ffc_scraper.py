#Forex Factory Scraper
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import date, timedelta
import re
import time
import csv
import calendar
import sys
import os

print("Number of command line arguments: "+str(len(sys.argv)))
print("The arguments are: "+str(sys.argv))

def getEventsCalendar(start_date, end_date, file_path):

	# Gets One Day at a time
	#
	print(start_date)
	# specify the url
	url = 'https://www.forexfactory.com/' + start_date

	# query the website and return the html to the variable ‘page’
	page = urlopen(url)

	# parse the html using beautiful soup and store in variable `soup`
	soup = BeautifulSoup(page, 'html.parser')
	# Take out the <div> of name and get its value

	# Find the table containing all the data
	table = soup.find('table', class_ = 'calendar__table')

	# Date of Event
	date_of_events = table.find_next('tr', class_ = 'calendar__row--new-day').find_next('span', class_ = 'date')

	# Regualr Expression to find the 'day of week', 'month' and the 'day'
	matchObj = re.search('([a-zA-Z]{3})([a-zA-Z]{3}) ([0-9]{1,2})', date_of_events.text)

	# Assigning the 'day of week', 'month' and 'day'

	day_of_week = matchObj.group(1)
	month = matchObj.group(2)
	month = strToIntMonth(month) # Convert from Str to Int
	# if month in monthsList:
	# 	print(month)
	month = int(format(month, "02")) # Places 0's in front of the month if it is single digit day, for months Jan - Sep
	day = matchObj.group(3)
	day = int(format(int(day), "02")) # Places 0's in front of the day if it is single digit day, for days 1-9 of the month
	year = int(start_date[-4:])

	# Event Times 
	event_times = table.find_all('td', class_ = 'calendar__time')

	# Used to hold event time as not all event times have a time if multiple news events start at the same time
	event_time_holder = '' # Holds event time of previous news event as news event is not 

	if(day_of_week != 'Sat' and day_of_week != 'Sun' ):
		for news in event_times:
			curr = news.find_next_sibling('td', class_ = 'currency').text.strip()
			impact = news.find_next_sibling('td', class_ = 'impact').find_next('span')['class']
			impact = impact[0]
			event = news.find_next_sibling('td', class_ = 'event').find_next('span').text.strip()
			previous = news.find_next_sibling('td', class_ = 'previous').text
			forecast = news.find_next_sibling('td', class_ = 'forecast').text
			actual = news.find_next_sibling('td', class_ = 'actual').text
			event_time = news.text.strip()
			print(event_time)
			print(event)
			try:
				matchObj = re.search('([0-9]+)(:[0-9]{2})([a|p]m)', event_time) # Regex to match time in the format HH:MMam/pm
				if(matchObj != None):
					event_time_hour = matchObj.group(1) # Matches the first group in the regex which is the hour in HH format
					event_time_minutes = matchObj.group(2) # Matches the second group in the regex which is the minutes in :MM format 
					am_or_pm = matchObj.group(3) # Matches the third group in the regex which is either 'am' or 'pm'
				elif(re.search('All Day', event_time)):
					event_time_hour = '0'
					event_time_minutes = ':00'
					am_or_pm = 'am'
				elif(re.search('Day [0-9]+', event_time)):
					event_time_hour = '0'
					event_time_minutes = ':00'
					am_or_pm = 'am'
				else:
					event_time_hour = '0'
					event_time_minutes = ':00'
					am_or_pm = 'am'

				# print("Event time hour: "+event_time_hour)
				# print("Event time Minutes: "+event_time_minutes)
				# print("AM or PM: "+am_or_pm)
				adjusted_date_time = timeDateAdjust(event_time_hour, event_time_minutes, am_or_pm, 5, year, month, day) # Returns a tuple with 3 elements consisting of 'event date YYYY:MM:DD', 'event time HH:MM', 'day of week Mon-Fri'

				event_date = adjusted_date_time[0]
				event_time = adjusted_date_time[1]
				day_of_week = adjusted_date_time[2]

				if event_time != '' and event_time != 'All Day': # If the event time is not empy and not 'All day' then we have found a time 
					event_time_holder = str(adjusted_date_time[1]) # Set the event_time_holder to this event_time so any subsequent events also have the same time as this event
																   # As forex factory only provides a time for the first event
					event_date_time = '{} {}'.format(event_date, event_time_holder) #
				else:
					event_time_holder = event_time_holder # event_time_holder remains the same and should have the value of the first event which was assigned a time
					event_date_time = '{} {}'.format(event_date, event_time_holder) #
			except Exception as e:
				print("There was an error: "+e)
				# if event_time == "All Day": # If the event_time says 'All day' in forex factory then the regex will not match it and we set it to midnight of that day
				# 	event_time_holder = "0:00"
				# 	event_date_time = '{} {}'.format(event_date, event_time_holder) #
				# else:
				# 	event_time_holder = event_time_holder
				# 	event_date_time = '{} {}'.format(event_date, event_time_holder) #

			with open(file_path, 'a') as file:
				file.write('{}, {}, {}, {}, {}, {}, {}, {}, {}\n'.format(day_of_week, event_date_time, event_time_holder, curr, impact, event, previous, forecast, actual))

	if start_date == end_date:
		print('Successfully retrieved all data')
		cwd = os.path.dirname(file_path)
		file_path = cwd+"//ffc_events_scraper_successful.txt"
		with open(file_path, 'w') as file:
			file.write("")
		return

	scrape_next_day = soup.find('div', class_='head').find_next('a', class_='calendar__pagination--next')['href']

	getEventsCalendar(scrape_next_day, end_date, file_path)


def strToIntMonth(month):
	#
	# Function to convert Str Month into an Int
	#

	# return {

	# 	'Jan' : 1,
	# 	'Feb' : 2,
	# 	'Mar' : 3,
	# 	'Apr' : 4,
	# 	'May' : 5,
	# 	'Jun' : 6,
	# 	'Jul' : 7,
	# 	'Aug' : 8,
	# 	'Sep' : 9,
	# 	'Oct' : 10,
	# 	'Nov' : 11,
	# 	'Dec' : 12

 # 	}

	if(month == 'Jan'):
		return 1
	elif(month == "Feb"):
		return 2
	elif(month == "Mar"):
		return 3
	elif(month == "Apr"):
		return 4
	elif(month == "May"):
		return 5
	elif(month == "Jun"):
		return 6
	elif(month == "Jul"):
		return 7
	elif(month == "Aug"):
		return 8
	elif(month == "Sep"):
		return 9
	elif(month == "Oct"):
		return 10
	elif(month == "Nov"):
		return 11
	elif(month == "Dec"):
		return 12
	else:
		return None

def timeDateAdjust(event_time_hour, event_time_minutes, am_or_pm, hours_to_adjust, year, month, day):

	d = date(year, month, day)

	if(am_or_pm == "am"):
		adjusted_hour = int(event_time_hour) + hours_to_adjust # Hours_to_adjust variable is used to adjust for timzone differences as the forex factory calendar is in EST
	else:
		adjusted_hour = int(event_time_hour) + 12 + hours_to_adjust # If pm then add 12 hours to adjust to 24 hours format
	
	# If adjusted_hour < 24 hours no need to update the date 
	# if it is over 24 then this means that it is the next day and the date needs to be updated.

	if(adjusted_hour < 24):
		adjusted_time = str(adjusted_hour) + event_time_minutes # Returns string representation of the 24h time in HH:MM
		d_of_week = calendar.day_abbr[d.weekday()] # use the calendar API to return Mon-Sun in abbreviated format as a string
		d= d.strftime("%Y.%m.%d") # Returns the date as a string in the format YYYY:MM:DD
		return (d, adjusted_time, d_of_week)
	else:
		adjusted_hour = adjusted_hour - 24 # Minus 24h as it is now the next day and 24h time will be am of the next day
		adjusted_time = str(adjusted_hour) + event_time_minutes # Returns string representation of the 24h time in HH:MM
		d = d + timedelta(days=1) # Adds one day on the original date of the event
		d_of_week = calendar.day_abbr[d.weekday()] # use the calendar API to return Mon-Sun in abbreviated format as a string
		d= d.strftime("%Y.%m.%d") # Returns the date as a string in the format YYYY:MM:DD
		return (d, adjusted_time, d_of_week)

	d = date(year, month, day)
	
if __name__ == "__main__":
    """
    Run this using the command "python `script_name`.py >> `output_name`.csv"
    """
    abs_path = os.path.abspath(__file__)
    cwd = os.path.dirname(abs_path)
    parent_dir = os.path.dirname(cwd)  
    # print(parent_dir)
    file_path = parent_dir + "\\Files\\test.csv"
    # print("Absolute Path"+abs_path)
    # print("File Path: "+file_path)
    with open(file_path, 'a') as file:
    	file.write(""); # Needs to write an empty line so that file is opened and getEventsCalendar can append to the file
    getEventsCalendar("calendar.php?day=jan1.2016","calendar.php?day=jul15.2018", file_path)

