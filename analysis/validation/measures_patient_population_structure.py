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



# # # check practice size in base cohort
# # # should be the same as population_base_eligible but grouped by practice instead of region, in case there are missing practice codes in the dataset
# # # may be used to exclude practices with very small patient numbers from practice-level analyses
# # measures.define_measure(
# #     name="population_by_practice",
# #     numerator=measure_base_population,
# #     denominator=measure_base_population,
# #     group_by={
# #         "practice": dataset.practice
# #     },
# # )

# # check PF eligible population size from base cohort
# measures.define_measure(
#     name="pf_eligible_population_by_sex",
#     numerator=pf_eligible_population,
#     denominator=measure_base_population,
#     group_by={"sex": dataset.sex},
# )
# # check eligibility for each condition among the base population
# # conditions include otitis_media, sinusitis, sore_throat, insect_bites, shingles, impetigo, uuti
# measures.define_measure(
#     name="pf_eligible_population_by_condition_otitis_media",
#     numerator=dataset.include_patient_otitis_media & measure_base_population,
#     denominator=measure_base_population,
#     group_by = {"age_band": age_band}
# )
# measures.define_measure(
#     name="pf_eligible_population_by_condition_sinusitis",
#     numerator=dataset.include_patient_sinusitis & measure_base_population,
#     denominator=measure_base_population,
#     group_by = {"age_band": age_band}
# )
# measures.define_measure(
#     name="pf_eligible_population_by_condition_sore_throat",
#     numerator=dataset.include_patient_sore_throat & measure_base_population,
#     denominator=measure_base_population,
#     group_by = {"age_band": age_band}
# )
# measures.define_measure(
#     name="pf_eligible_population_by_condition_insect_bites",
#     numerator=dataset.include_patient_insect_bites & measure_base_population,
#     denominator=measure_base_population,
#     group_by = {"age_band": age_band}
# )
# measures.define_measure(
#     name="pf_eligible_population_by_condition_shingles",
#     numerator=dataset.include_patient_shingles & measure_base_population,
#     denominator=measure_base_population,
#     group_by = {"age_band": age_band}
# )
# measures.define_measure(
#     name="pf_eligible_population_by_condition_impetigo",
#     numerator=dataset.include_patient_impetigo & measure_base_population,
#     denominator=measure_base_population,
#     group_by = {"age_band": age_band}
# )
# measures.define_measure(
#     name="pf_eligible_population_by_condition_uuti",
#     numerator=dataset.include_patient_uuti & measure_base_population,
#     denominator=measure_base_population,
#     group_by = {"age_band": age_band, "sex": dataset.sex}
# )

# # among PF eligible population, check how many had a PF consultation
# measures.define_measure(
#     name="pf_eligible_population_with_consultation_by_sex",
#     numerator=pf_consultation_population_eligible,
#     denominator=pf_eligible_population,
#     group_by={"sex": dataset.sex},
# )

# # among those had a PF consultation, how many are eligible for PF
# measures.define_measure(
#     name="pf_consultation_among_not_eligible_by_sex",
#     numerator=(
#         pf_consultation_population_all
#         & ~pf_eligible_population
#     ),
#     denominator=pf_consultation_population_all
# )
