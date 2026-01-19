import csv

def save_to_csv(filename, column_names):
    """ Function to save data to a CSV file """
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()


def read_from_csv(filename):
    """ Function to read data from a CSV file """
    data = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def append_to_csv(filename, row, column_names):
    """ Function to append a row to the CSV file """
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writerow(row)
        


def get_row_from_csv(filename, row_index):
    """ Function to get a row from the CSV file """
    data = read_from_csv(filename)
    return data[row_index]