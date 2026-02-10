from ehrql import create_dataset, weeks, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
import codelists
dataset = create_dataset()

start_date = "2024-01-31"
index_date = "2025-11-30"

# registration is not important here as we want to capture pregnancy regardless
#registration_start = practice_registrations.for_patient_on(start_date)
#registration_end = practice_registrations.for_patient_on(index_date)

dataset.pregnancy_end = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)).sort_by(clinical_events.date).last_for_patient().date

#dataset.pregnancy_end = clinical_events.where(
#    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)).sort_by(clinical_events.date).last_for_patient().date


# estimated date of delivery
# we can use this to estimate the start of pregnancy 9 months earlier
dataset.pregnancy_edd = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.edd_codes)).sort_by(clinical_events.date).last_for_patient().date

# calculate gestation at end of pregnancy
pregnancy_how_early = (dataset.pregnancy_edd - dataset.pregnancy_end).weeks
dataset.pregnancy_length_from_edd = 40 - pregnancy_how_early


# for start of pregnancy, assume pregnancy status known from 8 weeks
dataset.pregnancy_known_date = dataset.pregnancy_edd - weeks(32)


dataset.sex = patients.sex
dataset.age = patients.age_on(index_date)
dataset.define_population(
    (patients.sex == "female") & (dataset.age <=50) & (dataset.age >=11)
)

show(dataset)