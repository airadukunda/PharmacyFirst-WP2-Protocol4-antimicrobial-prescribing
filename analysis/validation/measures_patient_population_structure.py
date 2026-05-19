'''
This file defines measures around the patient population for sense checking.
Two population groups: 
(1) patients with at least one PF service code recorded during the month
(2) the total registered patient population in the same month

For both populations, breakdowns are produced by key demographic characteristics 
(e.g. sex, age group, ethnicity, IMD, and region). 
These summaries are intended to support comparisons with Table 1 reported in the paper:
Kingsley, Viveck J., et al. "Recording of Pharmacy First consultations in general practice records in England: an observational study of the service's first year using OpenSAFELY." medRxiv (2025): 2025-09.
'''
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

# National population structure
measures.define_measure(
    name="population_by_sex",
    numerator=pf_user_population,
    denominator=measure_base_population,
    group_by={"sex": dataset.sex},
)

measures.define_measure(
    name="population_by_age",
    numerator=pf_user_population,
    denominator=measure_base_population,
    group_by={"age_band": age_band},
)

measures.define_measure(
    name="population_by_ethnicity",
    numerator=pf_user_population,
    denominator=measure_base_population,
    group_by={"ethnicity": dataset.ethnicity},
)

measures.define_measure(
    name="population_by_imd",
    numerator=pf_user_population,
    denominator=measure_base_population,
    group_by={"imd": dataset.imd},
)

measures.define_measure(
    name="population_by_region",
    numerator=pf_user_population,
    denominator=measure_base_population,
    group_by={"region": dataset.region},
)
