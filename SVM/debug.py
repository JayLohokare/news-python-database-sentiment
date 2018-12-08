import csv

with open('newsQuerySheet.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    print (csv_reader)
    for row in csv_reader:
        print (row[3], row[4])