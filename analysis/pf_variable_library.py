# Functions to check status of a condition within a specified time window etc
# Copy from https://github.com/opensafely/pharmacy-first/blob/main/analysis/pf_variables_library.py

from ehrql import months, days

def check_pregnancy_status(index_date, selected_events, codelist):
    return (
        selected_events.where(selected_events.snomedct_code.is_in(codelist))
        .where(
            selected_events.date.is_on_or_between(index_date - months(1), index_date)
        )
        .exists_for_patient()
    )

# Function to check bullous impetigo status within a specified time window
def check_bullous_impetigo_status(start_date, end_date, selected_events, codelist):
    """
    Returns True if a patient has any bullous impetigo code
    recorded between start_date and end_date (inclusive).
    """

    return (
        selected_events.where(selected_events.snomedct_code.is_in(codelist))
        .where(
            selected_events.date.is_on_or_between(start_date, end_date)
        )
        .exists_for_patient()
    )

def check_catheter_status(index_date, events, codelist, lookback_months=12):
    """
    Returns True if patient has any urinary catheter code
    within lookback_months before index_date.
    """

    catheter_events = (
        events.where(events.snomedct_code.is_in(codelist))
        .where(events.date.is_on_or_between(index_date - months(lookback_months),index_date))
    )

    return catheter_events.exists_for_patient()

# Generic recurrent condition checker.
def check_recurrent_status(
    index_date,events,codelist,
    lookback_months,min_episodes,
):
    condition_events = (
        events
        .where(events.snomedct_code.is_in(codelist))
        .where(events.date.is_on_or_between(index_date - months(lookback_months),index_date,)
        )
    )

    event_count = condition_events.count_for_patient()

    first_date = (condition_events.sort_by(condition_events.date).first_for_patient().date)
    last_date = (condition_events.sort_by(condition_events.date).last_for_patient().date)

    separated = last_date >= first_date + days(28)

    return (event_count >= min_episodes) & separated

# Function to count number of coded events within a specified time window
def count_past_events(index_date, selected_events, codelist, num_months):
    return (
        selected_events.where(selected_events.snomedct_code.is_in(codelist))
        .where(
            selected_events.date.is_on_or_between(
                index_date - months(num_months), index_date
            )
        )
        .count_for_patient()
    )


# Function to get events linked to a specified codelist
def select_events_from_codelist(event_frame, codelist):
    selected_events = event_frame.where(event_frame.snomedct_code.is_in(codelist))

    return selected_events


# Function to get events with specific consultation IDs
def select_events_by_consultation_id(event_frame, consultation_ids):
    selected_events = event_frame.where(
        event_frame.consultation_id.is_in(consultation_ids)
    )
    return selected_events


# Function to get events within a time frame
def select_events_between(event_frame, start_date, end_date):
    selected_events = event_frame.where(
        event_frame.date.is_on_or_between(start_date, end_date)
    )
    return selected_events


def select_events(
    event_frame, codelist=None, consultation_ids=None, start_date=None, end_date=None
):
    """
    Wrapper function to select events based on codelist, consultation IDs, or a date range.
    Allows combining multiple selection criteria.
    """
    selected_events = event_frame

    if codelist is not None:
        selected_events = select_events_from_codelist(selected_events, codelist)
    if consultation_ids is not None:
        selected_events = select_events_by_consultation_id(
            selected_events, consultation_ids
        )
    if start_date is not None and end_date is not None:
        selected_events = select_events_between(selected_events, start_date, end_date)

    return selected_events