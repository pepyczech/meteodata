# meteodata
Python code to obtain weather data from Meteostat API based on Meteostat station ID or lat &amp; lon or address details (using OpenStreetMap API)

# 1. An overview of module use

The meteodata module allows obtaining hourly or daily weather data from the Meteostat API. The module works for any world-wide loaction, depending on Meteostat data availability.

# The data can be obtained using several different input options:

a. Meteostat station ID (data type: string) – see https://dev.meteostat.net/ (4-digit numerical code, e.g. “03647” for Little Rissington, Gloucestershire, UK)

b. Latitude and longitude (data type: list of floats) – e.g. [51.7836, -1.4854] for Witney, West Oxfordshire, UK. The code will pull and evaluate data for 20 nearist Meteostat stations and select one with best combination of distance & data completeness for the given time period (see Section 3. Function Inputs)

c. Address details (data type: dictionary) – the code leverages OpenStreetMap API to look up latitude and longitude based on address details (see https://wiki.openstreetmap.org/wiki/API ). The coordinates are then processed as per point (b). An example of a complete entry:

{‘street’:’Sheep St’,’town’:’Burford’,’country’:’United Kingdom’,’postcode’:’OX18 4LR’}

At least one key-value pair must be provided but ideally, country and at least one additional key-value pair should be provided for best results.

The code works for all world-wide locations, please note that UK postcodes must contain the space in the middle.

# 2. Module functions & dependencies

The module currently contains following custom functions:

- getMeteostat – main function, contains all Meteostat API functionality
- address2coords – uses OSM API to look up latitude and longitude based on address details

The module includes dependencies on the following python packages:

- pandas
- numpy
- datetime
- meteostat
- requests

# 3. Function inputs

The header of the main module function, with input parameters and default values, is below:

getMeteostat(loc='03647',date_range=None,offset=0,sample_rate='daily',interpol=1,
		min_coverage=0.9)

Input value description:

a. loc – geographical location from which the meteorological data is required– the options are (see Section 1 for more details):
- Meteostat station ID (data type: string) 
- Latitude & longitude (data type: list of floats)
- Address details (data type: dictionary)
- None (data type: Nonetype) – the code will not return any data if the value is set to None but will not return error

b. date_range – range of dates for which he meteorological data is required. Options:
- a range of dates (data type: a list of datetime.datetime values) – e.g. date_range=[datetime.datetime(2021, 5, 1),datetime.datetime(2022, 4, 1)]
- None (data type: Nonetype) – the code will pull data for 1 year from the current date

c. offset (data type: integer or float) – offset from the current date in days – used only if date_range is not provided. This is to allow adjustment of the latest date that will be used for data pull if date_range is not provided (in some cases meteorological data are uploaded into Meteostat database with some delay)

d. sample_rate (data type: string) – Meteostat API definition of sample rate. Options:
- ‘daily’ – daily data (default)
- anything else – hourly data

e. interpol (data type: int, float or boolean) – switches the built-in Meteostat API interpolation on or off
– False or numerical values <1 will result in no normalization & interpolation of the data (i.e. any gaps in data won’t be imputed)
- True or numerical values >=1 will result in no normalization & interpolation of the data

f. min_coverage (data type: float) – parameter used for optimization of Meteostat station selection if only geospatial coordinates or address are know. It is a threshold on proportion of weather data available within the date_range for each station that is deemed acceptable. Station with proportion of available data >= min_coverage will be only prioritized based on distance from the location.

An example:
- min_coverage = 0.9 (default value) – all stations with weather data available for at least 90% of the days (if sample_rate=’daily’) or hours (sample_rate=’hourly’) will be treated as equal and only prioritised by distance from the location. All other stations will be prioritized based on distance from location AND % weather data available within the date_range.

# 4. Practical examples

# a. Jupyter notebook

The functionality can be used in Jupyter notebook (meteostat1.ipynb)

- load dependencies (required python modules)
![image description](./pics/Screenshot%20from%202022-04-16%2014-07-04.png)
- execute the cells containing custom function definitions (see Section 2 for the list of functions
- Example 1 – obtaining weather data for a Meteostat station ID
- Example 2 – obtaining weather data for a location defined by latitude and longitude

First table above shows the list of weather stations sorted by distance & data availability. 

This is taking into account min_coverage value of 0.9 – e.g. Little Rissington has only 335 days (99.7%) of data available, compared to RAF Fairford with 336 days (100%) but it is rated better since it is closer and 99.7% is above the 90% threshold. Small differences in data completeness is resolved by Meteostat’s interpolation functionality.

Overall, Brize Norton is selected as it is closest to Witney and it has data availability >=90% (it actually has 100% data availability for the given time period)

- Example 3 – obtaining weather data for a location defined by latitude and longitude

The code feeds the address details into address2coords() functions and uses OpenStreetMap API to look up the latitude and longitude. The coordinates are then used in Meteostat API.

First table above shows the list of weather stations sorted by distance & data availability. 

This is taking into account min_coverage value of 0.9 – e.g. Little Rissington has only 335 days (99.7%) of data available, compared to RAF Brize Norton with 336 days (100%) but it is rated better since it is closer and 99.7% is above the 90% threshold. 

This results in Little Rissington being selected as best weather station, which makes sense as it is much closer to Burford than Brize Norton. Small differences in data completeness is resolved by Meteostat’s interpolation functionality.

# b. Using stand-alone python code

The functionality can be used by running stand-alone python source code (meteodata.py).

For example, the file can be loaded as custom python module (here we are using Spyder IDE). Don’t forget to add the location of the source code file to your IDE’s path manager - e.g. in Spyder:

The file meteodata.py contains all code, the source code is identical to dependencies and custom functions used in the Jupyter notebook (see section (a)).


The module needs to be loaded first

The main function can be then called to retrieve data



