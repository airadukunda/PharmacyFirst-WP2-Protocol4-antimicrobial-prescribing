
// read arrow output from ehrql
// stata itself does not directly support .arrow. However, OpenSAFELY's Stata Docker
// image contains the arrowload library that can load .arrow files in Stata.

. arrowload /path/to/arrow/file

// read compressed CSV output from ehrql
// stata cannot handle compressed CSV files directly, so unzip first to a plain CSV file
// the unzipped file will be discarded when the action finishes.
!gunzip output/dataset.csv.gz

// now import the uncompressed CSV using delimited
import delimited using output/dataset.csv

// save in compressed dta.gz format
gzsave output/model.dta.gz

// load a compressed .dta.gz file
gzload output/dataset.dta.gz