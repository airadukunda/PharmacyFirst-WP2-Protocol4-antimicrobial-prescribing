from datetime import date
import yaml

# python analysis/generate_project.py > project_test.yaml
# start_dates = ["2024-02-01", "2024-03-01"]

def month_range(start, end):
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return dates

start = date(2022, 2, 1)
end = date(2026, 1, 31)
start_dates = month_range(start, end)

project = {
    "version": "4.0",
    "actions": {
        "generate_dataset": {
            "run": "ehrql:v1 generate-dataset analysis/dataset_definition_patients.py --output output/dataset_patients.csv.gz",
            "outputs": {"highly_sensitive": {"dataset": "output/dataset_patients.csv.gz"}}
        }
    }
}

for d in start_dates:
    d_str = d.isoformat()
    action_name = f"generate_patient_dataset_{d_str.replace('-', '_')}"
    project["actions"][action_name] = {
        "run": f"ehrql:v1 generate-dataset analysis/dataset_definition_patients.py --dummy-tables dummy_tables --output output/dataset_patients_{d_str}.csv.gz -- --start_date {d_str}",
        "outputs": {
            "highly_sensitive": {
                "dataset": f"output/dataset_patients_{d_str}.csv.gz"
            }
        }
    }

print(yaml.dump(project, sort_keys=False))