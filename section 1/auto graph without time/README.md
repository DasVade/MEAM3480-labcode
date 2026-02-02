Temperature Log Plotter - Quick Readme

Put the Python script and your data file in the same directory.

Files required:
	•	auto graph.py
	•	your_data.csv  OR  your_data.xlsx

Open a terminal in that directory and run:

python “auto graph.py” your_data.csv

or

python “auto graph.py” your_data.xlsx

If the file name contains spaces, use quotes, for example:

python “auto graph.py” “3480 Lab 1 Test Trials - PreSnow Second Trial.csv”

After running, the following files will be created in the same directory:
	•	your_data.temp_plot.png
	•	your_data.clean_temp.csv

If the data file does not contain a time column, time is reconstructed
using a fixed sampling interval defined in the script.
