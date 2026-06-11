from ehrql import codelist_from_csv

 ####################################################
#Here i will add a codelist for medication and conditions for P4 : airadukunda
# Additional variables on medication (specific antimicrobial for the P4).For medicine we fir need to make sure if the fx  codelist_from_csv is colled at the begining as: 
#from ehrql import create_dataset, codelist_from_csv ( read the Using ehrQL to answer specific questions in OS documentation)
#a.Treatment for PF conditions 
aciclovir_codelist = codelist_from_csv("codelists/pharmacy-first-project-aciclovir.csv", column="code")
amoxicillin_codelist = codelist_from_csv("codelists/pharmacy-first-project-amoxicillin.csv", column="code")
cefalexin_codelist = codelist_from_csv("codelists/pharmacy-first-project-cefalexin.csv", column="code")
clarithromycin_codelist = codelist_from_csv("codelists/pharmacy-first-project-clarithromycin.csv", column="code")
clindamycin_codelist = codelist_from_csv("codelists/pharmacy-first-project-clindamycin.csv", column="code")
co_amoxiclav_codelist = codelist_from_csv("codelists/pharmacy-first-project-co-amoxiclav-oral-preparations.csv", column="code")
doxycycline_codelist = codelist_from_csv("codelists/pharmacy-first-project-doxycycline.csv", column="code")
erythromycin_codelist = codelist_from_csv("codelists/pharmacy-first-project-erythromycin.csv", column="code")
famciclovir_codelist = codelist_from_csv("codelists/pharmacy-first-project-famciclovir.csv", column="code")
flucloxacillin_codelist = codelist_from_csv("codelists/pharmacy-first-project-flucloxacillin.csv", column="code")
fosfomycin_codelist = codelist_from_csv("codelists/pharmacy-first-project-fosfomycin.csv", column="code")
fusidic_acid_cream_codelist = codelist_from_csv("codelists/pharmacy-first-project-fusidic-acid-cream.csv", column="code")
metronidazole_codelist = codelist_from_csv("codelists/pharmacy-first-project-metronidazole.csv", column="code")
mupirocin_codelist = codelist_from_csv("codelists/pharmacy-first-project-mupirocin.csv", column="code")
nitrofurantoin_codelist = codelist_from_csv("codelists/pharmacy-first-project-nitrofurantoin.csv", column="code")
phenoxymethylpenicillin_codelist = codelist_from_csv("codelists/pharmacy-first-project-phenoxymethylpenicillin.csv", column="code")
pivmecillinam_codelist = codelist_from_csv("codelists/pharmacy-first-project-pivmecillinam.csv", column="code")
trimethoprim_codelist = codelist_from_csv("codelists/pharmacy-first-project-trimethoprim.csv", column="code")
valaciclovir_codelist = codelist_from_csv("codelists/pharmacy-first-project-valaciclovir.csv", column="code")
uti_codelist = codelist_from_csv("codelists/pharmacy-first-project-urinary-tract-infection-codes-for-pharmacy-first-clone.csv",column="code")
#PF conditions :airadukunda
# SNOMED UK ethnicity category codelist - latest version 22911876
ethnicity_group6_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6",
)
ethnicity_group16_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_16",
)

# consultation type -- pending update
gp_codelist_consultation_f2f = codelist_from_csv(
    "codelists/pharmacy-first-project-face-to-face-consultation-codes-for-pharmacy-first.csv",
    column="code"
)
gp_codelist_consultation_online = codelist_from_csv(
    "codelists/pharmacy-first-project-online-consultation-codes-for-pharmacy-first.csv",
    column="code"
)
gp_codelist_consultation_telephone = codelist_from_csv(
    "codelists/pharmacy-first-project-telephone-consultation-codes-for-pharmacy-first.csv",
    column="code"
)

#PF conditions snomed codes used within PF
tx_codelist_pf_otitis_media = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-acute-otitis-media-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_impetigo = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-impetigo-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_infected_insect_bites = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-infected-insect-bites-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_shingles = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-shingles-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_sinusitis = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sinusitis-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_sore_throat = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sore-throat-treatment-full-dmd-codelist.csv",
    column="code",
)
 
tx_codelist_pf_urinary_tract_infection = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-urinary-tract-infection-treatment-full-dmd-codelist.csv",
    column="code",
)

####################################################
#Snomed codes used for PF conditions by GPs
gp_snomed_codelist_uti = codelist_from_csv(
    "codelists/pharmacy-first-project-urinary-tract-infection-and-related-conditions.csv",
    column="code",
)  
gp_snomed_codelist_impetigo = codelist_from_csv(
    "codelists/pharmacy-first-project-impetigo-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
gp_snomed_codelist_otitis_media = codelist_from_csv(
    "codelists/pharmacy-first-project-otitis-media-and-related-conditions.csv",
    column="code",
) 
gp_snomed_codelist_sinusitis = codelist_from_csv(
    "codelists/pharmacy-first-project-sinusitis-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
gp_snomed_codelist_sore_throat = codelist_from_csv(
    "codelists/pharmacy-first-project-Sore-throat-and-related-conditions.csv",
    column="code",
) 
gp_snomed_codelist_insect_bites = codelist_from_csv(
    "codelists/pharmacy-first-project-insect-bites-and-related-conditions-administration-codes-for-pharmacy-first.csv",
    column="code",
) 
gp_snomed_codelist_shingles = codelist_from_csv(
    "codelists/pharmacy-first-project-shingles-and-related-conditions-for-pharmacy-first.csv",
    column="code",
)

####################################################
#Snomed codes used for control conditions by GPs
gp_snomed_codelist_lower_back_pain = codelist_from_csv(
    "codelists/pharmacy-first-project-lower-back-pain-for-pf-control.csv",
    column="code",
)


####################################################
#Snomed codes used for specific conditions by GPs - population exclusion criteria
gp_snomed_codelist_urinary_catheter = codelist_from_csv(
    "codelists/pharmacy-first-project-urinary-catheter-administration-codes-for-pharmacy-first.csv",
    column="code",
)

#Snomed codes used for specific conditions by GPs - population exclusion criteria
gp_snomed_codelist_bullous_impetigo = codelist_from_csv(
    "codelists/pharmacy-first-project-bullous-impetigo-administration-codes-for-pharmacy-first.csv",
    column="code",
)

#Snomed codes used for specific conditions by GPs - population exclusion criteria
#current version: pregnancy code by NHSD
gp_snomed_codelist_pregnancy = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-preg_cod.csv",
    column="code",
    category_column="term",
)

# Import no-longer-pregnant codelist
gp_snomed_codelist_end_pregnancy = codelist_from_csv(
    "codelists/pharmacy-first-project-end-of-pregnancy-narrow.csv",
    column="code",
    category_column="term",
)

# estimated date of delivery
gp_snomed_codelist_pregnancy_edd = codelist_from_csv (
    "codelists/user-VickiPalin-pregnancy_edd_snomed.csv"
    , column = "code"
)
####################################################
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
pf_consultation_cp_minorillness = ["1577041000000109"]
# Pharmacy First service - 983341000000102
pf_consultation_service = ["983341000000102"]
# Community Pharmacy First Service - 2129921000000100 - not used (?)
pf_consultation_cp_service = ["2129921000000100"]
 
pf_consultation_events_dict = {
    # "pf_consultation_cp_minorillness": pf_consultation_cp_minorillness, # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "pf_consultation_service": pf_consultation_service, # Pharmacy First service (qualifier value)
    "pf_consultation_cp_service": pf_consultation_cp_service, # Community Pharmacy Pharmacy First Service
    "pf_consultation_services_combined": pf_consultation_cp_minorillness + pf_consultation_service + pf_consultation_cp_service,
    # "pf_consultation_services_combined": pf_consultation_service + pf_consultation_cp_service,
}
 
uti_code = ["1090711000000102"]
sinusitis_code = ["15805002"]
insectbite_code = ["262550002"]
otitismedia_code = ["3110003"]
sorethroat_code = ["363746003"]
shingles_code = ["4740000"]
impetigo_code = ["48277006"]