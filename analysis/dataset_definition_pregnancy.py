from ehrql import create_dataset, weeks, days, show, case, when
from ehrql.tables.tpp import patients, practice_registrations, clinical_events
import codelists
dataset = create_dataset()

start_date = "2023-05-01"
#end_date = "2024-08-31"

# Here we want to create a flag for each female patient of childbearing age, to indicate if
# they were pregnant on the index/start date, for each month the dataset definition is run.
# It will be an approximation only, as we will never know what date someone first knew they 
# were pregnant, and lots of data on early losses is not recorded.

# We will primarily base the logic around delivery /end of pregnancy dates and "Estimated date of delivery"
# which are generally well recorded.

# look back for recent end-of-pregnancy codes -- assume no longer pregnant if in last 12 weeks
dataset.pregnancy_end_recent = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date - weeks(32), start_date - days(1))
    ).sort_by(clinical_events.date).last_for_patient().date

# look ahead for end-of-pregnancy codes
# look ahead 40 weeks - this captures most relevant pregnancies:
#   person may not know about pregnancy until at least 5-6w;
#   but gestation may be longer than 40 weeks;
#   we're also looking across a whole month so some pregnancies may have started 4-5w later than others.
# NB We're not splitting between short vs full term pregnancies so we can't be sure when each one started 
# using this information alone. EDD should capture most though (next variable).
dataset.pregnancy_end = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.end_pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date, start_date + weeks(40))
    ).sort_by(clinical_events.date).first_for_patient().date


# estimated date of delivery (EDD) - very recent or in future
# to estimate the known start of pregnancy
# this date should assume exactly 40w gestation will be reached so we can calculate exact start of pregnancy, 
# but likely unknown until ~6w, so only include those 32w from middle of month ie. 34w from start
dataset.pregnancy_edd = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date - weeks(2), start_date + weeks(34))
    &
    clinical_events.snomedct_code.is_in(codelists.edd_codes)
    ).sort_by(clinical_events.date).first_for_patient().date
    

# recent "pregnant" codes - this is to be used where no delivery or EDD recorded
# note some patients may have an unrecorded miscarriage or termination soon after pregnancy recorded
# but we will be excluding those with recorded end-of-pregnancy prior to this step
dataset.pregnancy_code = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date + weeks(4))
    ).sort_by(clinical_events.date).first_for_patient().date



# combine criteria to create a pregnancy status for the current month:
dataset.pregnant = case(
    # recent delivery -> not pregnant now:
    when(dataset.pregnancy_end_recent.is_on_or_after(start_date - weeks(12))).then("0-R"),
    # end of pregnancy in month or next 2 months - currently pregnant:
    when(dataset.pregnancy_end.is_on_or_before(start_date + weeks(12))).then("P-E"),
    # EDD in month or next 8 months, not preceeded by an end-of-pregnancy
    when(dataset.pregnancy_edd.is_not_null() 
        # check that the pregnancy linked to the EDD did not end very early,
        # i.e prior to the last 12 weeks which is already captured above
         & (dataset.pregnancy_end_recent.is_null() # no past delivery captured
            | ~dataset.pregnancy_end_recent.is_on_or_between(dataset.pregnancy_edd-weeks(28),dataset.pregnancy_edd+weeks(3))
            )).then("P-EDD"),
    # recent pregnancy code
    when(dataset.pregnancy_code.is_not_null()).then("P"),
    otherwise="0",
)

# binary flag:
dataset.pregnant_flag = case(
    when(dataset.pregnant.is_in(("P-E", "P-EDD", "P"))).then(1),
    otherwise=0,
)

################### SENSE CHECKS ##############################
# Sense checks:
# check all the combinations of critera for areas of agreement/uncertainty/conflict

# SENSE CHECK 1
# for those with recent delivery, check how soon new pregnancy codes occur in the next 12 weeks
dataset.ck_pregnancy_future = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.pregnancy_codelist)
    &
    clinical_events.date.is_on_or_between(dataset.pregnancy_end_recent+days(1), dataset.pregnancy_end_recent + weeks(12))
    ).sort_by(clinical_events.date).first_for_patient().date

dataset.ck_diff_new_preg = (dataset.ck_pregnancy_future - dataset.pregnancy_end_recent).weeks

# SENSE CHECK 2
# check spread over time of groups of delivery codes (result should be positive)
# expect this to affect some patients but generally a small difference 
# due to recording of a single delivery over multiple days
# except for short pregnancies which could be close together
dataset.ck_diff_preg_ends = (dataset.pregnancy_end - dataset.pregnancy_end_recent).weeks

# SENSE CHECK 3-4
# check how many deliveries have an EDD around the same time and how many weeks 
# (negative weeks = early delivery)
dataset.ck_diff_edd_end_recent = (dataset.pregnancy_end_recent - dataset.pregnancy_edd).weeks
dataset.ck_diff_edd_end_current = (dataset.pregnancy_end - dataset.pregnancy_edd).weeks

############################


dataset.sex = patients.sex
dataset.age = patients.age_on(start_date)
dataset.define_population(
    (dataset.sex == "female") & (dataset.age <=50) & (dataset.age >=11)
)

show(dataset)