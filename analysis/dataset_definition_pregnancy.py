from ehrql import create_dataset
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
import codelists
dataset = create_dataset()

start_date = "2024-01-31"
index_date = "2025-11-30"

# registration is not important here as we want to capture pregnancy regardless
#registration_start = practice_registrations.for_patient_on(start_date)
#registration_end = practice_registrations.for_patient_on(index_date)

# create a subset of events
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date, index_date)
)

pregnancy_end = selected_events.where(
    selected_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
)

# estimated date of delivery
# we can use this to estimate the start of pregnancy 9 months earlier
pregnancy_edd = selected_events.where(
    selected_events.snomedct_code.is_in(codelists.edd_codes)
)

dataset.sex = patients.sex
dataset.age = patients.age_on(index_date)
dataset.define_population(
    (patients.sex == "female") & (dataset.age <=50) & (dataset.age >=11)
)
