import csv
import json
import humanize

# tzero = datetime.datetime(2022, 11, 10, 22, 18).timestamp()
tzero = 0
g = 9.81

with open("Subscale Launch Data/MPL3115.csv", "rt") as csv_file, open("mpl3115.ndjson", "wt") as json_file:
    reader = csv.DictReader(csv_file)
    count = 0
    for row in reader:
        row = dict((k, float(v)) for k, v in row.items())
        row["timestamp"] += tzero
        print(json.dumps(row), file=json_file)
        count += 1

    print(f"Converted {count} points")
    print(f"    json: {humanize.naturalsize(json_file.tell(), binary=True)}")

with open("Subscale Launch Data/MPU6050.fixed.csv", "rt") as csv_file, open("mpu6050.ndjson", "wt") as json_file:
    csv_file.readline() # Skip header, we'll use our own shorter keys
    reader = csv.DictReader(csv_file, ["timestamp", "temp", "ax", "ay", "az", "gx", "gy", "gz"])
    count = 0
    for row in reader:
        row = dict((k, float(v)) for k, v in row.items())
        row = {
            "timestamp": row["timestamp"],
            "temp": row["temp"],
            # Convert to m/s^2, same as linux iio
            "accel": (row["ax"] * g, row["ay"] * g, row["az"] * g),
            "gyro": (row["gx"], row["gy"], row["gz"]),
        }
        row["timestamp"] += tzero
        print(json.dumps(row), file=json_file)
        count += 1

    print(f"Converted {count} points")
    print(f"    json: {humanize.naturalsize(json_file.tell(), binary=True)}")

