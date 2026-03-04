from datetime import date
import yaml

# python analysis/generate_project.py > project_test.yaml

start_dates = ["2024-02-01", "2024-03-01"]
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
    action_name = f"generate_patient_dataset_{d.replace('-', '_')}"
    project["actions"][action_name] = {
        "run": f"ehrql:v1 generate-dataset analysis/dataset_definition_patients.py --output output/dataset_patients_{d}.csv.gz -- --start_date {d}",
        "outputs": {
            "highly_sensitive": {
                "dataset": f"output/dataset_patients_{d}.csv.gz"
            }
        }
    }

print(yaml.dump(project, sort_keys=False))