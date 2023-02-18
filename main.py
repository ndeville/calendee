import os
import sys

from dotenv import load_dotenv
load_dotenv()
USER_PATH = os.getenv("USER_PATH")

import pprint
pp = pprint.PrettyPrinter(indent=4)

####################
# CALENDAREE (WORK IN PROGRESS)

from datetime import datetime, time, timezone, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
# import pytz
import subprocess

# for pasting
from pynput.keyboard import Key, Controller
keyb = Controller()

EMAIL_BB = os.getenv("EMAIL_BB")
EMAIL_DV = os.getenv("EMAIL_DV")

print("\n\n\n\n")

# Global variables

test = False

available_days = [ # comment lines below to make unavailable
    "Mon",
    "Tue",
    "Wed",
    "Thu",
    "Fri",
]

available_hours = [ # comment lines below to make unavailable
    # "08:00",
    # "09:00",
    # "10:00",
    "11:00",
    # "11:30",
    "12:00",
    # "13:00",
    # "14:00",
    # "15:00",
    "16:00",
    # "16:30",
    "17:00",
    # "18:00",
    # "19:00",
]


timezones = { # This will define the return time & format
    "CET": 0, # default
    "UK": 1, # timezone offset in hours
    "ET": 6,
    "MT": 7,
    "PT": 9,
}

# Insert output functions

def write_to_clipboard(output):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))
    print(f"\nOUTPUT COPIED TO CLIPBOARD\n")

def paste():
    with keyb.pressed(Key.cmd):
        keyb.press('f')
        keyb.release('f')

# DAYS

def is_weekday(date):
    """
    Returns True if the given date is a weekday (Monday to Friday),
    and False if it's a weekend day (Saturday or Sunday).
    """
    return date.weekday() < 5

# BLANK AVAILABILITIES

def suffix(day): # day == datetime object
    if 11 <= day.day <= 13:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day.day % 10, 'th')

def format_day(datetime_object):
    
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)

    day = datetime_object.day

    # Use the custom suffix() function to determine the appropriate suffix for the day
    suffix_str = suffix(datetime_object)
    day_name = datetime_object.strftime("%a %d" + suffix_str)

    if day == tomorrow.day:
        formatted_day = f"tomorrow"
    else:
        formatted_day = f"{day_name}"

    return formatted_day

def format_time(datetime_object, ampm=False):

    # hour = datetime_object.strftime("%H:%M")

    if not ampm:
        formatted_time = datetime_object.strftime("%H:%M")
    else:
        # formatted_time = f"{available_hours[hour]}"
        formatted_time = datetime_object.strftime('%I:%M%p').lower()
        if formatted_time.endswith(":00") and int(formatted_time[:2]) < 12:
            hour = hour[:-3]

    return formatted_time

# EXISTING EVENTS

def get_all_events(calendar_id, token, test=False):
    """
    Gets all future events from a Google Calendar
    """
    # Set up Google API credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(token, scopes=SCOPES)
    creds = credentials.with_subject(calendar_id)

    # Build the Google Calendar API client
    service = build('calendar', 'v3', credentials=creds)


    # Get the current time in UTC
    now = datetime.utcnow()
    now_formatted = now.isoformat() + 'Z'

    # Set the maximum time to be 1 month in the future
    max_time = now + timedelta(days=30)
    max_time_formatted = max_time.isoformat() + 'Z'

    # Call the Google Calendar API to get events
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now_formatted,
        timeMax=max_time_formatted,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    if test:
        pp.pprint(events_result)

    # Get the events from the response
    events = events_result.get('items', [])

    return events

def list_of_events_datetimes(events):
    """
    Takes list of events dicts from Google Calendar
    Returns list of datetimes tuples with start & end times for each event
    """
    events_datetimes_list = []
    for event in events:
        try:
            start = event['start']['dateTime']
            start_datetime = datetime.fromisoformat(start).replace(tzinfo=None) # timezone-naive

            end = event['end']['dateTime']
            end_datetime = datetime.fromisoformat(end).replace(tzinfo=None) # timezone-naive

            events_datetimes_list.append((start_datetime, end_datetime))
        except KeyError:
            print("\nNo start time for this event: ", event['summary'], "\n")
            pass

    return events_datetimes_list


# FINAL AVAILABILITIES

def get_final_availabilities(availabilities, consolidated_events):
    final_availabilities = []
    for start_time, end_time in availabilities:
        available = True
        for booked_start, booked_end in consolidated_events:
            if start_time < booked_end and booked_start < end_time:
                available = False
                break
        if available:
            final_availabilities.append(start_time)
    return final_availabilities

def print_availabilities(final_availabilities, timezone='CET'):
    if timezone == 'CET':
        output = "(CET / Germany time)\n"
        ampm = False
    elif timezone == 'UK':
        output = "(UK)\n"
        ampm = True
    elif timezone == 'ET':
        output = "(ET)\n"
        ampm = True
    elif timezone == 'MT':
        output = "(MT)\n"
        ampm = True
    elif timezone == 'PT':
        output = "(PT)\n"
        ampm = True

    time_offset = timezones[timezone]

    day = False
    # new_line = ""
    for a in final_availabilities:
        a = a - timedelta(hours=time_offset) # convert to recipient timezone
        if day != a.date():
            output = f"{output}\n- {format_day(a)} {format_time(a, ampm=ampm)}"
            day = a.date()
        else:
            output = f"{output}, {format_time(a, ampm=ampm)}"
    
    output = f"{output}\n\nor see all availabilities at https://cal.com/ndeville"
        
    lines = output.split('\n')  # split the text into lines
    for i in range(1, len(lines)):  # skip the first line (header)
        if ',' in lines[i]:  # check if there is a comma in the line
            lst = lines[i].rsplit(", ", 1)  # split the line from the right side by the last comma
            lines[i] = " or ".join(lst)  # join the resulting list with "or" as the last element
    final_output = '\n'.join(lines)  # join the lines back into a single string

    print(final_output)
    return final_output

# MAIN FUNCTION

def get_my_availabilities(timezone="CET", slot=30, weekdays_forward=5, test=False):
    """
    slot = 30 # minutes
    weekdays_forward = 5 # number of weekdays to look forward and return availabilities for
    """
    global available_days
    global available_hours
    global timezones

    # DAYS

    now = datetime.now()

    today = now.date()
    # today_string = f"{now.strftime('%Y-%m-%d %H:%M')}"

    tomorrow = today + timedelta(days=1)
    # tomorrow_string = f"{tomorrow.strftime('%Y-%m-%d %H:%M')}"

    days_to_check = []
    for x in range(1,20): # random high number of days to check for availability
        day_to_check = today + timedelta(days=x)
        if is_weekday(day_to_check) and len(days_to_check) < weekdays_forward:
            days_to_check.append(day_to_check)

    if test:
        print()
        print("days_to_check:")
        pp.pprint(days_to_check)
        print()

    # BLANK AVAILABILITIES (CET)

    availabilities = []

    for day_string in days_to_check:
        for hour in available_hours:

            # Create a START datetime object from the input date and time
            datetime_object_start = datetime.combine(day_string, time.fromisoformat(hour))
            # Create a timedelta object from the global slot variable
            delta = timedelta(minutes=slot)
            # Add the timedelta to the END datetime object
            datetime_object_end = datetime_object_start + delta

            # For timezone senstitivity, we need to set the timezone of the datetime object
            # # Set the timezone of the datetime object to CET
            # cet_timezone = pytz.timezone('CET')
            # datetime_cet = cet_timezone.localize(datetime_object)
            # availabilities.append(datetime_cet)

            availabilities.append((datetime_object_start, datetime_object_end))

    if test:
        print()
        print(f"availabilities:")
        pp.pprint(availabilities)
        print()

    # CONSOLIDATED EVENTS

    datetimes_list_bb = []
    datetimes_list_dv = []

    # BB
    all_future_events_bb = get_all_events(EMAIL_BB, f'{USER_PATH}creds_bb/service_key.json')
    datetimes_list_bb = list_of_events_datetimes(all_future_events_bb)
        
    if test:
        print()
        print(f"datetimes_list_bb:")
        pp.pprint(datetimes_list_bb)

    # DV
    all_future_events_dv = get_all_events(EMAIL_DV, f'{USER_PATH}creds_dv/service_key.json')
    datetimes_list_dv = list_of_events_datetimes(all_future_events_dv)
        
    if test:
        print()
        print(f"datetimes_list_dv:")
        pp.pprint(datetimes_list_dv)

    consolidated_events = datetimes_list_bb + datetimes_list_dv
    consolidated_events = sorted(consolidated_events, key=lambda x: x[0]) # sorted by start time

    if test:
        print()
        print(f"consolidated_events:")
        pp.pprint(consolidated_events)
        print()

    # FINAL AVAILABILITIES

    final_availabilities = get_final_availabilities(availabilities, consolidated_events)

    if test:
        print()
        print(f"final_availabilities:")
        pp.pprint(final_availabilities)

    print("\n\n")
    output_my_availabilities = print_availabilities(final_availabilities, timezone=timezone)

    # TODO
    # - add timezone support

    return output_my_availabilities

# OLD FUNCTION TO CHECK GOOGLE CALENDAR OUTPUT

# def print_events(events, calendar):
#     count = 0

#     # print("\n\n")
#     # pp.pprint(events)
#     # print("\n\n")

#     for event in events:

#         count += 1

#         # Organiser

#         try:
#             organiser_name = event['organizer']['displayName']
#         except:
#             organiser_name = ""
        
#         try:
#             organiser_email = event['organizer']['email']
#         except:
#             organiser_email = ""
        
#         # Summary

#         summary = event['summary']
        
#         # Start

#         try:
#             start = event['start']['dateTime']
#         except:
#             start = event['start']['date']

#         try:
#             start_tz = event['start']['timeZone']
#         except:
#             start_tz = ""

#         # End

#         try:
#             end = event['end']['dateTime']
#         except:
#             end = event['end']['date']

#         try:
#             end_tz = event['end']['timeZone']
#         except:
#             end_tz = ""

#         print(f"\n{calendar} #{count}")
#         print(f"organiser_name\t{organiser_name}")
#         print(f"organiser_email\t{organiser_email}")
#         print(f"from\t\t{start} {start_tz}")
#         print(f"to\t\t{end} {end_tz}")
#         print(f"summary\t\t{summary}")

#     print("\n\n")

# if UPDATE_BB:
#     print_events(all_future_events_bb, "BB")
# if UPDATE_DV:
#     print_events(all_future_events_dv, "DV")

########################################################################################################

if __name__ == '__main__':
    print()
    arguments = sys.argv

    if len(sys.argv) > 1: # if argument passed
        tz = sys.argv[1].upper()
    else:
        tz = "CET"
    print(f"tz: {tz}")

    my_availabilities = get_my_availabilities(timezone=tz)
    write_to_clipboard(my_availabilities)
    paste()
    
