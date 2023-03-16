# calendee

Python scripts interfacing with Google Calendar.  

## availabilities.py

Notes: <a href="https://notes.nicolasdeville.com/projects/calendee" target="_blank">https://notes.nicolasdeville.com/projects/calendee</a>  

Working code, used via keyboard shortcuts using <a href="https://www.alfredapp.com/" target="_blank">Alfred</a> (optional).  

### variables

are `available_days`, `available_hours` & `timezones`:  

``` python
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
```

### outputs

Standard:  

``` bash
(CET / Germany time)

- tomorrow 11:00, 12:00 or 16:00
- Mon 20th 11:00, 12:00, 16:00 or 17:00
- Tue 21st 11:00, 12:00, 16:00 or 17:00

or see all at https://cal.com/ndeville
```

UK:  

``` bash
(UK time)

- tomorrow 10am, 11am or 3pm
- Mon 20th 10am, 11am, 3pm or 4pm
- Tue 21st 10am, 11am, 3pm or 4pm

or see all at https://cal.com/ndeville
```

PT: 

``` bash
(PT)

- tomorrow 2am, 3am or 7am
- Mon 20th 2am, 3am, 7am or 8am
- Tue 21st 2am, 3am, 7am or 8am

or see all at https://cal.com/ndeville
```

# meetings.py

Added <span class="datestamp">16 Mar 2023</span>   

Notes: <a href="https://notes.nicolasdeville.com/projects/calendee#Meetings" target="_blank">https://notes.nicolasdeville.com/projects/calendee#Meetings</a>

Working code. 

Fetches all events with attendees from a Google Calendar, and returns a list of events objects with the following attributes:  

``` python
class Meeting:
    def __init__(self):
        self.id = '' # from Google
        self.summary = ''
        self._date = '' # from Google 'start' in YYYY-MM-DD format
        self.htmlLink = ''
        self.attendees = set() # unique emails from both 'attendees' and 'organiser'
        self.description = ''
        self.domain = '' # WARNING: this caters only for 1 domain per meeting
```