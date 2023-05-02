"""Script to prepare the SQL files to build the database for the PROMs data. It is assumed that the script `prepare_data.py` has been run first to create the .csv files."""
__author__ = "David Parker"

import argparse
import traceback
import os

def get_cli_args():
    """Parse command line arguments"""
    try:
        parser = argparse.ArgumentParser(description="""Script to prepare the SQL files """)
        parser.add_argument("-f", "--foo", help="Help", required=False, default="bar")
    except:
        print("An exception occurred with argument parsing. Check your provided options.")
        traceback.print_exc()
    return parser.parse_args()

def make_schema(data_path: str):
    """Make the schema for the database"""

    with open("database/schema.sql", "w") as f_schema:
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.endswith(".csv"):
                    with open(os.path.join(root, file), "r") as f_data:
                        file_name = file.split(".")[0]
                        headers = f_data.readline().strip().split(",")
                        f_schema.write(f"CREATE TABLE {file_name} (\n")
                        for idx, header in enumerate(headers):
                            header = header.replace(" ", "_").lower()
                            if idx == 0:
                                f_schema.write(f"\t{header} INTEGER PRIMARY KEY,\n")
                            elif idx < 7 and idx > 0:
                                    f_schema.write(f"\t{header} TEXT,\n")
                            elif idx >= 7 and idx < len(headers) - 1:
                                f_schema.write(f"\t{header} REAL,\n")
                            elif idx == len(headers) - 1:
                                f_schema.write(f"\t{header} REAL\n")
                        f_schema.write(");\n\n")


def copy_data(data_path: str):
    """Copy the data from the .csv files to the database"""
    with open("database/import.sql", "w") as f_import:
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.endswith(".csv"):
                    with open(os.path.join(root, file), "r") as f_data:
                        file_name = file.split(".")[0]
                        file_path = os.path.join(root, file).replace("\\", "/")
                        f_import.write(f"\copy {file_name} FROM '{file_path}' WITH (FORMAT csv, HEADER true);\n")

def drop_tables():
    """Drop the tables in the database"""
    with open("database/drop.sql", "w") as f_drop:
        f_drop.write("DROP TABLE IF EXISTS hip_replacement, knee_replacement, groin_hernia, varicose_vein;\n")

def main():
    args = get_cli_args()
    if not os.path.exists("database"):
        os.mkdir("database")
    make_schema("data/processed")
    copy_data("data/processed")
    drop_tables()
    

if __name__ == '__main__':
    main()