from ehrql import case, create_measures, months, when
from analysis.dataset_definition_patients_measures import dataset

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(1).starting_on("2025-10-01"),
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

age_band_naive = case(
    when(dataset.age < 16).then("<16"),
    when((dataset.age >= 16) & (dataset.age <= 64)).then("16-64"),
    when(dataset.age > 64).then("65+"),
    when(dataset.age.is_null()).then("Missing"),
)

'''
pregancy-related: overall, by sex and age band
Checks:
- any records with sex == "unknown"?
- any pregnancy records among males?
- any pregnancy records among patients aged ≤16 years?
'''
measures.define_measure(
    name="base_pop_pregnancy_category",
    numerator=dataset.pregnant_this_month,
    denominator=measure_base_population,
    group_by={"pregnant": dataset.pregnant},
)
measures.define_measure(
    name="pregnant_by_sex",
    numerator=dataset.pregnant_this_month,
    denominator=measure_base_population,
    group_by={"sex": dataset.sex, "age_band": age_band_naive},
)

'''
impetigo-related
Checks:
- Bullous impetigo and recurrent impetigo should both be rare in the base population.
- The overlap between bullous and recurrent impetigo should also be very small.
- include_patient_impetigo should mainly reflect majority of patients.
- Among patients excluded from include_patient_impetigo, check the exclusion reasons (may overlap so their proportions do not need to sum to 100%).
'''
measures.define_measure(
    name="base_pop_bullous_impetigo",
    numerator=dataset.bullous_impetigo_this_month,
    denominator=measure_base_population,
)
measures.define_measure(
    name="base_pop_recurrent_impetigo",
    numerator=dataset.recurrent_impetigo_this_year,
    denominator=measure_base_population,
)
measures.define_measure(
    name="base_pop_bullous_and_recurrent_impetigo",
    numerator=dataset.bullous_impetigo_this_month & dataset.recurrent_impetigo_this_year,
    denominator=measure_base_population,
)
measures.define_measure(
    name="pf_impetigo_eligible_among_base",
    numerator=dataset.include_patient_impetigo,
    denominator=measure_base_population,
)
pf_impetigo_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_impetigo
)
measures.define_measure(
    name="pf_impetigo_excluded_due_to_bullous",
    numerator=dataset.bullous_impetigo_this_month,
    denominator=pf_impetigo_excluded_population,
)
measures.define_measure(
    name="pf_impetigo_excluded_due_to_recurrent",
    numerator=dataset.recurrent_impetigo_this_year,
    denominator=pf_impetigo_excluded_population,
)
measures.define_measure(
    name="pf_impetigo_excluded_due_to_pregnant_under16",
    numerator=(
        dataset.pregnant_this_month
        & (dataset.age < 16)
    ),
    denominator=pf_impetigo_excluded_population,
)


'''
UTI-related checks:
- catheter_status, recurrent_uti_6m, recurrent_uti_12m, and recurrent_uti should be relatively uncommon in the base population.
- recurrent_uti should be greater than or equal to both recurrent_uti_6m and recurrent_uti_12m.
- include_patient_uuti should only appear among females aged 16–64.
- Among patients not included in UTI eligibility, check the exclusion reasons - may overlap, so proportions do not need to sum to 100%.
'''
measures.define_measure(
    name="base_pop_catheter_status",
    numerator=dataset.catheter_status,
    denominator=measure_base_population,
)
measures.define_measure(
    name="base_pop_recurrent_uti_6m",
    numerator=dataset.recurrent_uti_6m,
    denominator=measure_base_population,
)
measures.define_measure(
    name="base_pop_recurrent_uti_12m",
    numerator=dataset.recurrent_uti_12m,
    denominator=measure_base_population,
)
measures.define_measure(
    name="base_pop_recurrent_uti",
    numerator=dataset.recurrent_uti,
    denominator=measure_base_population,
)
measures.define_measure(
    name="pf_uti_eligible_among_base",
    numerator=dataset.include_patient_uuti,
    denominator=measure_base_population,
    group_by={"sex": dataset.sex, "age_band": age_band_naive},
)
pf_uuti_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_uuti
)
measures.define_measure(
    name="pf_uti_excluded_due_to_age_sex",
    numerator=((dataset.sex == "male")|(dataset.age<16)|(dataset.age>64)),
    denominator=pf_uuti_excluded_population,
)
measures.define_measure(
    name="pf_uti_excluded_due_to_pregnancy",
    numerator=dataset.pregnant_this_month,
    denominator=pf_uuti_excluded_population,
)
measures.define_measure(
    name="pf_uti_excluded_due_to_catheter",
    numerator=dataset.catheter_status,
    denominator=pf_uuti_excluded_population,
)
measures.define_measure(
    name="pf_uti_excluded_due_to_recurrent_uti",
    numerator=dataset.recurrent_uti,
    denominator=pf_uuti_excluded_population,
)

# PF otitis media eligible: eligible population age range >=16 should be close to zero
measures.define_measure(
    name="pf_otitis_media_eligible_among_base",
    numerator=dataset.include_patient_otitis_media,
    denominator=measure_base_population,
    group_by={"age_band": age_band_naive},
)

# PF sinusitis eligible: eligible population age range <16 should be close to zero
measures.define_measure(
    name="pf_sinusitis_eligible_among_base",
    numerator=dataset.include_patient_sinusitis,
    denominator=measure_base_population,
    group_by={"age_band": age_band_naive},
)

# PF sore throat eligible
measures.define_measure(
    name="pf_sore_throat_eligible_among_base",
    numerator=dataset.include_patient_sore_throat,
    denominator=measure_base_population,
)
sore_throat_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_sore_throat
)
measures.define_measure(
    name="pf_sore_throat_excluded_due_to_age_under5",
    numerator=(dataset.age < 5),
    denominator=sore_throat_excluded_population,
)
measures.define_measure(
    name="pf_sore_throat_excluded_due_to_pregnant_under16",
    numerator=(dataset.pregnant_this_month & (dataset.age < 16)),
    denominator=sore_throat_excluded_population,
)

# PF infected insect bites eligible
measures.define_measure(
    name="pf_insect_bite_eligible_among_base",
    numerator=dataset.include_patient_insect_bites,
    denominator=measure_base_population,
)

# PF shingle eligible
measures.define_measure(
    name="pf_shingles_eligible_among_base",
    numerator=dataset.include_patient_shingles,
    denominator=measure_base_population,
    group_by={"age_band": age_band_naive},
)
shingles_excluded_population = (
    measure_base_population
    & ~dataset.include_patient_shingles
)
measures.define_measure(
    name="pf_shingles_excluded_due_to_age_under18",
    numerator=(dataset.age < 18),
    denominator=shingles_excluded_population,
)
measures.define_measure(
    name="pf_shingles_excluded_due_to_pregnancy",
    numerator=dataset.pregnant_this_month,
    denominator=shingles_excluded_population,
)

# include_patient_overall_eligible
measures.define_measure(
    name="pf_overall_eligible_among_base",
    numerator=dataset.include_patient_overall_eligible,
    denominator=measure_base_population,
    group_by={"age_band": age_band_naive},
)
