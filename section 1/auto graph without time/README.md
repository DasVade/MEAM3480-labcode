	1.	Place the Python script (auto graph.py) and your data file
(.csv or .xlsx) in the same directory.
	2.	Open a terminal in that directory.
	3.	Run the script with the data file as an argument:
python “auto graph.py” your_data.csv
or
python “auto graph.py” your_data.xlsx
	4.	After running, the following files will be generated in the same directory:
	•	your_data.temp_plot.png   (Temperature vs Time plot)
	•	your_data.clean_temp.csv  (Extracted time–temperature data)

Notes:
	•	If the data file contains no explicit time column, time is reconstructed
using a fixed sampling interval defined in the script.
