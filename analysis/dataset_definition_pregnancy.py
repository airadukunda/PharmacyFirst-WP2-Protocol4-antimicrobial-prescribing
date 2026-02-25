from ehrql import create_dataset, weeks, days, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
import codelists
dataset = create_dataset()

start_date = "2022-03-01"
end_date = "2024-03-31"

# Assumptions:


# look back for recent end-of-pregnancy codes -- assume no longer pregnant
dataset.pregnancy_end_recent = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date - days(1))
    ).sort_by(clinical_events.date).last_for_patient().date

# look ahead for end-of-pregnancy codes 
# look ahead 40 weeks (may not be known at the start but may be longer than 40 weeks, etc)
dataset.pregnancy_end = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date, start_date + weeks(40))
    ).sort_by(clinical_events.date).first_for_patient().date


# estimated date of delivery - very recent or in future
# we can use this to estimate the known start of pregnancy ~8 months earlier
dataset.pregnancy_edd = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date - weeks(2), start_date + weeks(40))
    &
    clinical_events.snomedct_code.is_in(codelists.edd_codes)
    ).sort_by(clinical_events.date).first_for_patient().date
    
# for start of pregnancy, assume pregnancy status known from 8 weeks
dataset.pregnancy_known_date = dataset.pregnancy_edd - weeks(32)


# (Allow end of pregnancy up to 4 weeks "late" or 36 weeks "early")

# calculate gestation at end of pregnancy
# pregnancy_how_early = (dataset.pregnancy_edd - dataset.pregnancy_end_first).weeks
# dataset.pregnancy_length_from_edd = 40 - pregnancy_how_early


# recent "pregnant" codes
dataset.pregnancy_code = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date + weeks(2))
    ).sort_by(clinical_events.date).first_for_patient().date



# combine criteria:
# NOT recent delivery 
# AND one of the following:
#   delivery in month or next 3 months
#   EDD in month or next 8 months not preceeded by an end-of-pregnancy has not ended
#   recent "pregnancy" code



dataset.sex = patients.sex
dataset.age = patients.age_on(start_date)
dataset.define_population(
    (patients.sex == "female") & (dataset.age <=50) & (dataset.age >=11)
)

show(dataset)