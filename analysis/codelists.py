from ehrql import codelist_from_csv
 
# Import pharmacy first conditions codelist
pf_conditions_codelist = codelist_from_csv(
    "codelists/user-chriswood-pharmacy-first-clinical-pathway-conditions.csv",
    column="code",
    category_column="term",
)
 
# Import ethnicity codelist
ethnicity_group6_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="snomedcode",
    category_column="Grouping_6",
)
 
# Import ethnicity codelist
ethnicity_group16_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="snomedcode",
    category_column="Grouping_16",
)
#PF conditions snomed codes used within PF
acute_otitis_media_tx_codelist = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-acute-otitis-media-treatment-full-dmd-codelist.csv",
    column="code",
)
 
impetigo_treatment_tx_codelist = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-impetigo-treatment-full-dmd-codelist.csv",
    column="code",
)
 
infected_insect_bites_tx_codelist = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-infected-insect-bites-treatment-full-dmd-codelist.csv",
    column="code",
)
 
shingles_treatment_tx_codelist = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-shingles-treatment-full-dmd-codelist.csv",
    column="code",
)
 
sinusitis_tx_codelist = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sinusitis-treatment-full-dmd-codelist.csv",
    column="code",
)
 
sore_throat_tx_codelist = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sore-throat-treatment-full-dmd-codelist.csv",
    column="code",
)
 
urinary_tract_infection_tx_codelist = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-urinary-tract-infection-treatment-full-dmd-codelist.csv",
    column="code",
)
#Snomed codes for exclusion criteria
Urinary_catheter_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-urinary-catheter-administration-codes-for-pharmacy-first.csv",
    column="code",
)
    # Import pregnancy codelist
pregnancy_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-preg_cod.csv",
    column="code",
    category_column="term",
)
bullous_impetigo_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-bullous-impetigo-administration-codes-for-pharmacy-first.csv",
    column="code",
)
#Snomed codes used for PF conditions by GPs
GP_UTI_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions.csv",
    column="code",
)  
GP_impetigo_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-impetigo-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
GP_sore_throat_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-Sore-throat-and-related-conditions.csv",
    column="code",
) 
GP_sinusitis_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-sinusitis-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
GP_otitis_media_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-otitis-media-and-related-conditions.csv",
    column="code",
) 
GP_insect_bites_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-insect-bites-and-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
GP_shingles_tx_codelist = codelist_from_csv(
    "codelists/pharmacy-first-project-shingles-and-related-conditions-for-pharmacy-first.csv",
    column="code",
) 
"""
pf_med_codelist = (
    acute_otitis_media_tx_codelist
    + impetigo_treatment_tx_codelist
    + infected_insect_bites_tx_codelist
    + shingles_treatment_tx_codelist
    + sinusitis_tx_codelist
    + sore_throat_tx_codelist
    + urinary_tract_infection_tx_codelist
)
"""
# Community Pharmacist Consultation Service for minor illness - 1577041000000109
# pf_consultation_cp_minorillness = ["1577041000000109"]
# Pharmacy First service - 983341000000102
pf_consultation_service = ["983341000000102"]
# Community Pharmacy First Service - 2129921000000100
pf_consultation_cp_service = ["2129921000000100"]
 
pf_consultation_events_dict = {
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
   # "pf_consultation_cp_minorillness": pf_consultation_cp_minorillness,
    # Pharmacy First service (qualifier value)
    "pf_consultation_service": pf_consultation_service,
    # Community Pharmacy Pharmacy First Service
    "pf_consultation_cp_service": pf_consultation_cp_service,
    "pf_consultation_services_combined": pf_consultation_service + pf_consultation_cp_service,
    # "pf_consultation_services_combined": pf_consultation_cp_minorillness + pf_consultation_service + pf_consultation_cp_service,
}
 
uti_code = ["1090711000000102"]
sinusitis_code = ["15805002"]
insectbite_code = ["262550002"]
otitismedia_code = ["3110003"]
sorethroat_code = ["363746003"]
shingles_code = ["4740000"]
impetigo_code = ["48277006"]

