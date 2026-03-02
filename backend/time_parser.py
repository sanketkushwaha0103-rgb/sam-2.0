import re
from datetime import datetime, timedelta


def _parse_clock(text, base_date):
    text = text.strip().lower()
    match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or "0")
    ampm = match.group(3)

    if minute > 59:
        return None

    if ampm:
        if hour < 1 or hour > 12:
            return None
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
    elif hour > 23:
        return None

    return datetime(
        year=base_date.year,
        month=base_date.month,
        day=base_date.day,
        hour=hour,
        minute=minute,
    )


def parse_time_text(time_text, now=None):
    now = now or datetime.now()
    text = time_text.strip().lower().replace(",", " ")
    text = re.sub(r"\s+", " ", text)

    rel_match = re.fullmatch(r"(?:in )?(\d+)\s*(minute|minutes|hour|hours|day|days)", text)
    if rel_match:
        amount = int(rel_match.group(1))
        unit = rel_match.group(2)
        if "minute" in unit:
            dt = now + timedelta(minutes=amount)
        elif "hour" in unit:
            dt = now + timedelta(hours=amount)
        else:
            dt = now + timedelta(days=amount)
        return dt, None

    abs_match = re.fullmatch(r"on (\d{4}-\d{2}-\d{2})(?: at (.+))?", text)
    if abs_match:
        try:
            base = datetime.strptime(abs_match.group(1), "%Y-%m-%d")
        except ValueError:
            return None, "I couldn't parse that date. Use YYYY-MM-DD."
        time_part = abs_match.group(2) or "09:00"
        dt = _parse_clock(time_part, base.date())
        if not dt:
            return None, "I couldn't parse that time. Try formats like 9 pm or 21:00."
        return dt, None

    today_match = re.fullmatch(r"today(?: at (.+))?", text)
    if today_match:
        time_part = today_match.group(1) or "21:00"
        dt = _parse_clock(time_part, now.date())
        if not dt:
            return None, "I couldn't parse that time. Try formats like 9 pm or 21:00."
        return dt, None

    tomorrow_match = re.fullmatch(r"tomorrow(?: at (.+))?", text)
    if tomorrow_match:
        time_part = tomorrow_match.group(1) or "09:00"
        base = (now + timedelta(days=1)).date()
        dt = _parse_clock(time_part, base)
        if not dt:
            return None, "I couldn't parse that time. Try formats like 9 pm or 21:00."
        return dt, None

    at_match = re.fullmatch(r"(?:at )?(.+)", text)
    if at_match:
        clock_text = at_match.group(1)
        dt = _parse_clock(clock_text, now.date())
        if dt:
            if dt < now:
                dt = dt + timedelta(days=1)
            return dt, None

    return None, "I couldn't parse that time. Try: at 9 pm, tomorrow at 8, or in 30 minutes."


def format_when(dt):
    return dt.strftime("%Y-%m-%d %I:%M %p")
