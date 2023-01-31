import json

fr = open("Fake Daemon\Data\Subscale Data - MPL3115.csv", "r")
fw = open("Fake Daemon\Data\MPL3115Modified.csv", "w")
for row in fr:
    tempRow = row.split(",")
    line = tempRow[0] + "," + tempRow[1] + "," + tempRow[2]
    fw.write(line)
    fw.write("\n")
fr.close()
fw.close()