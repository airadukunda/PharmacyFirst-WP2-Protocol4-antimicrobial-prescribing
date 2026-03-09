    #this file defines the practices for the patients and selects the fields that need to be included in the data for analysis. 
    #This data includes the denominator of the practice population for objective 2, the numerators will be all consultations 
from ehrql import create_dataset, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events, 
#need to add Appointment
import codelists
dataset = create_dataset()

start_date = "2024-01-31"
        #change to end of month
index_date = "2025-11-30"
registration_start = practice_registrations.for_patient_on(start_date)
registration_end = practice_registrations.for_patient_on(index_date)
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(start_date, index_date)
)
pf_consultation_events = selected_events.where(selected_events.snomedct_code.is_in(codelists.pf_consultation_events_dict["pf_consultation_services_combined"]))

'''
dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()
    #add PF condition codes and check consultation ID matches
pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = selected_events.where(
    selected_events.consultation_id.is_in(pf_ids)
)
dataset.sex = patients.sex

dataset.age = patients.age_on(index_date)
'''
dataset.define_population(
    registration_start.exists_for_patient() | registration_end.exists_for_patient())


    #add IMD, STP, region

dataset.practice = practice_registrations.for_patient_on("2025-11-30").practice_pseudo_id
dataset.stp = practice_registrations.for_patient_on("2025-11-30").practice_stp
dataset.region = practice_registrations.for_patient_on("2025-11-30").practice_nuts1_region_name
show(dataset)

#add the total number of consultations
#clinical_events.where(clinical_events.date.is_in(appointments.date))