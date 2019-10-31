# ghcn-daily
Pull down and reformat GHCN daily weather for a particular station

# usage
Run the script passing a GHCN station identifier. The script will try to locate the station metadata and the daily weather file for that station and, if successful, prints it to stdout
```sh
$ python ghcn-daily.py USW00023188 > daily.csv
```
# references

GHCN data this script access
https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/

The station metadata is looked for in the ghcn-stations.txt file and the data files are looked for in /all/. The readme.txt file at the top level has the documentation used for scripting the parsing rules. 
