from ehrql import create_dataset, weeks, days, show, case, when
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
import codelists
dataset = create_dataset()

start_date = "2022-01-01"
end_date = "2024-08-31"


# look back for recent end-of-pregnancy codes -- assume no longer pregnant
dataset.pregnancy_end_recent = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date - days(1))
    ).sort_by(clinical_events.date).last_for_patient().date

# look ahead for end-of-pregnancy codes 
# look ahead 38 weeks (approximation as we're using a whole month; 
#   person may not be known about pregnancy until at least 5-6w;
#   but gestation may be longer than 40 weeks)
#   for short pregnancies, may not have been pregnant during present month
dataset.pregnancy_end = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date, start_date + weeks(40))
    ).sort_by(clinical_events.date).first_for_patient().date


# estimated date of delivery - very recent or in future
# we can use this to estimate the known start of pregnancy ~8 months earlier
dataset.pregnancy_edd = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date - weeks(2), start_date + weeks(36))
    &
    clinical_events.snomedct_code.is_in(codelists.edd_codes)
    ).sort_by(clinical_events.date).first_for_patient().date
    

# recent "pregnant" codes
dataset.pregnancy_code = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date + weeks(2))
    ).sort_by(clinical_events.date).first_for_patient().date



# combine criteria to create a pregnancy status for the current month:
dataset.pregnant = case(
    # recent delivery -> not pregnant now
    when(dataset.pregnancy_end_recent.is_not_null()).then(0),
    # end of pregnancy in month or next 3 months
    when(dataset.pregnancy_end.is_on_or_before(start_date + weeks(12))).then(1),
    # EDD in month or next 8 months, not preceeded by an end-of-pregnancy
    when(dataset.pregnancy_edd.is_not_null()
         & ~dataset.pregnancy_end.is_on_or_before(dataset.pregnancy_edd)).then(1),
    # recent pregnancy code
    when(dataset.pregnancy_code.is_not_null()).then(1),
    otherwise=0,
)


dataset.sex = patients.sex
dataset.age = patients.age_on(start_date)
dataset.define_population(
    (patients.sex == "female") & (dataset.age <=50) & (dataset.age >=11)
)

show(dataset)