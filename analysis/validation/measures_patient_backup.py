'''
This file defines measures around the patient population for sense checking and validate variable definitions.
The measures include:
- population by sex, region, IMD, ethinicity
- among all population, how many are eligible for PF
- among PF eligible population, how many had a PF consultation
- among all population, how many had a PF consultation

https://reports.opensafely.org/reports/opensafely-pharmacy-first-first-year-dashboard/
'''
from ehrql import case, create_measures, months, when
from analysis.dataset_definition_patients_measures import dataset
# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(1).starting_on("2025-10-01")
)
base = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

pf_eligible_population = (
    dataset.include_patient_overall_eligible
    & base
)

pf_consultation_population_eligible = (
    (dataset.pf_consultation_general > 0)
    & pf_eligible_population
)

pf_consultation_population_all = (
    (dataset.pf_consultation_general > 0)
    & base
)

age_band = case(
    when((dataset.age >= 0) & (dataset.age < 20)).then("0-19"),
    when((dataset.age >= 20) & (dataset.age < 40)).then("20-39"),
    when((dataset.age >= 40) & (dataset.age < 60)).then("40-59"),
    when((dataset.age >= 60) & (dataset.age < 80)).then("60-79"),
    when(dataset.age >= 80).then("80+"),
    when(dataset.age.is_null()).then("Missing"),
)

age_group = case(
    when(dataset.age < 5).then("0-4"),
    when(dataset.age < 16).then("5-15"),
    when(dataset.age < 20).then("16-19"),
    when(dataset.age < 45).then("20-44"),
    when(dataset.age < 65).then("45-64"),
    when(dataset.age < 80).then("65-79"),
    when(dataset.age >= 80).then("80+"),
    when(dataset.age.is_null()).then("Missing"),
)

# check base cohort size
measures.define_measure(
    name="population_by_sex",
    numerator=base,
    denominator=base,
    group_by = {"sex": dataset.sex},
)

measures.define_measure(
    name="population_by_region",
    numerator=base,
    denominator=base,
    group_by={"region": dataset.region},
)

measures.define_measure(
    name="population_by_imd",
    numerator=base,
    denominator=base,
    group_by={"imd": dataset.imd},
)

measures.define_measure(
    name="population_by_ethnicity",
    numerator=base,
    denominator=base,
    group_by={"ethnicity": dataset.ethnicity},
)

# check PF eligible population size from base cohort
measures.define_measure(
    name="pf_eligible_population_by_sex",
    numerator=pf_eligible_population,
    denominator=base,
    group_by={"sex": dataset.sex},
)
# check eligibility for each condition among the base population
# conditions include otitis_media, sinusitis, sore_throat, insect_bites, shingles, impetigo, uuti
measures.define_measure(
    name="pf_eligible_population_by_condition_otitis_media",
    numerator=dataset.include_patient_otitis_media,
    denominator=base,
    group_by = {"age_band": age_band}
)
measures.define_measure(
    name="pf_eligible_population_by_condition_sinusitis",
    numerator=dataset.include_patient_sinusitis,
    denominator=base,
    group_by = {"age_band": age_band}
)
measures.define_measure(
    name="pf_eligible_population_by_condition_sore_throat",
    numerator=dataset.include_patient_sore_throat,
    denominator=base,
    group_by = {"age_band": age_band}
)
measures.define_measure(
    name="pf_eligible_population_by_condition_insect_bites",
    numerator=dataset.include_patient_insect_bites,
    denominator=base,
    group_by = {"age_band": age_band}
)
measures.define_measure(
    name="pf_eligible_population_by_condition_shingles",
    numerator=dataset.include_patient_shingles,
    denominator=base,
    group_by = {"age_band": age_band}
)
measures.define_measure(
    name="pf_eligible_population_by_condition_impetigo",
    numerator=dataset.include_patient_impetigo,
    denominator=base,
    group_by = {"age_band": age_band}
)
measures.define_measure(
    name="pf_eligible_population_by_condition_uuti",
    numerator=dataset.include_patient_uuti,
    denominator=base,
    group_by = {"age_band": age_band, "sex": dataset.sex}
)

# among PF eligible population, check how many had a PF consultation
measures.define_measure(
    name="pf_eligible_population_with_consultation_by_sex",
    numerator=pf_consultation_population_eligible,
    denominator=pf_eligible_population,
    group_by={"sex": dataset.sex},
)

# among those had a PF consultation, how many are eligible for PF
measures.define_measure(
    name="pf_consultation_among_not_eligible_by_sex",
    numerator=(~pf_eligible_population),
    denominator=pf_consultation_population_all
)
