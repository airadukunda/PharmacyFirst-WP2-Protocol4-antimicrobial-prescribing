# This file defines the population and selects the fields that need to be included in the data for analysis. 
# Get new dummy tables: opensafely exec ehrql:v1 create-dummy-tables analysis/dataset_definition_patients.py dummy_tables
# gunzip -c output/dataset_definition_patients.csv.gz > output/dataset_definition_patients.csv

from ehrql import create_dataset, show, days, weeks, months, years, case, when, get_parameter,codelist_from_csv # Here we added codelist_from_csv to be able to read csv codelist
# "tpp" : is the real dataset used in OpenSAFELY analyses.("core" is generic)
from ehrql.tables.tpp import (patients, practice_registrations, clinical_events, addresses, 
                              ethnicity_from_sus,
                              emergency_care_attendances,appointments,medications) # I added medications to be able to assing treatment to the dataset
import codelists

from analysis.pf_variable_library import (get_imd, get_latest_ethnicity, 
                                          select_events_between, select_events_from_codelist, select_events_by_consultation_id,
                                          has_event_count, ae_non_primary_diagnosis_matches)
from ehrql import claim_permissions
claim_permissions("appointments")

# call my codelists (medication,PF conditions and their controls)  from analysis/codelists.py                          # airadukunda 
from codelists import (
    # 1.PF medication (gp_dmd_codelist)
    aciclovir_codelist,
    amoxicillin_codelist,
    cefalexin_codelist,
    clindamycin_codelist,
    clarithromycin_codelist,
    co_amoxiclav_codelist,
    doxycycline_codelist,
    erythromycin_codelist,
    famciclovir_codelist,
    flucloxacillin_codelist,
    fosfomycin_codelist,
    fusidic_acid_cream_codelist,
    metronidazole_codelist,
    mupirocin_codelist,
    nitrofurantoin_codelist,
    phenoxymethylpenicillin_codelist,
    pivmecillinam_codelist,
    trimethoprim_codelist,
    valaciclovir_codelist,
    #2.PF control conditions (gp_snomed_codelist) :airadukunda
    acute_bronchitis_control_codelist,
    conjunctivitis_allergic_control_codelist,
    vulvovaginal_candidiasis_control_codelist,
    #3.PF conditions (gp_snomed_codelist) : airadukunda 
    impetigo_codelist,
    infected_insect_bites_codelist,
    otitis_media_codelist,
    shingles_codelist,
    sinusitis_codelist,
    sore_throat_codelist,
    uti_codelist
    )

dataset = create_dataset()
dataset.configure_dummy_data(population_size=100) # The size was increased from 500 to 1000 pop.airadukunda

# One month time period (to start with this is Nov 25) 
# start_date = "2025-10-31"     
# index_date = "2025-11-30"  
#start_date = get_parameter("start_date", default="2024-02-01")
start_date = get_parameter("start_date", default="2022-02-01") # 2 years before PF.airadukunda
index_date = start_date + months(1) - days(1)  # Here index_date means "last day of the month of start_date"
# index_date = start_date + years(1)

"""
Monthly patient-level denominator + numerator dataset
Patient table key fields:
- Patient identifiers: patient_id, month (start_date, index_date), registration_status, alive_status, practice_id, region, 
- Demographics: age, sex, ethnicity, IMD
- Appointment count: scheduled; seen.
- PF consultation count for each condition
- GP consultation count for each condition
- GP consultation for each condition, by consultation mode (f2f, online, telephone, other)
- Eligibility/clinical characteristics flag (True/False)

 Eligibility/clinical characteristics flag for study population denominator:
- include_patient_otitis_media
- include_patient_sinusitis
- include_patient_sore_throat
- include_patient_insect_bites
- include_patient_shingles
- include_patient_impetigo
- include_patient_uti
- include_patient_overall_eligible: at least one condition

The above variables require:
- pregnant_this_month: True/False, developed by Helen
- bullous_impetigo_this_month
- recurrent_impetigo_this_year
- catheter_status
- recurrent_uti

A&E variables:
- total number of A&E attendances in month based on arrival_date
- for each PF condition, using GP wider SNOMED codelists, create variables for:
    - count of A&E attendances with primary diagnosis (diagnosis_01) match to the condition-specific GP codelist
    - flag for any non-primary diagnosis (diagnosis_02-24) match to the condition-specific GP codelist (T/F)

Appointment variables:
- total number of appointments that were scheduled to date in month (based on start_date)
- total number of appointments that were seen in month (based on seen_date)
       
Notes: 
- may have patients not eligible but PF consultation
- should do consistent criteria for registration_status for practice dataset
- run for every month - specify parameters in .yaml
- include detailed flags for each condition's inclusion and exclusion (may be good to have)
"""

########################################################
# Patient identifiers: alive_status, registration_status
alive = patients.is_alive_on(index_date) # alive at the end of month
# Only include the patient if they were registered for the whole month, 
# so registered before the month starts and not deregistered or died during the month
registered_start = practice_registrations.for_patient_on(start_date).exists_for_patient()
registered_index = practice_registrations.for_patient_on(index_date).exists_for_patient()

# Demographics: sex, age, patient_imd
sex = patients.sex
age = patients.age_on(index_date)

# Define population
# base_population = patients.exists_for_patient()
age_valid = (patients.age_on(index_date) <= 120) # "Exclude any patients over 120 years old as the date of birth is most likely to be missing"
base_population = alive & registered_start & registered_index & age_valid 
dataset.define_population(base_population) # include all patients or those alive and registered

dataset.start_date = case(when(base_population).then(start_date))
dataset.index_date = case(when(base_population).then(index_date))

#Demographic variables 
dataset.registered_start = registered_start
dataset.registered_index = registered_index
dataset.alive = alive
dataset.sex = sex 
dataset.age = age
dataset.age_band = case(                         #Age band (15-49) for women.airadukunda
        when(age < 15).then("0-14"),
        when(age < 50).then("15-49"),
        when(age >= 50).then("50+"),
        otherwise="missing",
)
dataset.date_of_birth = patients.date_of_birth  # debug
dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(index_date,clinical_events,codelists.ethnicity_group16_codelist,ethnicity_from_sus,grouping=16,)
# Patient identifiers: practice_id, stp, region
dataset.practice = practice_registrations.for_patient_on(index_date).practice_pseudo_id
dataset.stp = practice_registrations.for_patient_on(index_date).practice_stp
# dataset.region = practice_registrations.for_patient_on(index_date).practice_nuts1_region_name
dataset.region = case(
    when(practice_registrations.for_patient_on(index_date).practice_nuts1_region_name.is_null()).then("Missing"),
    otherwise=practice_registrations.for_patient_on(index_date).practice_nuts1_region_name,
)
dataset.protocol = case(
    when(patients.exists_for_patient()).then("Protocol4"),
    otherwise="Protocol4",
)
# PF conditions and their medications
# We will need to have codelists for both 
# Attach medication to the dataset:I will need to add medications codelists in importation section at the bigning of the this data definition
# Here we can automate the code , to avoid repetitions.
dataset.medication = medications.exists_for_patient() # Has medication? 
#or
dataset.add_column("med", medications.exists_for_patient())
# Most recent medication date ?
dataset.medication_date = medications.sort_by(medications.date).last_for_patient().date
#Medication and condition between start and  index dates 
#a.On index date (time varying?)
#recent_medication = medications.where(medications.date == index_date)
#recent_clinical_event = clinical_events.where(clinical_events.date == index_date)
#b.Between two dates (start_date, index_date)
recent_medication = medications.where(medications.date.is_on_or_between(start_date , index_date))
recent_clinical_event = clinical_events.where(clinical_events.date.is_on_or_between(start_date,index_date))

#1.Urinary Tract Infections ((female, age 15–49)) 
#1.a.Clinical event
#  
female_15_49 = (
    (patients.sex == "female") &
    (patients.age_on(index_date) >= 15) &
    (patients.age_on(index_date) <= 49)
)
dataset.has_uti = (   # This code check if the clinical event happened between start and index date was uti 
    recent_clinical_event
    .where(clinical_events.snomedct_code.is_in(uti_codelist))
    .where(female_15_49)     #Inclusion and exclusion criteria
    .exists_for_patient()
    .as_int()
)

#1.b.Treatment  
#1.b.1.Nitrofurantoin 
dataset.nitrofurantoin_uti = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(nitrofurantoin_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
#1.b.2.Trimethoprim
dataset.trimethoprim_uti = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(trimethoprim_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
#1.b.3.fosfomycin
dataset.fosfomycin_uti = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(fosfomycin_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
#1.b.4.pivmecillinam
dataset.pivmecillinam_uti = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(pivmecillinam_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
#1.b.5.co-amoxiclav
dataset.co_amoxiclav_uti = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(co_amoxiclav_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
#1.b.6.cefelexin
dataset.cefalexin_uti = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(cefalexin_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
#1.b.7.Amoxicillin
dataset.amoxicillin_uti = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(amoxicillin_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
#1.c.all antimicrobials (we can sum all 1.b)

uti_all_treatment_codelist = (  # source : https://docs.opensafely.org/ehrql/how-to/codelists/
    nitrofurantoin_codelist
    + trimethoprim_codelist
    + fosfomycin_codelist
    + pivmecillinam_codelist
    + co_amoxiclav_codelist
    + cefalexin_codelist
    + amoxicillin_codelist
)

dataset.uti_all_treatment = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(uti_all_treatment_codelist))
    .where(female_15_49)
    .exists_for_patient()
    .as_int()
)
# count of the number of UTI antimicrobial categories prescribed : number of UTI antimicrobial categories prescribed
dataset.uti_treatment_count = (
    dataset.nitrofurantoin_uti
    + dataset.trimethoprim_uti
    + dataset.fosfomycin_uti
    + dataset.pivmecillinam_uti
    + dataset.co_amoxiclav_uti
    + dataset.cefalexin_uti
    + dataset.amoxicillin_uti
)
#Binary indicator for whether any UTI treatment was prescribed : 1 if any UTI antimicrobial was prescribed, otherwise 0
dataset.uti_treated = (
    (
        dataset.nitrofurantoin_uti
        + dataset.trimethoprim_uti
        + dataset.fosfomycin_uti
        + dataset.pivmecillinam_uti
        + dataset.co_amoxiclav_uti
        + dataset.cefalexin_uti
        + dataset.amoxicillin_uti
    ) > 0
).as_int()

#2.Impetigo
#2.a.Clinical event
dataset.has_impetigo = (  # This code check if the clinical event happened between start and  index date was uti (i will need to add inclusion and exclusion criteria)
    recent_clinical_event
    .where(clinical_events.snomedct_code.is_in(impetigo_codelist))
    .exists_for_patient()
    .as_int()
)
#2.b.Treatment 
#2.b.1. Fusidic_acid_cream
dataset.fusidic_acid_cream_impetigo = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(fusidic_acid_cream_codelist))
    .exists_for_patient()
    .as_int()
)
#2.b.2.Flucloxacillin
dataset.flucloxacillin_impetigo = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(flucloxacillin_codelist))
    .exists_for_patient()
    .as_int()
)

#2.b.3.Clarithromycin
dataset.clarithromycin_impetigo = (
    recent_medication

    .where(recent_medication.dmd_code.is_in(clarithromycin_codelist))
    .exists_for_patient()
    .as_int()
)
#2.b.4.Erythromycin
dataset.erythromycin_impetigo = (
    recent_medication

    .where(recent_medication.dmd_code.is_in(erythromycin_codelist))
    .exists_for_patient()
    .as_int()
)
#2.b.5.Mupirocin 2%
dataset.mupirocin_impetigo = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(mupirocin_codelist))
    .exists_for_patient()
    .as_int()
)
#2.c.All recommended impetigo treatments ( we can sum all the antimicrobial)

impetigo_all_treatment_codelist = (  #source : https://docs.opensafely.org/ehrql/how-to/codelists/
    fusidic_acid_cream_codelist
    + flucloxacillin_codelist
    + clarithromycin_codelist
    + erythromycin_codelist
    + mupirocin_codelist
)
#Any recommended impetigo antimicrobial was prescribed 
dataset.impetigo_all_treatment = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(impetigo_all_treatment_codelist))
    .exists_for_patient()
    .as_int()
)
#counting how many different impetigo treatments were prescribed on the index date
#number of treatment categories prescribed
dataset.impetigo_treatment_count = (     
    dataset.fusidic_acid_cream_impetigo
    + dataset.flucloxacillin_impetigo
    + dataset.clarithromycin_impetigo
    + dataset.erythromycin_impetigo
    + dataset.mupirocin_impetigo
)
#Impetigo treated :1 if any treatment was prescribed, 0 otherwise. 
dataset.impetigo_treated = (
    (
        dataset.fusidic_acid_cream_impetigo
        + dataset.flucloxacillin_impetigo
        + dataset.clarithromycin_impetigo
        + dataset.erythromycin_impetigo
        + dataset.mupirocin_impetigo
    ) > 0
).as_int()

#3. Insect bites 
#3.a.Clinical event
dataset.has_insecte_bite = (  # This code check if the clinical event happened between start and  index date was uti (i will need to add inclusion and exclusion criteria)
    recent_clinical_event
    .where(clinical_events.snomedct_code.is_in(infected_insect_bites_codelist))
    .exists_for_patient()
    .as_int()
)
#3.b.Treatment
#(Flucloxacillin/Clarithromycin/Erythromycin/Co-amoxiclav/Metronidazole/Clindamycin/Cefuroxime/Doxycycline)

#3.b.1.Flucloxacillin
dataset.flucloxacillin_insect_bite = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(flucloxacillin_codelist))
    .exists_for_patient()
    .as_int()
)

#3.b.2.Clarithromycin
dataset.clarithromycin_insect_bite = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(clarithromycin_codelist))
    .exists_for_patient()
    .as_int()
)

#3.b.3.Erythromycin
dataset.erythromycin_insect_bite = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(erythromycin_codelist))
    .exists_for_patient()
    .as_int()
)
#3.b.4.Co-amoxiclav
dataset.co_amoxiclav_insect_bite = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(co_amoxiclav_codelist))
    .exists_for_patient()
    .as_int()
)
#3.b.5.Metronidazole
dataset.metronidazole_insect_bite = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(metronidazole_codelist))
    .exists_for_patient()
    .as_int()
)
#3.b.6.Clindamycin
dataset.clindamycin_insect_bite = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(clindamycin_codelist))
    .exists_for_patient()
    .as_int()
)
#3.b.7.Doxycycline
dataset.doxycycline_insect_bite = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(doxycycline_codelist))
    .exists_for_patient()
    .as_int()
)
#3.c.All recommended insect bite treatments
insect_bite_all_treatment_codelist = ( #codelist combination : https://docs.opensafely.org/ehrql/how-to/codelists/
    flucloxacillin_codelist
    + clarithromycin_codelist
    + erythromycin_codelist
    + co_amoxiclav_codelist
    + metronidazole_codelist
    + clindamycin_codelist
    + doxycycline_codelist
)
# Any recommended insect bite antimicrobial was prescribed
dataset.insect_bite_all_treatment = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(insect_bite_all_treatment_codelist))
    .exists_for_patient()
    .as_int()
)
# Counting how many different treatment categories were prescribed
dataset.insect_bite_treatment_count = (
    dataset.flucloxacillin_insect_bite
    + dataset.clarithromycin_insect_bite
    + dataset.erythromycin_insect_bite
    + dataset.co_amoxiclav_insect_bite
    + dataset.metronidazole_insect_bite
    + dataset.clindamycin_insect_bite
    + dataset.doxycycline_insect_bite
)
# Insect bite treated: 1 if any recommended treatment was prescribed, 0 otherwise
dataset.insect_bite_treated = (
    (
        dataset.flucloxacillin_insect_bite
        + dataset.clarithromycin_insect_bite
        + dataset.erythromycin_insect_bite
        + dataset.co_amoxiclav_insect_bite
        + dataset.metronidazole_insect_bite
        + dataset.clindamycin_insect_bite
        + dataset.doxycycline_insect_bite
    ) > 0
).as_int()

#4.Otitis media 
#4.a.Clinical event 
dataset.has_otitis_media = (  # This code check if the clinical event happened between start and index date was uti 
    recent_clinical_event
    .where(clinical_events.snomedct_code.is_in(otitis_media_codelist))
    .exists_for_patient()
    .as_int()
)
#4.b.Treatment
# (Amoxicillin/Clarithromycin/Erythromycin/Co-amoxiclav)
#4.b.1.Amoxicillin
dataset.amoxicillin_otitis_media = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(amoxicillin_codelist))
    .exists_for_patient()
    .as_int()
)
#4.b.2.Clarithromycin
dataset.clarithromycin_otitis_media = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(clarithromycin_codelist))
    .exists_for_patient()
    .as_int()
)

#4.b.3.Erythromycin
dataset.erythromycin_otitis_media = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(erythromycin_codelist))
    .exists_for_patient()
    .as_int()
)

#4.b.4.Co-amoxiclav
dataset.co_amoxiclav_otitis_media = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(co_amoxiclav_codelist))
    .exists_for_patient()
    .as_int()
)

#4.c.All recommended otitis media treatments
otitis_media_all_treatment_codelist = (
    amoxicillin_codelist
    + clarithromycin_codelist
    + erythromycin_codelist
    + co_amoxiclav_codelist
)

# Any recommended otitis media antimicrobial was prescribed
dataset.otitis_media_all_treatment = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(otitis_media_all_treatment_codelist))
    .exists_for_patient()
    .as_int()
)

# Counting how many different treatment categories were prescribed
dataset.otitis_media_treatment_count = (
    dataset.amoxicillin_otitis_media
    + dataset.clarithromycin_otitis_media
    + dataset.erythromycin_otitis_media
    + dataset.co_amoxiclav_otitis_media
)
# Otitis media treated: 1 if any recommended treatment was prescribed, 0 otherwise
dataset.otitis_media_treated = (
    (
        dataset.amoxicillin_otitis_media
        + dataset.clarithromycin_otitis_media
        + dataset.erythromycin_otitis_media
        + dataset.co_amoxiclav_otitis_media
    ) > 0
).as_int()

#5.Shingles

#5.a.Clinical event
dataset.has_shingles = (
    recent_clinical_event
    .where(clinical_events.snomedct_code.is_in(shingles_codelist))
    .exists_for_patient()
    .as_int()
)

#5.b.Treatment
# (Aciclovir/Valaciclovir/Famciclovir)

#5.b.1.Aciclovir
dataset.aciclovir_shingles = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(aciclovir_codelist))
    .exists_for_patient()
    .as_int()
)

#5.b.2.Valaciclovir
dataset.valaciclovir_shingles = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(valaciclovir_codelist))
    .exists_for_patient()
    .as_int()
)

#5.b.3.Famciclovir
dataset.famciclovir_shingles = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(famciclovir_codelist))
    .exists_for_patient()
    .as_int()
)

#5.c.All recommended shingles treatments
shingles_all_treatment_codelist = (
    aciclovir_codelist
    + valaciclovir_codelist
    + famciclovir_codelist
)

# Any recommended shingles antiviral was prescribed
dataset.shingles_all_treatment = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(shingles_all_treatment_codelist))
    .exists_for_patient()
    .as_int()
)

# Counting how many different treatment categories were prescribed
dataset.shingles_treatment_count = (
    dataset.aciclovir_shingles
    + dataset.valaciclovir_shingles
    + dataset.famciclovir_shingles
)
 # Shingles treated: 1 if any recommended treatment was prescribed, 0 otherwise
dataset.shingles_treated = (
    (
        dataset.aciclovir_shingles
        + dataset.valaciclovir_shingles
        + dataset.famciclovir_shingles
    ) > 0
).as_int()
#6.Sinusitis

#6.a.Clinical event
dataset.has_sinusitis = (
    recent_clinical_event
    .where(clinical_events.snomedct_code.is_in(sinusitis_codelist))
    .exists_for_patient()
    .as_int()
)

#6.b.Treatment
# (Phenoxymethylpenicillin/Clarithromycin/Erythromycin/Doxycycline/Co-amoxiclav)

#6.b.1.Phenoxymethylpenicillin
dataset.phenoxymethylpenicillin_sinusitis = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(phenoxymethylpenicillin_codelist))
    .exists_for_patient()
    .as_int()
)

#6.b.2.Clarithromycin
dataset.clarithromycin_sinusitis = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(clarithromycin_codelist))
    .exists_for_patient()
    .as_int()
)

#6.b.3.Erythromycin
dataset.erythromycin_sinusitis = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(erythromycin_codelist))
    .exists_for_patient()
    .as_int()
)

#6.b.4.Doxycycline
dataset.doxycycline_sinusitis = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(doxycycline_codelist))
    .exists_for_patient()
    .as_int()
)

#6.b.5.Co-amoxiclav
dataset.co_amoxiclav_sinusitis = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(co_amoxiclav_codelist))
    .exists_for_patient()
    .as_int()
)

#6.c.All recommended sinusitis treatments
sinusitis_all_treatment_codelist = (
    phenoxymethylpenicillin_codelist
    + clarithromycin_codelist
    + erythromycin_codelist
    + doxycycline_codelist
    + co_amoxiclav_codelist
)

# Any recommended sinusitis antimicrobial was prescribed
dataset.sinusitis_all_treatment = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(sinusitis_all_treatment_codelist))
    .exists_for_patient()
    .as_int()
)

# Counting how many different treatment categories were prescribed
dataset.sinusitis_treatment_count = (
    dataset.phenoxymethylpenicillin_sinusitis
    + dataset.clarithromycin_sinusitis
    + dataset.erythromycin_sinusitis
    + dataset.doxycycline_sinusitis
    + dataset.co_amoxiclav_sinusitis
)

# Sinusitis treated: 1 if any recommended treatment was prescribed, 0 otherwise
dataset.sinusitis_treated = (
    (
        dataset.phenoxymethylpenicillin_sinusitis
        + dataset.clarithromycin_sinusitis
        + dataset.erythromycin_sinusitis
        + dataset.doxycycline_sinusitis
        + dataset.co_amoxiclav_sinusitis
    ) > 0
).as_int()

#7.Sore throat
#7.a.Clinical event
dataset.has_sore_throat = (
    recent_clinical_event
    .where(clinical_events.snomedct_code.is_in(sore_throat_codelist))
    .exists_for_patient()
    .as_int()
)

#7.b.Treatment
# (Phenoxymethylpenicillin/Clarithromycin/Erythromycin)

#7.b.1.Phenoxymethylpenicillin
dataset.phenoxymethylpenicillin_sore_throat = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(phenoxymethylpenicillin_codelist))
    .exists_for_patient()
    .as_int()
)

#7.b.2.Clarithromycin
dataset.clarithromycin_sore_throat = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(clarithromycin_codelist))
    .exists_for_patient()
    .as_int()
)

#7.b.3.Erythromycin
dataset.erythromycin_sore_throat = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(erythromycin_codelist))
    .exists_for_patient()
    .as_int()
)
#7.c.All recommended sore throat treatments
sore_throat_all_treatment_codelist = (
    phenoxymethylpenicillin_codelist
    + clarithromycin_codelist
    + erythromycin_codelist
)

# Any recommended sore throat antimicrobial was prescribed
dataset.sore_throat_all_treatment = (
    recent_medication
    .where(recent_medication.dmd_code.is_in(sore_throat_all_treatment_codelist))
    .exists_for_patient()
    .as_int()
)

# Counting how many different treatment categories were prescribed
dataset.sore_throat_treatment_count = (
    dataset.phenoxymethylpenicillin_sore_throat
    + dataset.clarithromycin_sore_throat
    + dataset.erythromycin_sore_throat
)

# Sore throat treated: 1 if any recommended treatment was prescribed, 0 otherwise
dataset.sore_throat_treated = (
    (
        dataset.phenoxymethylpenicillin_sore_throat
        + dataset.clarithromycin_sore_throat
        + dataset.erythromycin_sore_throat
    ) > 0
).as_int()


########################################################
'''
This section counts the number of PF consultations for each condition.
Outputs:
- pf_consultation_general: consultation count where their clinical events have any of the three general PF codes 
- pf_consultation_general_butno_condition: consultation count where their clinical events have any of the three general PF codes BUT no PF condition codes
- numerator_pf_consultation_{name}: number of PF consultations for a specific PF condition
- numerator_pf_episode_{name}: number of PF consultation episodes for a specific PF condition (consultations occurring within the same day are grouped into a single episode)
'''

selected_events = select_events_between(clinical_events, start_date, index_date)
pf_consultation_events = select_events_from_codelist(selected_events, codelists.pf_consultation_events_dict["pf_consultation_services_combined"])
# 'pf_ids' is a set of consultation ids where their clinical events have any of the three general PF codes
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = select_events_by_consultation_id(selected_events, pf_ids)

# dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()
dataset.pf_consultation_general = pf_consultation_events.consultation_id.count_distinct_for_patient()

pf_conditions_pf_codes = {
    "uti": codelists.uti_code,                     
    "sinusitis": codelists.sinusitis_code,
    "insectbite": codelists.insectbite_code,
    "otitismedia": codelists.otitismedia_code,
    "sorethroat": codelists.sorethroat_code,
    "shingles": codelists.shingles_code,
    "impetigo": codelists.impetigo_code, # I will need to add controls as for our analysis will use Compartive XTITSA 
}

# a set of codes for any PF condition
pf_conditions_pf_code_set = []
for codes in pf_conditions_pf_codes.values():
    pf_conditions_pf_code_set += codes

# select events with both general PF codes and PF condition codes
pf_condition_events = selected_pf_id_events.where(selected_pf_id_events.snomedct_code.is_in(pf_conditions_pf_code_set))
# extract consultation IDs for these events
pf_condition_consultation_ids = pf_condition_events.consultation_id
# select PF consultation events (those with general PF codes) that the consultation id is not in the set of consultation ids with condition codes
pf_consultations_general_butno_condition_events = pf_consultation_events.where(
    ~pf_consultation_events.consultation_id.is_in(pf_condition_consultation_ids)
)
# count number of consultations from the above event selection
dataset.pf_consultation_general_butno_condition = (
    pf_consultations_general_butno_condition_events.consultation_id.count_distinct_for_patient()
)

for name, codes in pf_conditions_pf_codes.items():
    # count consultations and episodes (consultations occurring within the same day are grouped into a single episode)
    count_pf_consultation, count_pf_episode = has_event_count(selected_pf_id_events, codes)
    setattr(dataset, f"numerator_pf_consultation_{name}", count_pf_consultation)
    setattr(dataset, f"numerator_pf_episode_{name}", count_pf_episode)

########################################################
'''
This section counts the number of GP consultations for PF-related conditions and control conditions, explicitly excluding consultations identified as PF consultations using general PF service codes.

Key logic:
- pf_ids' represents consultation IDs where at least one event contains a general PF service code.

1. 'gp_events_clean' is derived by excluding all events belonging to consultations in 'pf_ids'. 
- This ensures that GP consultation counts do not overlap with PF consultation counts.
2. Identify PF-related conditions in managed in GP using the condition-specific SNOMED codelists (e.g. UTI, sinusitis)
3. Consultations are counted using distinct consultation IDs per patient. 
- For testing purpose, episodes are defined by grouping events occurring within a 1-day window, so multiple events on the same day are treated as a single episode.

Outputs:
- numerator_gp_consultation_{name}: number of GP consultations for a specific PF condition
- numerator_gp_episode_{name}: number of GP consultation episodes for a specific PF condition (consultations occurring within the same day are grouped into a single episode)
'''

gp_events_clean = selected_events.where(
    ~selected_events.consultation_id.is_in(pf_ids)
)

pf_conditions_gp_codes = {
    "uti": codelists.gp_snomed_codelist_uti,
    "sinusitis": codelists.gp_snomed_codelist_sinusitis,
    "insectbite": codelists.gp_snomed_codelist_insect_bites,
    "otitismedia": codelists.gp_snomed_codelist_otitis_media,
    "sorethroat": codelists.gp_snomed_codelist_sore_throat,
    "shingles": codelists.gp_snomed_codelist_shingles,
    "impetigo": codelists.gp_snomed_codelist_impetigo,
}

control_conditions_gp_codes = {
    "lowerbackpain": codelists.gp_snomed_codelist_lower_back_pain,
}

all_conditions_gp_codes = {
    **pf_conditions_gp_codes,
    **control_conditions_gp_codes,
}

# for name, codes in pf_conditions_gp_codes.items():
for name, codes in all_conditions_gp_codes.items():
    count_gp_consultation, count_gp_episode = has_event_count(gp_events_clean, codes)
    setattr(dataset, f"numerator_gp_consultation_{name}", count_gp_consultation)
    setattr(dataset, f"numerator_gp_episode_{name}", count_gp_episode)

########################################################
'''
This section counts the number of GP consultations for PF-related conditions by consultation mode (excluding consultations with PF service codes)

Key logic:
- 'gp_events_clean' already excludes all consultations with PF service codes (pf_ids).

1. 'pf_conditions_gp_code_set' is creased, including all GP used SNOMED codes for the seven conditions 
2. events in 'gp_events_clean' are filtered using the combined code set to identify condition-related events.
3. consultation IDs are then extracted from events in step 2. This set of IDs represents the condition-related consultations without any PF service codes.
4. retrieve all events within the selected consultation IDs 
5. consultation mode is classified using specific codelists:
5.1 three sets of events are identified for each consultation type: face-to-face, online, and telephone
5.2 consultation IDs are extracted for each type/event set
5.3 a hierarchical assignment is applied:
- face-to-face takes precedence
- online excludes consultations already classified as face-to-face
- telephone excludes consultations classified as face-to-face or online
- remaining consultations are classified as 'othermode'
- all counts are based on distinct consultation IDs per patient.

Outputs:
- gp_pf_consultation_f2f
- gp_pf_consultation_online
- gp_pf_consultation_f2f_telephone
- gp_pf_consultation_othermode
'''
pf_conditions_gp_code_set = []
for codes in pf_conditions_gp_codes.values():
    pf_conditions_gp_code_set += codes

gp_pf_condition_events = gp_events_clean.where(gp_events_clean.snomedct_code.is_in(pf_conditions_gp_code_set))
gp_pf_condition_ids = gp_pf_condition_events.consultation_id
gp_pf_condition_all_events = select_events_by_consultation_id(gp_events_clean,gp_pf_condition_ids)
gp_pf_f2f_type_events = select_events_from_codelist(
    gp_pf_condition_all_events,
    codelists.gp_codelist_consultation_f2f
)
gp_pf_online_type_events = select_events_from_codelist(
    gp_pf_condition_all_events,
    codelists.gp_codelist_consultation_online
)
gp_pf_telephone_type_events = select_events_from_codelist(
    gp_pf_condition_all_events,
    codelists.gp_codelist_consultation_telephone
)
gp_pf_f2f_ids = gp_pf_f2f_type_events.consultation_id
gp_pf_online_ids = gp_pf_online_type_events.consultation_id
gp_pf_telephone_ids = gp_pf_telephone_type_events.consultation_id

dataset.gp_pf_consultation_f2f = (
    gp_pf_f2f_ids.count_distinct_for_patient()
)

dataset.gp_pf_consultation_online = (
    gp_pf_online_type_events.where(
        ~gp_pf_online_type_events.consultation_id.is_in(gp_pf_f2f_ids)
    ).consultation_id.count_distinct_for_patient()
)

dataset.gp_pf_consultation_telephone = (
    gp_pf_telephone_type_events.where(
        ~gp_pf_telephone_type_events.consultation_id.is_in(gp_pf_f2f_ids)
        & ~gp_pf_telephone_type_events.consultation_id.is_in(gp_pf_online_ids)
    ).consultation_id.count_distinct_for_patient()
)

dataset.gp_pf_consultation_othermode = (
    gp_pf_condition_all_events.where(
        ~gp_pf_condition_all_events.consultation_id.is_in(gp_pf_f2f_ids)
        & ~gp_pf_condition_all_events.consultation_id.is_in(gp_pf_online_ids)
        & ~gp_pf_condition_all_events.consultation_id.is_in(gp_pf_telephone_ids)
    ).consultation_id.count_distinct_for_patient()
)

########################################################
'''
This section repeats the above logic to count GP consultations by consultation mode,
but only for control conditions rather than PF-conditions

Outputs:
- gp_control_consultation_f2f
- gp_control_consultation_online
- gp_control_consultation_f2f_telephone
- gp_control_consultation_othermode
'''
control_conditions_gp_code_set = []
for codes in control_conditions_gp_codes.values():
    control_conditions_gp_code_set += codes

gp_control_condition_events = gp_events_clean.where(
    gp_events_clean.snomedct_code.is_in(control_conditions_gp_code_set)
)
gp_control_condition_ids = gp_control_condition_events.consultation_id
gp_control_condition_all_events = select_events_by_consultation_id(
    gp_events_clean,
    gp_control_condition_ids
)

gp_control_f2f_type_events = select_events_from_codelist(
    gp_control_condition_all_events,
    codelists.gp_codelist_consultation_f2f
)
gp_control_online_type_events = select_events_from_codelist(
    gp_control_condition_all_events,
    codelists.gp_codelist_consultation_online
)
gp_control_telephone_type_events = select_events_from_codelist(
    gp_control_condition_all_events,
    codelists.gp_codelist_consultation_telephone
)

gp_control_f2f_ids = gp_control_f2f_type_events.consultation_id
gp_control_online_ids = gp_control_online_type_events.consultation_id
gp_control_telephone_ids = gp_control_telephone_type_events.consultation_id

dataset.gp_control_consultation_f2f = (
    gp_control_f2f_ids.count_distinct_for_patient()
)

dataset.gp_control_consultation_online = (
    gp_control_online_type_events.where(
        ~gp_control_online_type_events.consultation_id.is_in(gp_control_f2f_ids)
    ).consultation_id.count_distinct_for_patient()
)

dataset.gp_control_consultation_telephone = (
    gp_control_telephone_type_events.where(
        ~gp_control_telephone_type_events.consultation_id.is_in(gp_control_f2f_ids)
        & ~gp_control_telephone_type_events.consultation_id.is_in(gp_control_online_ids)
    ).consultation_id.count_distinct_for_patient()
)

dataset.gp_control_consultation_othermode = (
    gp_control_condition_all_events.where(
        ~gp_control_condition_all_events.consultation_id.is_in(gp_control_f2f_ids)
        & ~gp_control_condition_all_events.consultation_id.is_in(gp_control_online_ids)
        & ~gp_control_condition_all_events.consultation_id.is_in(gp_control_telephone_ids)
    ).consultation_id.count_distinct_for_patient()
)

########################################################
'''
This section counts the number of GP consultations for each PF-related conditions and control conditions by consultation mode (excluding consultations with PF service codes)

Outputs:
- gp_consultation_<name>_f2f
- gp_consultation_<name>_online
- gp_consultation_<name>_telephone
- gp_consultation_<name>_othermode
'''

# for name, codes in pf_conditions_gp_codes.items():
for name, codes in all_conditions_gp_codes.items():

    # condition-specific events -> consultation IDs
    condition_events = gp_events_clean.where(gp_events_clean.snomedct_code.is_in(codes))
    condition_ids = condition_events.consultation_id

    # retrieve all events within these consultations
    condition_all_events = select_events_by_consultation_id(gp_events_clean,condition_ids)

    # assign consultation mode
    f2f_events = select_events_from_codelist(condition_all_events,codelists.gp_codelist_consultation_f2f)
    online_events = select_events_from_codelist(condition_all_events,codelists.gp_codelist_consultation_online)
    telephone_events = select_events_from_codelist(condition_all_events,codelists.gp_codelist_consultation_telephone)
    f2f_ids = f2f_events.consultation_id
    online_ids = online_events.consultation_id
    telephone_ids = telephone_events.consultation_id

    setattr(dataset,f"gp_consultation_{name}_f2f",f2f_ids.count_distinct_for_patient())
    setattr(dataset,f"gp_consultation_{name}_online",
        online_events.where(
            ~online_events.consultation_id.is_in(f2f_ids)
        ).consultation_id.count_distinct_for_patient()
    )
    setattr(dataset,f"gp_consultation_{name}_telephone",
        telephone_events.where(
            ~telephone_events.consultation_id.is_in(f2f_ids)
            & ~telephone_events.consultation_id.is_in(online_ids)
        ).consultation_id.count_distinct_for_patient()
    )
    setattr(dataset,f"gp_consultation_{name}_othermode",
        condition_all_events.where(
            ~condition_all_events.consultation_id.is_in(f2f_ids)
            & ~condition_all_events.consultation_id.is_in(online_ids)
            & ~condition_all_events.consultation_id.is_in(telephone_ids)
        ).consultation_id.count_distinct_for_patient()
    )

########################################################
"""
Clinical variables for eligible population denominator:
- pregnant_this_month
- bullous_impetigo_this_month
- recurrent_impetigo_this_year
- catheter_status
- recurrent_uti
"""

from analysis.pf_variable_library import check_code_in_time_window, check_recurrent_status
# -- pregnancy_status - naive version
# pregnant_this_month = check_code_in_time_window(index_date-months(1),index_date, clinical_events, codelists.gp_snomed_codelist_pregnancy)
# dataset.pregnant_this_month = pregnant_this_month
# -- pregancy_status developed by Helen
# look back for recent end-of-pregnancy codes -- assume no longer pregnant if in last 12 weeks
dataset.pregnancy_end_recent = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_end_pregnancy) &
    clinical_events.date.is_on_or_between(start_date - weeks(32), start_date - days(1))
    ).sort_by(clinical_events.date).last_for_patient().date
# look ahead 40 weeks for end-of-pregnancy codes
dataset.pregnancy_end = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_end_pregnancy) &
    clinical_events.date.is_on_or_between(start_date, start_date + weeks(40))
    ).sort_by(clinical_events.date).first_for_patient().date
# estimated date of delivery (EDD) - very recent or in future to estimate the known start of pregnancy
dataset.pregnancy_edd = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date - weeks(2), start_date + weeks(34)) &
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_pregnancy_edd)
    ).sort_by(clinical_events.date).first_for_patient().date
# recent "pregnant" codes - this is to be used where no delivery or EDD recorded
dataset.pregnancy_code = clinical_events.where(
    clinical_events.snomedct_code.is_in(codelists.gp_snomed_codelist_pregnancy) &
    clinical_events.date.is_on_or_between(start_date - weeks(12), start_date + weeks(4))
    ).sort_by(clinical_events.date).first_for_patient().date
# combine criteria to create a pregnancy status for the current month:
dataset.pregnant = case(
    # recent delivery -> not pregnant now:
    when(dataset.pregnancy_end_recent.is_on_or_after(start_date - weeks(12))).then("0-R"),
    # EDD in month or next 8 months, not preceeded by an end-of-pregnancy
    when(dataset.pregnancy_edd.is_not_null() 
        # check that the pregnancy linked to the EDD did not end very early,
        # i.e prior to the last 12 weeks which is already captured above
         & (dataset.pregnancy_end_recent.is_null() # no past delivery captured
            | ~dataset.pregnancy_end_recent.is_on_or_between(dataset.pregnancy_edd-weeks(28),dataset.pregnancy_edd+weeks(3))
            )).then("P-EDD"),
    # end of pregnancy in month or next 2 months - currently pregnant:
    when(dataset.pregnancy_end.is_on_or_before(start_date + weeks(12))).then("P-E"),
    # recent pregnancy code
    when(dataset.pregnancy_code.is_not_null()).then("P"),
    otherwise="0",)
pregnant_this_month = dataset.pregnant.is_in(("P-E", "P-EDD", "P"))
dataset.pregnant_this_month = pregnant_this_month

# bullous_impetigo during the specific month
bullous_impetigo_this_month = check_code_in_time_window(index_date-months(1),index_date,clinical_events,codelists.gp_snomed_codelist_bullous_impetigo)
dataset.bullous_impetigo_this_month = bullous_impetigo_this_month

# recurrent_impetigo: (defined as 2 or more episodes in the same year) 
# an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
# >= two 4-week-separated episodes
recurrent_impetigo_this_year = check_recurrent_status(index_date, clinical_events, codelists.gp_snomed_codelist_impetigo, 
                                                      lookback_months=12, gap_weeks=4, min_episodes=2)
dataset.recurrent_impetigo_this_year = recurrent_impetigo_this_year

# catheter_status: excluding patients who clearly have a catheter, and for following 12 months after code is included
catheter_status = check_code_in_time_window(index_date - months(12),index_date,clinical_events,codelists.gp_snomed_codelist_urinary_catheter)
dataset.catheter_status = catheter_status

# recurrent_uti: (2 episodes in last 6 months, or 3 episodes in last 12 months) an episode is defined as a 4 week period, so any codes within this time are considered to be part of the same episode.
# recurrent_uti_6m = (age < 0)
# recurrent_uti_12m = (age < 0)
recurrent_uti_6m = check_recurrent_status(
    index_date, clinical_events, codelists.gp_snomed_codelist_uti,
    lookback_months=6, gap_weeks=4,min_episodes=2
)
recurrent_uti_12m = check_recurrent_status(
    index_date, clinical_events, codelists.gp_snomed_codelist_uti,
    lookback_months=12, gap_weeks=4, min_episodes=3
)
recurrent_uti = recurrent_uti_6m | recurrent_uti_12m
dataset.recurrent_uti_6m = recurrent_uti_6m
dataset.recurrent_uti_12m = recurrent_uti_12m
dataset.recurrent_uti = recurrent_uti

########################################################
"""
Eligibility/clinical characteristics flag for study population denominator:
- include_patient_otitis_media
- include_patient_sinusitis
- include_patient_sore_throat
- include_patient_insect_bites
- include_patient_shingles
- include_patient_impetigo
- include_patient_uti
- include_patient_overall_eligible
"""
female = patients.sex.is_in(["female"])

# Condition: acute otitis media
# - inclusion: children aged 1 to 17 years
# - exclusion: none
include_patient_otitis_media = (age >= 1) & (age <= 17) 
dataset.include_patient_otitis_media = include_patient_otitis_media

# Condition: acute sinusitis
# - inclusion: age >= 12
# - exclusion: none
include_patient_sinusitis = (age >= 12)
dataset.include_patient_sinusitis = include_patient_sinusitis

# Condition: acute sore throat
# - inclusion: age >= 5
# - exclusion: pregnant female under 16s
age_eligible_sore_throat = (age >= 5)
exclusion_sore_throat = pregnant_this_month & (age < 16) & (female)
include_patient_sore_throat = (age_eligible_sore_throat & ~exclusion_sore_throat)
dataset.include_patient_sore_throat = include_patient_sore_throat

# Condition: infected insect bites
# - inclusion: age >= 1
# - exclusion: pregnant female under 16s
age_eligible_insect_bites = (age >= 1)
exclusion_insect_bites = pregnant_this_month & (age < 16) & (female)
include_patient_insect_bites = (age_eligible_insect_bites & ~exclusion_insect_bites)
dataset.include_patient_insect_bites = include_patient_insect_bites

# Condition: shingles
# - inclusion: age >= 18
# - exclusion: pregnant female
age_eligible_shingles = (age >= 18)
exclusion_shingles = pregnant_this_month & (female)
include_patient_shingles = (age_eligible_shingles & ~exclusion_shingles)
dataset.include_patient_shingles = include_patient_shingles

# Condition: impetigo
# - inclusion: age >= 1
# - exclusion: 
# - - bullous impetigo, 
# - - recurrent impetigo (defined as 2 or more episodes in the same year), 
# - - pregnant female under 16 years
impetigo_age_eligible = (age >= 1)
impetigo_exclusion = (bullous_impetigo_this_month | recurrent_impetigo_this_year | (pregnant_this_month & (age < 16) & female))
include_patient_impetigo = (impetigo_age_eligible & ~impetigo_exclusion)
dataset.include_patient_impetigo = include_patient_impetigo

# Condition: Uncomplicated UTI
# - inclusion: women aged 16 to 64 years
# - exclusion: 
# - - pregnant female
# - - urinary catheter
# - - recurrent UTI: 2 episodes in last 6 months, or 3 episodes in last 12 months
uuti_eligible = (age >= 16) & (age <= 64) & female
uuti_exclusion = (pregnant_this_month | catheter_status | recurrent_uti)
include_patient_uuti = (uuti_eligible & ~uuti_exclusion)
dataset.include_patient_uuti = include_patient_uuti

# include_patient_overall_eligible
include_patient_overall_eligible = (include_patient_otitis_media|include_patient_sinusitis
                                  |include_patient_sore_throat|include_patient_insect_bites
                                  |include_patient_shingles|include_patient_impetigo|include_patient_uuti)
dataset.include_patient_overall_eligible = include_patient_overall_eligible
########################################################
'''A&E variables'''
# select A&E clinical events in month based on arrival date
ae_events = emergency_care_attendances.where(emergency_care_attendances.arrival_date.is_on_or_between(start_date, index_date))
# overall A&E attendances in month
dataset.ae_attendance_count = ae_events.count_for_patient()
# A&E PF-condition matching using GP codelists
# for name, codes in pf_conditions_gp_codes.items():
for name, codes in all_conditions_gp_codes.items(): 
    # primary diagnosis match
    ae_primary = ae_events.where(ae_events.diagnosis_01.is_in(codes))
    # non-primary diagnosis match
    ae_non_primary = ae_non_primary_diagnosis_matches(ae_events, codes)
    # count and flag
    setattr(dataset, f"ae_{name}_primary_count", ae_primary.count_for_patient())
    setattr(dataset, f"has_ae_{name}_non_primary", ae_non_primary)

########################################################
'''Appointments variables'''
# select attended appointments in month
dataset.appointment_scheduled = appointments.where(
    (appointments.start_date.is_on_or_between(start_date, index_date)) &
    (appointments.status.is_in([
            "Arrived",
            "In Progress",
            "Finished",
            "Visit",
            "Patient Walked Out",
            "Did Not Attend"
        ]))
).count_for_patient()
dataset.appointment_seen = appointments.where(
    (appointments.seen_date.is_on_or_between(start_date, index_date)) &
    (appointments.status.is_in([
            "Arrived",
            "In Progress",
            "Finished",
            "Visit",
            "Patient Walked Out",
            "Did Not Attend"
        ]))
).count_for_patient()

########################################################

show(dataset) # DEBUG: show the patients in the base population

########################################################
# Define measures for analysis