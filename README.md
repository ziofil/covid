# Covid
Altair interactive visualizations of current COVID trends. The script pulls data from [JHU](https://github.com/CSSEGISandData/COVID-19) and generates new and total (absolute and relative to population) cases and deaths visualizations for the desired countries. It then opens the interactive charts in four new browser tabs.

You can (shift-)click on the legend items to selectively visualize and compare the trends.

# Usage
1. Edit `covid.py` with the desired countries
2. Execute `python covid.py --browser path/to/browser/executable` from the shell (browser arg is optional)

# Example:
![example graph](https://github.com/ziofil/covid/blob/master/example.png)

# TODO
Currently some countries may not work due to a name mismatch between the JHU and the worldbank datasets. I need to find which ones are off and fix them manually.
