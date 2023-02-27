# calendee

Notes: <a href="https://notes.nicolasdeville.com/projects/calendee" target="_blank">https://notes.nicolasdeville.com/projects/calendee</a>  

Working code, used via keyboard shortcuts using <a href="https://www.alfredapp.com/" target="_blank">Alfred</a> (optional).  

## Variables

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

## Outputs

Standard:  

``` bash
(CET / Germany time)

- tomorrow 11:00, 12:00 or 16:00
- Wed 01st 11:00, 12:00, 16:00 or 17:00
- Thu 02nd 11:00, 12:00, 16:00 or 17:00
- Fri 03rd 11:00, 12:00, 16:00 or 17:00
- Mon 06th 11:00, 12:00 or 17:00

or see all availabilities at https://cal.com/ndeville
```

UK:  

``` bash
(UK time)

- tomorrow 10, 11 or 3
- Wed 01st 10, 11, 3 or 4
- Thu 02nd 10, 11, 3 or 4
- Fri 03rd 10, 11, 3 or 4
- Mon 06th 10, 11 or 4

or see all availabilities at https://cal.com/ndeville
```

PT: 

``` bash
(PT)

- tomorrow 2, 3 or 7
- Wed 01st 2, 3, 7 or 8
- Thu 02nd 2, 3, 7 or 8
- Fri 03rd 2, 3, 7 or 8
- Mon 06th 2, 3 or 8

or see all availabilities at https://cal.com/ndeville
```

## TODO

- finalise am/pm formatting
- ensure X number of days of availabilities are always returned (eg if holidays are coming up)  