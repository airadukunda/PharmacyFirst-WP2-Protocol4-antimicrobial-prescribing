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
# flags: pregnancy_status, ... 
# conditions: acute otitis media, acute sore throat, ...


# Condition: acute otitis media (aom)
# - inclusion: children aged 1 to 17 years
# - exclusion: none
aom_age_eligible = (age >= 1) & (age <= 17)
dataset.aom_age_eligible = aom_age_eligible # DEBUG

include_patient_aom = aom_age_eligible
dataset.include_patient_aom = include_patient_aom
# show(dataset) # DEBUG: show the patients in the base population


# Flag: pregnancy_status
from analysis.pf_variable_library import check_pregnancy_status
pregnant_this_month = check_pregnancy_status(index_date, clinical_events, codelists.pregnancy_codelist) # To confirm with Helen
# pregnant_this_month = False
dataset.pregnant_this_month = pregnant_this_month
# show(dataset) # DEBUG: show the patients in the base population


# Condition: acute sore throat (ast)
# - inclusion: age >= 5
# - exclusion: pregnant individuals under 16s
ast_age_eligible = (age >= 5)
ast_exclusion = pregnant_this_month & (age < 16)
dataset.ast_age_eligible = ast_age_eligible # DEBUG
dataset.ast_exclusion = ast_exclusion # DEBUG

include_patient_ast = (ast_age_eligible & ~ast_exclusion)
dataset.include_patient_ast = include_patient_ast
show(dataset) # DEBUG: show the patients in the base population


# condition-related fields
# pregnancy: assume we have it and NotImplemented
# bullous impetigo: might be recorded wrongly, implement and see whether there are excluding the wrong patients
# urinary catheter, and urinary infection

# impetigo, uti


# pregnant_this_month = ...

# include_uti = (
#     base_population
#     & (sex == "female")
#     & (age >= 16)
#     & (age <= 64)
#     & ~pregnant_this_month
#     & ~recurrent_uti
# )

# dataset.Include_patient_UTI = include_uti

########################################################





########################################################
# Numerator - 




########################################################





########################################################
# Covariate - 




########################################################