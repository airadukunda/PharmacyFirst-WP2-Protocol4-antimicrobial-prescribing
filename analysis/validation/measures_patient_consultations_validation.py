from ehrql import case, create_measures, months, when
from analysis.dataset_definition_patients_measures import dataset
# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(2).starting_on("2025-10-01"),
    # intervals=years(2).starting_on("2024-02-01")
)

measure_base_population = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

pf_eligible_population = (
    dataset.include_patient_overall_eligible
    & measure_base_population
)

pf_user_population = (
    (dataset.pf_consultation_general > 0)
    & measure_base_population
)

age_band = case(
    when((dataset.age >= 0) & (dataset.age < 20)).then("0-19"),
    when((dataset.age >= 20) & (dataset.age < 40)).then("20-39"),
    when((dataset.age >= 40) & (dataset.age < 60)).then("40-59"),
    when((dataset.age >= 60) & (dataset.age < 80)).then("60-79"),
    when(dataset.age >= 80).then("80+"),
    when(dataset.age.is_null()).then("Missing"),
)

'''
1. Check whether PF consultation counts broken down by condition sum to the corresponding total number of consultations:
- pf_consultation_general: total number of consultations with PF service codes
- pf_consultation_general_butno_condition: number of consultations with PF service codes but no associated condition code
- numerator_pf_consultation_<condition>: number of consultations with PF service codes AND a specific PF condition code (e.g. UTI, sinusitis, insect bite, otitis media, sore throat, shingles, impetigo)

-> Validation check: The sum of consultations across all conditions should equal:
  sum(numerator_pf_consultation_{condition}) = pf_consultation_general − pf_consultation_general_butno_condition
  This assumes that each consultation is assigned to at most one PF condition.



GP consultation count:
- numerator_gp_consultation_{condition}: number of condition-related GP consultations
- gp_consultation_{condition}_{mode}: number of condition-related GP consultations broken down by consultation mode
-> Validation check: For one {condition} e.g., uti:
        numerator_gp_consultation_uti = gp_consultation_uti_f2f + gp_consultation_uti_online + gp_consultation_uti_telephone + gp_consultation_uti_othermode

- gp_pf_consultation_f2f: number of PF condition-related GP consultations with f2f consultation mode
-> Validation check: gp_pf_consultation_f2f = sum(gp_consultation_{condition}_f2f)

'''