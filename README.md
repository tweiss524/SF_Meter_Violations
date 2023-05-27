# Predicting Meter Violations in San Francisco

This project was completed in collaboration with Jeffrey Kuo, Tim Tantivilaisin, and Bryan Wang at the University of California, Berkeley, with guidance from Professor Thomas Bengtsson.

# Introduction

The objective of this project was to investigate crime in San Francisco. In particular, we decided to take an in-depth look into parking citations given throughout all of San Francisco obtained from unpaid meters in order to answer the following question: "if I do not pay the meter on a specific street $S$ during a specific time interval $T$, how likely am I to get a parking ticket?" This project aims to help the user make informed decisions about whether or not it is worth it to pay for the meter, thereby mitigating the financial consequences of failing to pay for a meter. Additionally, information about locations where meter violations are most common would be beneficial to the city, as this information would enable them to assess if tickets are being distributed fairly across neighborhoods, as well as devise more effective traffic regulations in regions where traffic violations are most common.

In order to answer these questions, the problem was transformed into a probability problem in which probabilities were calculated given a street section (e.g. Mission St. between Spear St. and Main St.), a 15 minute time interval (e.g. 9:00am - 9:15am), and a day of the week (e.g. Sunday). Note that a street section will be defined as a corridor -- the name of the street the section belongs to -- between two limits -- the two streets at either end of the section (e.g. Mission St. between Spear St. and Main St.). 

# Data Sources

Four main data sources were used throughout this analysis:

- [SFMTA Parking Citations Dataset](https://data.sfgov.org/Transportation/SFMTA-Parking-Citations/ab4h-6ztd): tabular dataset consisting of about 19M rows and 10 columns providing citation information from 2008 to present. Some of the columns in this dataset were paramount in constructing the probability of citations, such as \verb|Citation Location|, \verb|Citation Issued DateTime| (can obtain day of the week from this variable), and \verb|geom| (geometric endpoints of a street segment). This dataset was filtered to only provide information about meter violations in 2022-2023. 
- [Street Sweeping Schedule Dataset](https://data.sfgov.org/City-Infrastructure/Street-Sweeping-Schedule/yhqp-riqs): tabular dataset with about 40k rows and 17 columns giving information about the street sweeping schedule on each street. This dataset was used to obtain geometric endpoints for each street segment and was joined to both the parking citations dataset as well as the meter locations dataset (Map of Parking Meters). In order to correct for some of the incorrect mappings, we used the US Census Bureau Geocoder to run the address strings for each citation, giving us the correct geometry for each street section.
- [SFMTA Parking Meter Detailed Revenue Transactions Dataset](https://data.sfgov.org/Transportation/SFMTA-Parking-Meter-Detailed-Revenue-Transactions/imvp-dq3v): tabular dataset with about 157M rows and 8 columnswhich contained information about which meters were active, and intervals of when each meter was paid throughout the day.
- [Map of Parking Meters Dataset](https://data.sfgov.org/Transportation/Map-of-Parking-Meters/fqfu-vcqd): tabular dataset with about 35k rows and 40 columns which contained information about which streets each meter was on.

With this information, we gain knowledge of all instances when someone was parked illegally on a street due to not paying a meter, with the assumption that all metered spots are always taken. A detailed visualization of the data pipeline is shown in Figure 1 below: 

# Notebooks

A list of all the notebooks and their functions are explained below:
- [eda.ipynb](eda.ipynb): basic EDA performed on the SFMTA Parking Citations Dataset.
- [meter_eda.ipynb](meter_eda.ipynb): basic EDA performed on the SFMTA Parking Meter Detailed Revenue Transactions Dataset.
- [preprocess.ipynb](preprocess.ipynb): data preprocessing for Citations and Street Sweeping datasets, including filtering and dropping duplicates.
- [initial_possion.ipynb](initial_poisson.ipynb): attempted initial model utilizing Poisson regression in order to predict the number of citations on a particular street segment at a given time. This notebook was ultimately not included in the final analysis.
- [prob_e_and_i.ipynb](prob_e_and_i.ipynb): utilized the Citations and Street Sweeping dataset in order to estimate the probability of enforcement being on a steet while someone was illegally parked. 
- [prob_i.ipynb](prob_i.ipynb): utilized the Street Sweeping and Meter transactions/locations datasets in order to estimate the probability of someone being illegally parked.
- [final_probabilities.ipynb](final_probabilities.ipynb): used the final datasets from [prob_e_and_i.ipynb](prob_e_and_i.ipynb) and [prob_i.ipynb](prob_i.ipynb) to estimate our final probabilities of meter citations.
- [reformat_table.ipynb](reformat_table.ipynb): pivoted the dataset from [final_probabilities.ipynb](final_probabilities.ipynb) and added time lags in order to be in the correct format for creating the interactive map.
