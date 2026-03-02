from ehrql import create_dataset, weeks, days, show, case, when
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
import codelists
dataset = create_dataset()

start_date = "2023-05-01"
#end_date = "2024-08-31"


# look back for recent end-of-pregnancy codes -- assume no longer pregnant if in last 12 weeks
dataset.pregnancy_end_recent = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date - weeks(30), start_date - days(1))
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
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date + weeks(4))
    ).sort_by(clinical_events.date).first_for_patient().date



# combine criteria to create a pregnancy status for the current month:
dataset.pregnant = case(
    # recent delivery -> not pregnant now
    when(dataset.pregnancy_end_recent.is_on_or_after(start_date - weeks(12))).then("0-R"),
    # end of pregnancy in month or next 3 months
    when(dataset.pregnancy_end.is_on_or_before(start_date + weeks(16))).then("P-E"),
    # EDD in month or next 8 months, not preceeded by an end-of-pregnancy
    when(dataset.pregnancy_edd.is_not_null() 
        # check that the pregnancy linked to the EDD did not end very early,
        # i.e prior to the last 12 weeks which is already captured above
         & (dataset.pregnancy_end_recent.is_null()
            | ~dataset.pregnancy_end_recent.is_on_or_between(dataset.pregnancy_edd-weeks(30),dataset.pregnancy_edd+weeks(3))
            )).then("P-EDD"),
    # recent pregnancy code
    when(dataset.pregnancy_code.is_not_null()).then("P"),
    otherwise="0",
)


sex = patients.sex
age = patients.age_on(start_date)
dataset.define_population(
    (sex == "female") & (age <=50) & (age >=11)
)

show(dataset)