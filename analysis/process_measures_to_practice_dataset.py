import pandas as pd

input_file = "output/practice_measures.csv"
df = pd.read_csv(input_file)

print(df.groupby("interval_start")["practice"].nunique())
print(df[df["measure"] == "population"].groupby("interval_start")["numerator"].sum())

df["interval_start"] = pd.to_datetime(df["interval_start"])

pop = (
    df[df["measure"] == "appointments_total"]
    .rename(columns={"denominator": "population"})
    [["practice", "stp", "region", "interval_start", "population"]]
)

appt = (
    df[df["measure"] == "appointments_total"]
    .rename(columns={"numerator": "appointments_total"})
    [["practice", "stp", "region", "interval_start", "appointments_total"]]
)

df_wide = pop.merge(
    appt,
    on=["practice", "stp", "region", "interval_start"],
    how="left"
)

df_wide["appointments_total"] = df_wide["appointments_total"].fillna(0)


pf = (
    df[df["measure"] == "pf_consultation_general"]
    .rename(columns={"numerator": "pf_consultation_general"})
    [["practice", "stp", "region", "interval_start", "pf_consultation_general"]]
)
pf_uti_consultation = (
    df[df["measure"] == "pf_consultation_uti"]
    .rename(columns={"numerator": "pf_consultation_uti"})
    [["practice", "stp", "region", "interval_start", "pf_consultation_uti"]]
)
pf_uti_eligible = (
    df[df["measure"] == "pf_consultation_uti"]
    .rename(columns={"denominator": "populationeligible_uuti"})
    [["practice", "stp", "region", "interval_start", "populationeligible_uuti"]]
)

df_wide = df_wide.merge(pf, on=["practice", "stp", "region", "interval_start"], how="left")
df_wide = df_wide.merge(pf_uti_consultation, on=["practice", "stp", "region", "interval_start"], how="left")
df_wide = df_wide.merge(pf_uti_eligible, on=["practice", "stp", "region", "interval_start"], how="left")
df_wide["pf_consultation_general"] = df_wide["pf_consultation_general"].fillna(0)
df_wide["pf_consultation_uti"] = df_wide["pf_consultation_uti"].fillna(0)
df_wide["populationeligible_uuti"] = df_wide["populationeligible_uuti"].fillna(0)

df_wide.to_csv("output/practice_level_data.csv", index=False)

print(df_wide.head())
print(df_wide["interval_start"].unique())
print(df_wide.groupby("interval_start")["practice"].nunique())
print(df_wide.groupby("interval_start")["population"].sum())