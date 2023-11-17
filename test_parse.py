import csv
import json

if __name__ == "__main__":
    request_list = []

    with open("request_data_3.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            request_list.append(row[0])

    request = request_list[0]
    # try making a headers.json and cookies.json file
    headers = {}
    cookies = {}

    