"""RFC5545 RRULE handling for recurring tasks/appointments (#38).

Recurrence is stored as a single RRULE string on `Task.recurrence_rule` (e.g.
"FREQ=WEEKLY;BYDAY=MO"). Instances are materialized on read rather than
pre-generated as rows, keeping the model simple: a recurring Task is one DB
row, and callers ask for its occurrences within a window.
"""

from datetime import date, datetime, timezone

from dateutil.rrule import rrulestr

from app.models.task import Task

MAX_INSTANCES = 200


def validate_recurrence_rule(rule: str) -> bool:
    if not rule:
        return False
    try:
        anchor = datetime.now(timezone.utc).replace(microsecond=0)
        rrulestr(rule, dtstart=anchor)
        return True
    except (ValueError, TypeError):
        return False


def expand_occurrences(task: Task, range_start: date, range_end: date) -> list[date]:
    """Return the occurrence dates of a recurring task within [range_start, range_end].

    Falls back to the task's own due_date/start_at if there is no recurrence_rule.
    """
    anchor = task.start_at or (
        datetime.combine(task.due_date, datetime.min.time(), tzinfo=timezone.utc)
        if task.due_date
        else None
    )
    if not task.recurrence_rule or not anchor:
        base_date = task.due_date or (task.start_at.date() if task.start_at else None)
        if base_date and range_start <= base_date <= range_end:
            return [base_date]
        return []

    try:
        rule = rrulestr(task.recurrence_rule, dtstart=anchor)
    except (ValueError, TypeError):
        return []

    window_start = datetime.combine(range_start, datetime.min.time(), tzinfo=anchor.tzinfo)
    window_end = datetime.combine(range_end, datetime.max.time(), tzinfo=anchor.tzinfo)
    occurrences = rule.between(window_start, window_end, inc=True)
    return [occurrence.date() for occurrence in occurrences[:MAX_INSTANCES]]
