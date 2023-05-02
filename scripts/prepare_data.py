"""Script to prepare the PROMs data to build a database. The script will make some .csv files that will be used to build the database. The data comes from the NHS and can be downloaded [here](https://digital.nhs.uk/data-and-information/publications/statistical/patient-reported-outcome-measures-proms)"""
__author__ = "David Parker"

import os


def find_unique_headers(data_path: str) -> dict:
    """Find the unique headers in the PROMs data

    Parameters
    ----------
    data_path : str
        path to the PROMs data

    Returns
    -------
    dict[str, list[str]]
        Dictionary of unique headers and the files that have those headers
    """    
    headers = {}
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith(".csv"):
                with open(os.path.join(root, file), "r") as f:
                    file_name = file.split(".")[0]
                    headers[file_name] = f.readline().strip().split(",")
    # Group files with the same headers
    unique_headers = {}
    for file_name, file_headers in headers.items():
        if not headers:  # check if headers is empty
            continue
        header_set = tuple(file_headers)
        if header_set not in unique_headers:
            unique_headers[header_set] = []
        unique_headers[header_set].append(file_name)
    return unique_headers


def select_files(unique_headers: dict) -> dict:
    """Select the files to use to build the database. After manual inspection of the files, it was decided that only lists with a length of 8 or 12 contain the relevant data. There is data for Hip Replacement, Knee Replacement, Groin Hernia and Varicose Vein.

    Parameters
    ----------
    unique_headers : dict[str, list[str]]
        Dictionary of unique headers and the files that have those headers. From the `find_unique_headers` function

    Returns
    -------
    dict[str, list[str]]
        Dictionary of files to use for each condition, e.g. Hip Replacement
    """
    files_to_use = {"Hip Replacement": [], "Knee Replacement": [], "Groin Hernia": [], "Varicose Vein": []}

    for header_set, files in unique_headers.items():
        if len(files) in [8, 12]:
            for file in files:
                if "Hip" in file:
                    files_to_use["Hip Replacement"].append(file)
                elif "Knee" in file:
                    files_to_use["Knee Replacement"].append(file)
                elif "Groin" in file:
                    files_to_use["Groin Hernia"].append(file)
                elif "Varicose" in file:
                    files_to_use["Varicose Vein"].append(file)
    return files_to_use


def concatenate_files(data_path: str, output_path: str) -> None:
    """Concatenate all the files from each for each condition into one file. The files are concatenated in the order that they are read in. The files are also checked to make sure that the headers are the same and that the number of rows is correct.

    Parameters
    ----------
    data_path : str
        Path to the raw PROM data
    output_path : str
        _description_
    """    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    print(f"Concatenating files from {data_path} to {output_path}...")

    unique_headers = find_unique_headers(data_path)
    files_to_use = select_files(unique_headers)

    for condition, files in files_to_use.items():
        print(f"Concatenating {condition} files...")
        # Read in the data for each file
        data = []
        # Counter to check that the final file has the correct number of rows
        num_rows = 0
        for file in files:
            with open(os.path.join(data_path, f"{file}.csv"), "r") as f:
                data.append(f.readlines())
                num_rows += len(data[-1]) - 1
                print(f"\tFound {len(data[-1]) - 1} records in {file}")
        
        print(f"\tFound {num_rows} records in total")

        assert(len(data) == len(files))
        # Check that the headers are the same
        for i in range(len(data)):
            assert(data[i][0] == data[0][0])

        # Concatenate the data
        new_file_name = f"{condition.replace(' ', '_').lower()}.csv"
        with open(os.path.join(output_path, new_file_name), "w") as f:
            # Add an index column
            f.write(f"{condition.replace(' ', '_').lower()}_id,")
            f.write(data[0][0].replace('-', '_').replace(' ', '_').lower())
            row_index = 0
            for i in range(len(data)):
                for j in range(1, len(data[i])):
                    f.write(f"{row_index},")
                    f.write(data[i][j])
                    row_index += 1

        # Check that the number of rows is correct
        with open(os.path.join(output_path, new_file_name), "r") as f:
            assert(len(f.readlines()) == num_rows + 1)

        print(f"\tSaved {new_file_name} to {output_path} with {num_rows} records")

def main():
    concatenate_files("data/raw", "data/processed")

if __name__ == '__main__':
    main()