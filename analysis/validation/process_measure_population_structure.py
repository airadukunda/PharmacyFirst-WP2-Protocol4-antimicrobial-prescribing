import pandas as pd

df = pd.read_csv("output/patient_measures_population_structure.csv")

measures_of_interest = [
    "population_by_sex",
    "population_by_age",
    "population_by_ethnicity",
    "population_by_imd",
    "population_by_region",
]

df = df[df["measure"].isin(measures_of_interest)].copy()

# 拆成 category + variable
def get_category_variable(row):
    if row["measure"] == "population_by_sex":
        return "sex", row["sex"]
    elif row["measure"] == "population_by_age":
        return "age", row["age_band"]
    elif row["measure"] == "population_by_ethnicity":
        return "ethnicity", row["ethnicity"]
    elif row["measure"] == "population_by_imd":
        return "imd", row["imd"]
    elif row["measure"] == "population_by_region":
        return "region", row["region"]
    else:
        return None, None

df[["category", "variable"]] = df.apply(
    lambda row: pd.Series(get_category_variable(row)), axis=1
)

df = df.rename(columns={
    "interval_start": "month",
    "numerator": "pf_population",
    "denominator": "total_population"
})

df_final = df[["month", "category", "variable", "pf_population", "total_population"]]

df_final = (
    df_final
    .groupby(["month", "category", "variable"])
    .sum()
    .reset_index()
)

category_order = ["sex", "age", "ethnicity", "imd", "region"]

df_final["category"] = pd.Categorical(
    df_final["category"],
    categories=category_order,
    ordered=True
)

df_final = df_final.sort_values(["month", "category", "variable"])

df_final.to_csv("output/patient_measures_population_structure_longformat.csv", index=False)

print(df_final.head())