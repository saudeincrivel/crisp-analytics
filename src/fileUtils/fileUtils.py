import os
import csv
from typing import List, Dict, Any


class FileUtils:
    @staticmethod
    def save_to_disk(data: List[Dict[str, Any]]) -> None:
        cur_directory = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(cur_directory, '..', 'data'))

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        existing_files = [file for file in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, file))]
        count = len(existing_files)

        file_path = os.path.join(data_dir, f"output_{count}.csv")

        if not data:
            raise ValueError("No data to save")

        campos = data[0].keys()

        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=campos)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        print('Data saved successfully to', file_path)
