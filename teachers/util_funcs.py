from datetime import time
from collections import defaultdict
import pprint
from django.db.models import Min, Max
from teachers.models import ClassSchedule

def get_daily_available_slots(day_start=time(5, 0), day_end=time(23, 0)):
    """
    Returns a dict mapping each day_of_week to a list of (start, end) tuples
    where there is no scheduled ClassSchedule.
    
    day_start, day_end: time objects bounding the window you care about.
    """
    # Fetch all schedules, ordered by day and start_time
    qs = ClassSchedule.objects.select_related('subject_id') \
        .order_by('day_of_week', 'start_time')

    # Group the intervals per day
    intervals_by_day = defaultdict(list)
    for sched in qs:
        intervals_by_day[sched.day_of_week].append((sched.start_time, sched.end_time))

    available_by_day = {}
    for day, intervals in intervals_by_day.items():
        free_slots = []
        # Start from the very beginning of the window
        cursor = day_start

        for (start, end) in intervals:
            # If there's a gap between cursor and the next class start, record it
            if start > cursor:
                free_slots.append((cursor, start))
            # Move cursor forward if this class ends later
            if end > cursor:
                cursor = end

        # Finally, if there's time between last class and end of day span
        if cursor < day_end:
            free_slots.append((cursor, day_end))

        available_by_day[day] = free_slots

    # Also include days with no classes at all
    all_days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for d in all_days:
        available_by_day.setdefault(d, [(day_start, day_end)])

    print([
        {"day_of_week": day, "free_slots": [
            {"start": s, "end": e} for s, e in slots
        ]}
        for day, slots in available_by_day.items()
    ])
    return available_by_day
