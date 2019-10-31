
# James, C. Oct 2019


import sys, os
import csv
import datetime
import requests

# fixed-width field rules for station metadata file
station_meta_rules = [
    ('id', 1, 11, str),
    ('lat', 13, 20, float),
    ('lon', 22, 30, float),
    ('elev', 32, 37, float),
    ('state', 39, 40, str),
    ('name', 42, 71, str),
    ('gsn_flag', 73, 75, str),
    ('hcn_crn_flag', 77, 79, str),
    ('wmo_id', 81, 85, str)
]

# data line metadata fields fixed width defs
data_meta_rules = [
    ('id', 1, 11, str),
    ('year', 12, 15, int),
    ('month', 16, 17, int),
    ('field', 18, 21, str)
]

# data line value fields fixed with defs
# note, these are defs within the 8 char block
# for each data line after the metadata fields, there are 31 of these blocks
data_value_rules = [
    ('val', 1, 5, float),
    ('mflag', 6, 6, str),
    ('qflag', 7, 7, str),
    ('sflag', 8, 8, str)
]

# parse fixed-wdith text using rules defined in defs
def read_fixedwidth(text, defs):
    data = {}
    for d in defs:
        fname, start, end, cfunc = d
        try:
            data[fname] = cfunc(text[start-1:end].strip())
        except:
            data[fname] = None
    return data

data_dir_url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/all/"
station_meta_url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"

if len(sys.argv) < 2:
    sys.exit("Please provide a station ID e.g.: python ghcn-daily.py USW00023188")

station_id = sys.argv[1]
data_file_url = "{}{}.dly".format(data_dir_url, station_id)

# make sure data file exists for station
if requests.head(data_file_url).status_code != 200:
    sys.exit("Daily file for {} not found".format(station_id))

# get station metadata
r = requests.get(station_meta_url, stream=True)
for l in r.iter_lines():
    station_meta = read_fixedwidth(l.decode(), station_meta_rules)
    if station_meta['id'] == station_id:
        break
else:
    sys.exit("Could not find metadata for {}".format(station_id))

data_file = requests.get(data_file_url, stream=True)
data = {}
fields = []
for row in data_file.iter_lines():
    row = row.decode()

    # get metadata fields
    row_meta = read_fixedwidth(row, data_meta_rules)

    # get all unique fields - changes over time series
    if row_meta['field'] not in fields:
        fields.append(row_meta['field'])

    block_len = 8
    block_start = 22
    day = 1
    
    while block_start < len(row):
        vdict = read_fixedwidth(row[block_start-1:block_start+(block_len-1)], data_value_rules)

        # break when we hit an invalid day for a month that doesn't have 31 days
        # because the format makes all months have 31 days
        try:
            date = datetime.datetime(row_meta['year'], row_meta['month'], day)
        except:
            break

        if row_meta['year'] not in data:
            data[row_meta['year']] = {}
        if row_meta['month'] not in data[row_meta['year']]:
            data[row_meta['year']][row_meta['month']] = {}
        if day not in data[row_meta['year']][row_meta['month']]:
            data[row_meta['year']][row_meta['month']][day] = {}

        data[row_meta['year']][row_meta['month']][day][row_meta['field']] = vdict

        block_start += block_len
        day += 1

writer = csv.writer(sys.stdout)

# initialize header with metadata field names
header = ["STATION", "STATION_NAME", "LATITUDE", "LONGITUDE", "ELEVATION", "DATE"]

# add field names to header
for f in fields:
    header += [f, f+"_m", f+"_q", f+"_s"]

writer.writerow(header)

# print CSV
for year in sorted(data.keys()):
    for month in sorted(data[year].keys()):
        for day in sorted(data[year][month].keys()):

            # initialize row with non-data fields
            row = [
                station_meta['id'],
                station_meta['name'],
                station_meta['lat'],
                station_meta['lon'],
                station_meta['elev'],
                "{:04d}-{:02d}-{:02d}".format(year, month, day)
            ]
            
            # add in all data fields, preserving order by looping through field list
            # in same order as we did when we initialized the header fields
            for f in fields:
                if f not in data[year][month][day]:
                    row += [None, None, None]
                else:
                    fdata = data[year][month][day][f]
                    v, m, q, s = fdata['val'], fdata['mflag'], fdata['qflag'], fdata['sflag']
                    row += [v, m, q, s]

            writer.writerow(row)
