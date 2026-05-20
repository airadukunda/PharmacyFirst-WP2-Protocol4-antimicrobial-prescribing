from ehrql import case, create_measures, months, when
from analysis.dataset_definition_patients_measures import dataset
# opensafely exec ehrql:v1 generate-measures analysis/measures_patient.py --output output/measures_patient.csv

measures = create_measures()
measures.configure_disclosure_control(enabled=False)
measures.define_defaults(
    intervals=months(2).starting_on("2025-10-01"),
    # intervals=months(2).starting_on("2024-02-01")
)

measure_base_population = (
    dataset.alive
    & dataset.registered_start
    & dataset.registered_index
    & (dataset.age <= 120)
)

'''
Checks:
- For each condition:
  gp_consultation_<condition>_f2f
  + gp_consultation_<condition>_online
  + gp_consultation_<condition>_telephone
  + gp_consultation_<condition>_othermode
  should equal numerator_gp_consultation_<condition>.

- Across all conditions:
  sum(gp_consultation_<condition>_<mode>) can be compared with gp_pf_consultation_<mode>.
  If the condition-specific sum is larger, this suggests overlap between
  condition-specific GP consultation codelists.
'''
gp_modes = [
    "f2f",
    "online",
    "telephone",
    "othermode",
]

gp_conditions = [
    "uti",
    "sinusitis",
    "insectbite",
    "otitismedia",
    "sorethroat",
    "shingles",
    "impetigo",
]

# GP PF-related consultation counts by mode
for mode in gp_modes:
    measures.define_measure(
        name=f"gp_pf_consultation_{mode}",
        numerator=getattr(dataset, f"gp_pf_consultation_{mode}"),
        denominator=measure_base_population,
    )

for condition in gp_conditions:
    # Total GP consultation count for this condition
    measures.define_measure(
        name=f"gp_consultation_{condition}_total",
        numerator=getattr(dataset, f"numerator_gp_consultation_{condition}"),
        denominator=measure_base_population,
    )

    # GP consultation count by mode for this condition
    for mode in gp_modes:
        measures.define_measure(
            name=f"gp_consultation_{condition}_{mode}",
            numerator=getattr(dataset, f"gp_consultation_{condition}_{mode}"),
            denominator=measure_base_population,
        )