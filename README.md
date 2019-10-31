# ghcn-daily
Pull down and reformat GHCN daily weather for a particular station

# usage
Run the script passing a GHCN station identifier. The script will try to locate the station metadata and the daily weather file for that station and, if successful, prints it to stdout

```sh
$ python ghcn-daily.py USW00023188 > daily.csv
```
