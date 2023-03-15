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

print("\n\n")

####################
# GLOBAL VARIABLES

test = False

blacklist = os.getenv("BLACKLIST_MEETINGS_PARTICIPANTS").split(",")

met_with = set()
meetings = []
meetings_ids = []

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



# MAIN FUNCTION

# all_future_events_bb = get_all_events(EMAIL_BB, f'{USER_PATH}creds_bb/service_key.json')
# if test:
    # print(f"\nall_future_events_bb:")
    # pp.pprint(all_future_events_bb)

all_future_events_dv = get_all_events(EMAIL_DV, f'{USER_PATH}creds_dv/service_key.json')

# if test:
    # print(f"\nall_future_events_dv:")
    # pp.pprint(all_future_events_dv)

for event in all_future_events_dv:
    uid = event['id']
    # uid = event['iCalUID']
    # uid = f"{event['organizer']['email']}-{event['start']['dateTime']}"
    # print(f"\n{uid=}")
    if 'attendees' in event:
        attendees = event['attendees']
        if len(attendees) > 1:
            for attendee in attendees:
                attendee_email = attendee['email']
                if attendee_email not in blacklist:
                    met_with.add(attendee_email)
                    meetings.append(event)
        organiser = event['organizer']['email']
        if organiser not in blacklist:
            met_with.add(organiser)
            if uid not in meetings_ids:
                meetings.append(event)
                meetings_ids.append(uid)
            else:
                print(f"\n\nDuplicate meeting: {uid=}")

print(f"\n\n\nMeetings:")
for meeting in meetings:
    print(f"    - {meeting['summary']} organised by {meeting['organizer']['email']}")
print(f"\nTOTAL: {len(meetings)=} meetings:")


print(f"\n\nMet with {len(met_with)} people:")
for met in met_with:
    print(f"\"{met}\",")

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