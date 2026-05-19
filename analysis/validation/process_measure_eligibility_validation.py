# Condition: acute otitis media
# - inclusion: children aged 1 to 17 years
# - exclusion: none

# Condition: acute sinusitis
# - inclusion: age >= 12
# - exclusion: none

# Condition: acute sore throat
# - inclusion: age >= 5
# - exclusion: pregnant individuals under 16s

# Condition: infected insect bites
# - inclusion: age >= 1
# - exclusion: pregnant individuals under 16s

# Condition: shingles
# - inclusion: age >= 18
# - exclusion: pregnant individuals

# Condition: impetigo
# - inclusion: age >= 1
# - exclusion: 
# - - bullous impetigo, 
# - - recurrent impetigo (defined as 2 or more episodes in the same year), 
# - - pregnant individuals under 16 years

# Condition: Uncomplicated UTI
# - inclusion: women aged 16 to 64 years
# - exclusion: 
# - - pregnant individuals
# - - urinary catheter
# - - recurrent UTI: 2 episodes in last 6 months, or 3 episodes in last 12 months

import pandas as pd

input_file = "output/patient_measures_eligibility_validation.csv"
output_file = "output/patient_measures_eligibility_validation_ordered.csv"

df = pd.read_csv(input_file)

measure_order = [
    # Pregnancy-related
    "base_pop_pregnancy_category",
    "pregnant_by_sex",

    # Impetigo-related
    "base_pop_bullous_impetigo",
    "base_pop_recurrent_impetigo",
    "base_pop_bullous_and_recurrent_impetigo",
    "pf_impetigo_eligible_among_base",
    "pf_impetigo_excluded_due_to_bullous",
    "pf_impetigo_excluded_due_to_recurrent",
    "pf_impetigo_excluded_due_to_pregnant_under16",

    # UTI-related
    "base_pop_catheter_status",
    "base_pop_recurrent_uti_6m",
    "base_pop_recurrent_uti_12m",
    "base_pop_recurrent_uti",
    "pf_uti_eligible_among_base",
    "pf_uti_excluded_due_to_age_sex",
    "pf_uti_excluded_due_to_pregnancy",
    "pf_uti_excluded_due_to_catheter",
    "pf_uti_excluded_due_to_recurrent_uti",

    # Otitis media
    "pf_otitis_media_eligible_among_base",

    # Sinusitis
    "pf_sinusitis_eligible_among_base",

    # Sore throat
    "pf_sore_throat_eligible_among_base",
    "pf_sore_throat_excluded_due_to_age_under5",
    "pf_sore_throat_excluded_due_to_pregnant_under16",

    # Insect bites
    "pf_insect_bite_eligible_among_base",

    # Shingles
    "pf_shingles_eligible_among_base",
    "pf_shingles_excluded_due_to_age_under18",
    "pf_shingles_excluded_due_to_pregnancy",

    # Overall eligible
    "pf_overall_eligible_among_base",
]

df["measure_order"] = df["measure"].apply(
    lambda x: measure_order.index(x) if x in measure_order else 999
)

sort_cols = ["measure_order", "measure", "interval_start"]

if "sex" in df.columns:
    sort_cols.append("sex")

if "age_band" in df.columns:
    sort_cols.append("age_band")

if "pregnant" in df.columns:
    sort_cols.append("pregnant")

df = df.sort_values(sort_cols).drop(columns=["measure_order"])

df.to_csv(output_file, index=False)

print(f"Saved ordered measures to {output_file}")