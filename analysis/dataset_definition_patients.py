# This file defines the population and selects the fields that need to be included in the data for analysis. 
        
from ehrql import create_dataset, show
from ehrql.tables.tpp import (patients, practice_registrations, clinical_events,addresses,case,when)
import codelists

dataset = create_dataset()
dataset.configure_dummy_data(population_size=1000)

# One month time period (to start with this is Nov 25) 
start_date = "2025-10-31"     
index_date = "2025-11-30"  

########################################################
# Criteria for objective 1:
# during each monthly interval (between the start and index date), patients will be included if: 
# (1) alive & 
# (2) a registered patient &
# (3) apply to the condition-specific eligibility - age, sex, inclusion and exclusion criteria & ...
# to do when practice size is available: exclude practices which are unusual (e.g very small practices, so from practice list size) 
########################################################

########################################################
# Basics: sex, age, alive and registered
alive = patients.is_alive_on(index_date) # alive at the end of month
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient() # Question - registered at 'the end of month'?
base_population = patients.exists_for_patient()
# base_population = alive & registered_index

sex = patients.sex
age = patients.age_on(index_date)

dataset.sex = sex
dataset.age = age
dataset.alive = alive
dataset.registered_index = registered_index

dataset.define_population(base_population) # include all patients or the live and registered patients
# show(dataset) # DEBUG: show the patients in the base population
########################################################


########################################################
# Condition related flags
# - flags: pregnancy_status, ... 
# - conditions: acute otitis media, acute sore throat, ...


# [ ] Flag: pregnancy_status
from analysis.pf_variable_library import check_pregnancy_status
pregnant_this_month = check_pregnancy_status(index_date, clinical_events, codelists.pregnancy_codelist) # To confirm with Helen
# pregnant_this_month = (age < 0)
dataset.pregnant_this_month = pregnant_this_month
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug

# [ ] Flag: bullous_impetigo within 4 weeks
bullous_impetigo_this_month = (age < 0)
# from analysis.pf_variable_library import check_bullous_impetigo_status
# bullous_impetigo_this_month = check_bullous_impetigo_status(start_date,index_date,clinical_events,codelists.bullous_impetigo_code)
dataset.bullous_impetigo_this_month = bullous_impetigo_this_month
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug

# [ ] Flag: recurrent_impetigo: (defined as 2 or more episodes in the same year) 
# an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
# >= two 4-week-separated episodes
recurrent_impetigo_this_year = (age < 0)
# from analysis.pf_variable_library import check_recurrent_status
# recurrent_impetigo_this_year = check_recurrent_status(index_date, clinical_events, codelists.impetigo_codelist, lookback_months = 12, min_episodes = 2)
dataset.recurrent_impetigo_this_year = recurrent_impetigo_this_year
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug


# [ ] Flag: catheter_status: excluding patients who clearly have a catheter, and for following 12 months after code is included
catheter_status = (age < 0)
# from analysis.pf_variable_library import check_catheter_status
# catheter_status = check_catheter_status(index_date,clinical_events,codelists.urinary_catheter_codelist,lookback_months=12)
dataset.catheter_status = catheter_status
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug


# [ ] Flag: recurrent_uti: (2 episodes in last 6 months, or 3 episodes in last 12 months) an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
recurrent_6m = (age < 0)
recurrent_12m = (age < 0)
# recurrent_6m = check_recurrent_status(
#     index_date,clinical_events,codelists.uti_code,
#     lookback_months=6,min_episodes=2,
# )
# recurrent_12m = check_recurrent_status(
#     index_date,clinical_events,codelists.uti_code,
#     lookback_months=12,min_episodes=3,
# )
recurrent_uti = recurrent_6m | recurrent_12m
dataset.recurrent_uti = recurrent_uti
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug



# [to-review] Condition: acute otitis media (aom)
# - inclusion: children aged 1 to 17 years
# - exclusion: none
aom_age_eligible = (age >= 1) & (age <= 17)
# dataset.aom_age_eligible = aom_age_eligible # DEBUG
include_patient_aom = aom_age_eligible
dataset.include_patient_aom = include_patient_aom
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: acute sore throat (ast)
# - inclusion: age >= 5
# - exclusion: pregnant individuals under 16s
ast_age_eligible = (age >= 5)
ast_exclusion = pregnant_this_month & (age < 16)
# dataset.ast_age_eligible = ast_age_eligible # DEBUG
# dataset.ast_exclusion = ast_exclusion # DEBUG
include_patient_ast = (ast_age_eligible & ~ast_exclusion)
dataset.include_patient_ast = include_patient_ast
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: infected insect bites (iib)
# - inclusion: age >= 1
# - exclusion: pregnant individuals under 16s
iib_age_eligible = (age >= 1) # To confirm with Helen: any age < 1?
iib_exclusion = ast_exclusion
# dataset.iib_age_eligible = iib_age_eligible # DEBUG
# dataset.llb_exclusion = iib_exclusion # DEBUG
include_patients_iib = (iib_age_eligible & ~iib_exclusion)
dataset.include_patients_iib = include_patients_iib
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: acute sinusitis
# - inclusion: age >= 12
# - exclusion: none
sinustitis_age_eligible = (age >= 12)
# dataset.sinustitis_age_eligible = sinustitis_age_eligible
include_patients_sinustitis = sinustitis_age_eligible
dataset.include_patients_sinustitis = include_patients_sinustitis
# show(dataset) # DEBUG: show the patients in the base population


# [to-review] Condition: shingles
# - inclusion: age >= 18
# - exclusion: pregnant individuals
shingles_age_eligible = (age >= 18)
shingles_exclusion = pregnant_this_month
include_patients_shingles = (shingles_age_eligible & ~shingles_exclusion)
dataset.include_patients_shingles = include_patients_shingles
# show(dataset) # DEBUG: show the patients in the base population


# [ ] Condition: impetigo
# - inclusion: age >= 1
# - exclusion: 
# - - bullous impetigo, 
# - - recurrent impetigo (defined as 2 or more episodes in the same year), 
# - - pregnant individuals under 16 years
impetigo_age_eligible = (age >= 1)
impetigo_exclusion = (bullous_impetigo_this_month | recurrent_impetigo_this_year | (pregnant_this_month & (age < 16)))
include_patients_impetigo = (impetigo_age_eligible & ~impetigo_exclusion)
dataset.include_patients_impetigo = include_patients_impetigo
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug


# [ ] Condition: Uncomplicated UTI
# - inclusion: women aged 16 to 64 years
# - exclusion: 
# - - pregnant individuals
# - - urinary catheter
# - - recurrent UTI: 2 episodes in last 6 months, or 3 episodes in last 12 months
uuti_eligible = (age >= 16) & (age <= 64) & (patients.sex.is_in(["female"]))
uuti_exclusion = (pregnant_this_month | catheter_status | recurrent_6m | recurrent_12m)
include_patients_uuti = (uuti_eligible & ~uuti_exclusion)
dataset.include_patients_uuti = include_patients_uuti
# show(dataset) # DEBUG: show the patients in the base population
# Note: to incorporate codelist and debug

########################################################





########################################################
# Numerator - copied from dataset_definition.py
selected_events = clinical_events.where(clinical_events.date.is_on_or_between(start_date, index_date))
pf_consultation_events = selected_events.where(selected_events.snomedct_code.is_in(codelists.pf_consultation_events_dict["pf_consultation_services_combined"]))
dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = selected_events.where(selected_events.consultation_id.is_in(pf_ids))

def has_event(events, codelist):
    return events.where(events.snomedct_code.is_in(codelist)).exists_for_patient()

dataset.uti_numerator = has_event(selected_pf_id_events,codelists.uti_code)
dataset.sinusitis_numerator = has_event(selected_pf_id_events,codelists.sinusitis_code)
dataset.insectbite_numerator = has_event(selected_pf_id_events,codelists.insectbite_code)
dataset.otitismedia_numerator = has_event(selected_pf_id_events,codelists.otitismedia_code)
dataset.sorethroat_numerator = has_event(selected_pf_id_events,codelists.sorethroat_code)
dataset.shingles_numerator = has_event(selected_pf_id_events,codelists.shingles_code)
dataset.impetigo_numerator = has_event(selected_pf_id_events,codelists.impetigo_code)

########################################################





########################################################
# Covariate:
# - [] patient age, sex 
# - [] patient ethnicity
# - [] patient IMD
# - [] practice ID and size

# Covariate - patient IMD - copied from dataset_definition.py
def get_imd(addresses, index_date):
    imd_rounded = addresses.for_patient_on(index_date).imd_rounded
    max_imd = 32844
    imd_quintile = case(
        when((imd_rounded >= 0) & (imd_rounded < int(max_imd * 1 / 5))).then("1 (Most Deprived)"),
        when(imd_rounded < int(max_imd * 2 / 5)).then("2"),
        when(imd_rounded < int(max_imd * 3 / 5)).then("3"),
        when(imd_rounded < int(max_imd * 4 / 5)).then("4"),
        when(imd_rounded <= max_imd).then("5 (Least Deprived)"),
        otherwise="Missing",
    )
    return imd_quintile
 
dataset.imd = get_imd(addresses, index_date)


# Covariate - practice ID - copied from dataset_definition.py
dataset.practice = practice_registrations.for_patient_on(index_date).practice_pseudo_id

########################################################

show(dataset) # DEBUG: show the patients in the base population