'''
Dataset definition: monthly patient-level dataset
Measures: data validation measures - pre-analysis exploration / quality assurance
'''
###########################################################################
#--------------------------- dataset definition ---------------------------
###########################################################################
# use INTERVAL to run across multiple months, but for now just run for one month to explore the data and measures









#################################################################
#--------------------------- measures ---------------------------
#################################################################
from ehrql import create_measures, months

measures = create_measures()
measures.define_defaults(
    intervals=months(2).starting_on("2024-02-01"),
)
measures.configure_disclosure_control(enabled=False)