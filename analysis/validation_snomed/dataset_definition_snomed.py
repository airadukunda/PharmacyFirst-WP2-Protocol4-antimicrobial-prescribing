# analysis/dataset_definition_snomed_validation.py
# opensafely run generate_dataset_snomed_count
# gunzip -c output/dataset_patients_snomed.csv.gz > output/dataset_patients_snomed.csv

from ehrql import create_dataset, get_parameter, INTERVAL, days, months, show, case, when
from ehrql.tables.tpp import (patients, practice_registrations, clinical_events)
import analysis.codelists as codelists
from analysis.pf_variable_library import (select_events_between, select_events_from_codelist)

dataset = create_dataset()
dataset.configure_dummy_data(population_size=500)

start_date = get_parameter("start_date", default="2024-02-01")
index_date = start_date + months(1) - days(1)

# start_date = INTERVAL.start_date    
# index_date = INTERVAL.end_date

'''
This work aims to examine coding patterns within GP consultations related to PF conditions, 
excluding consultations classified as PF consultations. 

For each PF condition, consultations are identified using the corresponding PF-condition-specific SNOMED codelists. 
Within these GP consultations, the frequency of each SNOMED code from the same condition-specific codelist is quantified by 
counting the number of unique consultations (consultation_id) in which the code appears.

Detailed approach
1. Use the existing PF-condition-specific SNOMED codelists to identify consultations related to each PF condition (e.g. UTI, sore throat, sinusitis) 
    ---> PF-condition-related consultations
2. Exclude consultations already classified as PF consultations. Restrict the analysis to remaining GP consultations related to the PF condition.
    ---> updated PF-condition-related consultations
3. For each PF condition,
    For each SNOMED code within the same condition-specific codelist, 
        calculate the number of unique consultations (consultation_id) in which the code appears.

The resulting dataset:
- each row representing an individual patient;
- each column representing the count of a specific SNOMED code.
'''
#----------------------------------------
# Patient identifiers: alive_status, registration_status, age
alive = patients.is_alive_on(index_date) # alive at the end of month
# Only include the patient if they were registered for the whole month, 
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()
# Exclude any patients over 120 years old as the date of birth is most likely to be missing
age = patients.age_on(index_date)
age_valid = (patients.age_on(index_date) <= 120) 

base_population = alive & registered_start & registered_index & age_valid 
dataset.define_population(base_population)

dataset.start_date = case(when(base_population).then(start_date))
dataset.index_date = case(when(base_population).then(index_date))

#----------------------------------------
selected_events = select_events_between(clinical_events, start_date, index_date)

# PF consultation ids
pf_consultation_events = select_events_from_codelist(selected_events, codelists.pf_consultation_events_dict["pf_consultation_services_combined"])
pf_ids = pf_consultation_events.consultation_id

# GP consultation events excluding PF consultations
gp_events_clean = selected_events.where(~selected_events.consultation_id.is_in(pf_ids))

# codelists for PF conditions - long version
pf_gp_codelists = {
    "uti": codelists.gp_snomed_codelist_uti,
    "sinusitis": codelists.gp_snomed_codelist_sinusitis,
    "insectbite": codelists.gp_snomed_codelist_insect_bites,
    "otitismedia": codelists.gp_snomed_codelist_otitis_media,
    "sorethroat": codelists.gp_snomed_codelist_sore_throat,
    "shingles": codelists.gp_snomed_codelist_shingles,
    "impetigo": codelists.gp_snomed_codelist_impetigo,
}

condition = get_parameter("condition", default="sorethroat")
codes = pf_gp_codelists[condition]

for code in codes:

    code_events = gp_events_clean.where(gp_events_clean.snomedct_code == code)

    dataset.add_column(
        f"count_{code}",
        code_events.consultation_id.count_distinct_for_patient(),
    )

show(dataset)
