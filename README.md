# Command to run the code

## For Phase-2
```
python calculate_weighgts.py files wts_files
```

## For Phase-3
```
python indexing.py files output_files
```

## For Phase-4
First run the indexing command to generate the dictionary file and posting file once.
```
python indexing.py files output_files
```
After that we can run as many retrievals as we want

Exampls: 1
```
python retrieve.py computer,network 0.5,0.75
```
Exampls: 2
```
python retrieve.py international,affairs
```