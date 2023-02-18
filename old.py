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