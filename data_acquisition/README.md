# Data Acquisition

Python scripts to scrap the data from each of the sources is provided here. Notice that any update in sources can make this code useless.

The execution pipeline is the following:
1. Execute the desired crawler for a platform. Scripts can be found in `crawlers/`.
2. Structure the data using the scripts within `processing/`.
3. Infer gender with `genderize/`.

You will need to include your `DATA_PATH` and Gender API key in `constansts.py`.
