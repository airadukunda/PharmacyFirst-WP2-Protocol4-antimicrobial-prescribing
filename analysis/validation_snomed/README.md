# Validation of SNOMED coding patterns in GP consultations related to Pharmacy First conditions

The Python files in this folder examine coding patterns within GP consultations related to Pharmacy First (PF) conditions, excluding consultations classified as
PF consultations.

For each PF condition, consultations are identified using the corresponding condition-specific SNOMED codelist. Within these GP consultations, the frequency of each SNOMED code from the same condition-specific codelist is quantified by counting the number of unique consultations (`consultation_id`) in which the code appears.

## Overview of workflow

The workflow consists of two main steps:

1. Generate patient-level datasets containing consultation counts for each SNOMED code within each PF-condition-specific codelist.
2. Reshape and aggregate these outputs into SNOMED-code-level summary datasets and visualisations.

- `dataset_definition_snomed_validation.py`: defines the patient-level dataset for step 1.
- `process.py`: processes the patient-level datasets (step 2) by:

## Detailed approach:
1. Use the existing PF-condition-specific SNOMED codelists to identifyconsultations related to each PF condition.
2. Exclude consultations already classified as PF consultations, restricting the analysis to remaining GP consultations related to the PF condition.
3. For each PF condition and each SNOMED code within the same condition-specific codelist, calculate the number of unique consultations (`consultation_id`) in which the code appears.
4. Produce an aggregated output dataset with one row per PF condition and SNOMED code, and generate summary datasets and plots.

The resulting dataset from 4 includes:
- PF condition
- SNOMED code
- SNOMED term
- number of unique consultations containing the code