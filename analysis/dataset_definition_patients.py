# This file defines the population and selects the fields that need to be included in the data for analysis. 
# Get new dummy tables: opensafely exec ehrql:v1 create-dummy-tables analysis/dataset_definition_patients.py dummy_tables

from ehrql import create_dataset, show, months, case, when
from ehrql.tables.tpp import (patients, practice_registrations, clinical_events, addresses, ethnicity_from_sus)
import codelists

dataset = create_dataset()
dataset.configure_dummy_data(population_size=1000)

# One month time period (to start with this is Nov 25) 
start_date = "2025-10-31"     
index_date = "2025-11-30"  

"""
Monthly patient-level denominator + numerator dataset
Patient table key fields:
- [v] Patient identifiers: patient_id, month (start_date, index_date), registration_status, alive_status, practice_id, region, 
- [v] Demographics: age, sex, [to-review]ethnicity, IMD
- [v] PF consultation flag for each condition (True/False for PF code recorded)
- [~] Eligibility/clinical characteristics flag (True/False)

Eligibility/clinical characteristics flag for study population denominator:
- include_patient_otitis_media
- include_patient_sinusitis
- include_patient_sore_throat
- include_patient_insect_bites
- include_patient_shingles
- include_patient_impetigo
- include_patient_uti
- include_patient_overall_eligible: at least one condition

The above variables require:
- pregnant_this_month
- bullous_impetigo_this_month
- recurrent_impetigo_this_year
- catheter_status
- recurrent_uti
"""

########################################################
# Patient identifiers: alive_status, registration_status
alive = patients.is_alive_on(index_date) # alive at the end of month
# Only include the patient if they were registered for the whole month, 
# so registered before the month starts and not deregistered or died during the month
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()

# Demographics: sex, age, patient_imd
sex = patients.sex
age = patients.age_on(index_date)

# Define population
# base_population = patients.exists_for_patient()
age_valid = (patients.age_on(index_date) <= 120) # To confirm with Helen: "Exclude any patients over 120 years old as the date of birth is most likely to be missing"
base_population = alive & registered_start & registered_index & age_valid
dataset.define_population(base_population) # include all patients or those alive and registered

dataset.start_date = case(when(base_population).then(start_date))
dataset.index_date = case(when(base_population).then(index_date))
dataset.registered_start = registered_start
dataset.registered_index = registered_index
dataset.alive = alive
dataset.sex = sex
dataset.age = age
from analysis.pf_variable_library import get_imd, get_latest_ethnicity
dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(index_date,clinical_events,codelists.ethnicity_group16_codelist,ethnicity_from_sus,grouping=16,)
# Patient identifiers: practice_id, stp, region
dataset.practice = practice_registrations.for_patient_on(index_date).practice_pseudo_id
dataset.stp = practice_registrations.for_patient_on(index_date).practice_stp
dataset.region = practice_registrations.for_patient_on(index_date).practice_nuts1_region_name

########################################################
# PF consultation flag for each condition (True/False for PF code recorded) 
# copied from dataset_definition.py
selected_events = clinical_events.where(clinical_events.date.is_on_or_between(start_date, index_date))
pf_consultation_events = selected_events.where(selected_events.snomedct_code.is_in(codelists.pf_consultation_events_dict["pf_consultation_services_combined"]))
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = selected_events.where(selected_events.consultation_id.is_in(pf_ids))

def has_event(events, codelist):
    return events.where(events.snomedct_code.is_in(codelist)).exists_for_patient()

dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()
dataset.uti_numerator = has_event(selected_pf_id_events,codelists.uti_code)
dataset.sinusitis_numerator = has_event(selected_pf_id_events,codelists.sinusitis_code)
dataset.insectbite_numerator = has_event(selected_pf_id_events,codelists.insectbite_code)
dataset.otitismedia_numerator = has_event(selected_pf_id_events,codelists.otitismedia_code)
dataset.sorethroat_numerator = has_event(selected_pf_id_events,codelists.sorethroat_code)
dataset.shingles_numerator = has_event(selected_pf_id_events,codelists.shingles_code)
dataset.impetigo_numerator = has_event(selected_pf_id_events,codelists.impetigo_code)

########################################################
"""
Clinical variables for eligible population denominator:
- pregnant_this_month
- bullous_impetigo_this_month
- recurrent_impetigo_this_year
- catheter_status
- recurrent_uti
"""

from analysis.pf_variable_library import check_code_in_time_window, check_recurrent_status # To confirm with Helen - recurrent check
# [] Flag: pregnancy_status # To confirm with Helen - any update
pregnant_this_month = check_code_in_time_window(index_date-months(1),index_date, clinical_events, codelists.pregnancy_codelist)
dataset.pregnant_this_month = pregnant_this_month
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug

# [] Flag: bullous_impetigo within 4 weeks
bullous_impetigo_this_month = (age < 0)
# bullous_impetigo_this_month = check_code_in_time_window(start_date,index_date,clinical_events,codelists.bullous_impetigo_code)
dataset.bullous_impetigo_this_month = bullous_impetigo_this_month
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug

# [] Flag: recurrent_impetigo: (defined as 2 or more episodes in the same year) 
# an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
# >= two 4-week-separated episodes
recurrent_impetigo_this_year = (age < 0)
# recurrent_impetigo_this_year = check_recurrent_status(index_date, clinical_events, codelists.impetigo_codelist, 
#                                                       lookback_months=12, gap_weeks=4, min_episodes=2)
dataset.recurrent_impetigo_this_year = recurrent_impetigo_this_year
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug


# [] Flag: catheter_status: excluding patients who clearly have a catheter, and for following 12 months after code is included
catheter_status = (age < 0)
# catheter_status = check_code_in_time_window(index_date - months(12),index_date,clinical_events,codelists.catheter_codelist)
dataset.catheter_status = catheter_status
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug


# [] Flag: recurrent_uti: (2 episodes in last 6 months, or 3 episodes in last 12 months) an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
recurrent_uti_6m = (age < 0)
recurrent_uti_12m = (age < 0)
# recurrent_uti_6m = check_recurrent_status(
#     index_date, clinical_events, codelists.uti_code,
#     lookback_months=6, gap_weeks=4,min_episodes=2
# )
# recurrent_uti_12m = check_recurrent_status(
#     index_date, clinical_events, codelists.uti_code,
#     lookback_months=12, gap_weeks=4, min_episodes=3
# )
recurrent_uti = recurrent_uti_6m | recurrent_uti_12m
dataset.recurrent_uti = recurrent_uti
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug

########################################################
"""
Eligibility/clinical characteristics flag for study population denominator:
- include_patient_otitis_media
- include_patient_sinusitis
- include_patient_sore_throat
- include_patient_insect_bites
- include_patient_shingles
- include_patient_impetigo
- include_patient_uti
- include_patient_overall_eligible

"""

# [to-review] Condition: acute otitis media
# - inclusion: children aged 1 to 17 years
# - exclusion: none
include_patient_otitis_media = (age >= 1) & (age <= 17) 
dataset.include_patient_otitis_media = include_patient_otitis_media
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: acute sinusitis
# - inclusion: age >= 12
# - exclusion: none
include_patient_sinusitis = (age >= 12)
dataset.include_patient_sinusitis = include_patient_sinusitis
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: acute sore throat
# - inclusion: age >= 5
# - exclusion: pregnant individuals under 16s
age_eligible_sore_throat = (age >= 5)
exclusion_sore_throat = pregnant_this_month & (age < 16)
include_patient_sore_throat = (age_eligible_sore_throat & ~exclusion_sore_throat)
dataset.include_patient_sore_throat = include_patient_sore_throat
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: infected insect bites
# - inclusion: age >= 1
# - exclusion: pregnant individuals under 16s
age_eligible_insect_bites = (age >= 1) # To confirm with Helen: any age < 1?
exclusion_insect_bites = pregnant_this_month & (age < 16)
include_patient_insect_bites = (age_eligible_insect_bites & ~exclusion_insect_bites)
dataset.include_patient_insect_bites = include_patient_insect_bites
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: shingles
# - inclusion: age >= 18
# - exclusion: pregnant individuals
age_eligible_shingles = (age >= 18)
exclusion_shingles = pregnant_this_month
include_patient_shingles = (age_eligible_shingles & ~exclusion_shingles)
dataset.include_patient_shingles = include_patient_shingles
# show(dataset) # DEBUG: show the patients in the base population


# [] Condition: impetigo
# - inclusion: age >= 1
# - exclusion: 
# - - bullous impetigo, 
# - - recurrent impetigo (defined as 2 or more episodes in the same year), 
# - - pregnant individuals under 16 years
impetigo_age_eligible = (age >= 1)
impetigo_exclusion = (bullous_impetigo_this_month | recurrent_impetigo_this_year | (pregnant_this_month & (age < 16)))
include_patient_impetigo = (impetigo_age_eligible & ~impetigo_exclusion)
dataset.include_patient_impetigo = include_patient_impetigo
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug


# [] Condition: Uncomplicated UTI
# - inclusion: women aged 16 to 64 years
# - exclusion: 
# - - pregnant individuals
# - - urinary catheter
# - - recurrent UTI: 2 episodes in last 6 months, or 3 episodes in last 12 months
uuti_eligible = (age >= 16) & (age <= 64) & (patients.sex.is_in(["female"]))
uuti_exclusion = (pregnant_this_month | catheter_status | recurrent_uti)
include_patient_uuti = (uuti_eligible & ~uuti_exclusion)
dataset.include_patient_uuti = include_patient_uuti
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug


# include_patient_all_conditions
include_patient_overall_eligible = (include_patient_otitis_media|include_patient_sinusitis
                                  |include_patient_sore_throat|include_patient_insect_bites
                                  |include_patient_shingles|include_patient_impetigo|include_patient_uuti)
dataset.include_patient_overall_eligible = include_patient_overall_eligible
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug

########################################################

show(dataset) # DEBUG: show the patients in the base population