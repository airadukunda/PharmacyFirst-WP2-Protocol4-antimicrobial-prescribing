import os
cwd = os.getcwd()
print(cwd)
import pandas as pd
#This says to look at the output from dataset_definition...
pd.read_csv("../output/dataset.csv.gz")


#import os
#df = pd.read_csv(os.path.join("..", "data_folder", "data_file.csv.gz")) 
