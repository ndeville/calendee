####################
# CALENDEE

import os
import sys

from dotenv import load_dotenv
load_dotenv()
USER_PATH = os.getenv("USER_PATH")

import pprint
pp = pprint.PrettyPrinter(indent=4)

from datetime import datetime, time, timezone, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import subprocess

# for pasting
from pynput.keyboard import Key, Controller
keyb = Controller()

# Email addresses of calendars to check
EMAIL_BB = os.getenv("EMAIL_BB")
EMAIL_DV = os.getenv("EMAIL_DV")

####################
# GLOBAL VARIABLES

test = False

blacklist = os.getenv("BLACKLIST_MEETINGS_PARTICIPANTS").split(",")

met_with = set()
meetings = []
meetings_ids = []

####################
# CLASSES

class Meeting:
    def __init__(self):
        self.id = '' # from Google
        self.uid = '' # self.organiser + self.start
        self.summary = ''
        self._date = '' # from Google 'start'
        self.htmlLink = ''
        self.attendees = set() # unique emails from both 'attendees' and 'organiser'
        self.description = ''

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if isinstance(value, str) and len(value) == 10 and value[4] == '-' and value[7] == '-':
            year, month, day = value.split('-')
            try:
                year = int(year)
                month = int(month)
                day = int(day)
                if 1 <= month <= 12 and 1 <= day <= 31:
                    self._date = value
                else:
                    raise ValueError("Invalid date value")
            except ValueError:
                raise ValueError("Invalid date format. Should be YYYY-MM-DD")
        else:
            raise ValueError("Invalid date format. Should be YYYY-MM-DD")


####################
# FUNCTIONS

def get_all_events(calendar_id, token, test=False):
    # Set up Google API credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(token, scopes=SCOPES)
    creds = credentials.with_subject(calendar_id)

    # Build the Google Calendar API client
    service = build('calendar', 'v3', credentials=creds)

    # Initialize an empty list to store all events
    all_events = []

    # Initialize the page token
    page_token = None

    # Get the current time in UTC
    now = datetime.utcnow()
    now_formatted = now.isoformat() + 'Z'

    # Set the maximum time to be 1 month in the future (covers potential holidays)
    # max_time = now + timedelta(days=30)
    # max_time_formatted = max_time.isoformat() + 'Z'

    # Set the maximum time to be today, for only past events
    max_time = now
    max_time_formatted = max_time.isoformat() + 'Z'

    # Call the Google Calendar API to get events and handle pagination
    while True:
        events_result = service.events().list(
            calendarId=calendar_id,
            # timeMin=now_formatted,
            timeMax=max_time_formatted,
            singleEvents=True,
            orderBy='startTime',
            pageToken=page_token
        ).execute()

        events = events_result.get('items', [])
        all_events.extend(events)

        # Check if there is a next page token, if not break the loop
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break

    if test:
        for event in all_events:
            print(f"\n========\n")
            pp.pprint(event)

    return all_events

def construct_meeting(event, test=False):
    global blacklist

    m = Meeting()

    m.id = event['id']

    m._date = '' # from Google 'start'
    try:
        m._date = event['start']['dateTime'].split('T')[0]
    except KeyError:
        m.date = event['start']['date']

    m.htmlLink = event['htmlLink']

    if 'description' in event:
        m.description = event['description']

    # Attendees / only if not in blacklist
    if 'attendees' in event:
        attendees = event['attendees']
        if len(attendees) > 1:
            for attendee in attendees:
                attendee_email = attendee['email']
                if attendee_email not in blacklist:
                    m.attendees.add(attendee_email)
    organiser = event['organizer']['email']
    if organiser not in blacklist:
        m.attendees.add(organiser)

    m.attendees = list(m.attendees)

    if len(m.attendees) > 0:

        if test:
            print(f"{m.attendees=} on {m.date}")

        # UID
        try:
            m.uid = f"{m.attendees[0]}-{m.date}"
        except KeyError:
            print(f"\n\nERROR with {event['id']}:")
            pp.pprint(event)
        m.summary = event['summary']

        return m
    
    else:
        return None # no attendees meeting

def process_events(all_events_from_one_calendar, test=False):
    global met_with
    global meetings
    global meetings_ids

    for event in all_events_from_one_calendar:

        m = construct_meeting(event)

        if m != None:

            # if m.uid not in meetings_ids:
            if m.id not in meetings_ids:
                meetings.append(m)
                # meetings_ids.append(m.uid)
                meetings_ids.append(m.id)
                met_with = met_with.union(set(m.attendees))
            else:
                print(f"\n\nDuplicate meeting: {m.uid=}")

# MAIN FUNCTION


## BB
all_future_events_bb = get_all_events(EMAIL_BB, f'{USER_PATH}creds_bb/service_key.json')

process_events(all_future_events_bb, test=test)

## DV
all_future_events_dv = get_all_events(EMAIL_DV, f'{USER_PATH}creds_dv/service_key.json')

process_events(all_future_events_dv, test=test)


print(f"\n\n{len(meetings)} meetings:")
for meeting in meetings:
    attendees = ",".join(meeting.attendees)
    print(f"    - {meeting.summary} with {attendees}")

print(f"\n\nMet with {len(met_with)} people:")
for met in met_with:
    # print(f"\"{met}\",")
    print(met)

# 230315-2219 if I am the attendee, event added twice
# Create a Meeting class and dedupe attendees/organiser under a single "attendees" set. 
# Process list of objects with uid as key.  

# then make functions and add BB

########################################################################################################

if __name__ == '__main__':
    print()
    arguments = sys.argv

    # Get timezone argument, if passed
    # if len(sys.argv) > 1: 
    #     tz = sys.argv[1].upper()
    # else:
    #     tz = "CET"
    # print(f"tz: {tz}")


    # Write to clipboard
    # write_to_clipboard(my_availabilities)

    # Paste availabilities
    # paste()