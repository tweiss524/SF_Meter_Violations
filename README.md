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
- [eda.ipynb](notebooks/eda.ipynb): compilation of basic EDA performed on the SFMTA Parking Citations Dataset used for presentation purposes.
- eda_\[name\].ipynb: basic EDA performed by each member of the group.
- [meter_eda.ipynb](notebooks/meter_eda.ipynb): basic EDA performed on the SFMTA Parking Meter Detailed Revenue Transactions Dataset.
- [preprocess.ipynb](notebooks/preprocess.ipynb): data preprocessing for Citations and Street Sweeping datasets, including filtering and dropping duplicates.
- [initial_possion.ipynb](notebooks/initial_poisson.ipynb): attempted initial model utilizing Poisson regression in order to predict the number of citations on a particular street segment at a given time. This notebook was ultimately not included in the final analysis.
- [prob_e_and_i.ipynb](notebooks/prob_e_and_i.ipynb): utilized the Citations and Street Sweeping dataset in order to estimate the probability of enforcement being on a steet while someone was illegally parked. 
- [prob_i.ipynb](notebooks/prob_i.ipynb): utilized the Street Sweeping and Meter transactions/locations datasets in order to estimate the probability of someone being illegally parked.
- [final_probabilities.ipynb](notebooks/final_probabilities.ipynb): used the final datasets from [prob_e_and_i.ipynb](notebooks/prob_e_and_i.ipynb) and [prob_i.ipynb](notebooks/prob_i.ipynb) to estimate our final probabilities of meter citations.
- [reformat_table.ipynb](notebooks/reformat_table.ipynb): pivoted the dataset from [final_probabilities.ipynb](notebooks/final_probabilities.ipynb) and added time lags in order to be in the correct format for creating the interactive map.

# Analysis

The goal was to calculate the probability of getting a parking ticket given a street section and day of the week/time of day and given someone has not paid the meter. To do this, we divide each 24 hour day into fifteen minute time bins, conditioning on this as well as a street segment and weekday (e.g. probability of getting a citation from 9:00-9:15am on a typical Friday on street segment $A$).

In terms of notation, define
- Weekday: $W \in \{\text{Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday}\}$
- Street Segment: $S \in \{1, 2, \dots, N\}$ where $N$ is the number of unique streets
- Start of Time Interval (15 minute increments): $T \in \{9\text{:}00 \text{am}, 9\text{:}15 \text{am}, 9\text{:}30 \text{am}, \dots, 5\text{:}45 \text{pm}\}$
- $E = \text{event that enforcement happens}$
- $I = \text{event that illegal parking happens}$

Then, the probability of getting a ticket given a time bin $T$, a street segment $S$, and a day of week $W$ is denoted as 
    $$p_{t, s, w} = P(E \mid I, T = t, S = s, W = w) = \frac{P(E \cap I \mid T = t, S = s, W = w)}{P(I \mid T = t, S = s, W = w)}$$

The following formula was used to empirically calculate an estimate of the numerator as carried out in [prob_e_and_i.ipynb](notebooks/prob_e_and_i.ipynb):
$$\widehat{P(E \cap I \mid T = t, S = s, W = w)} = \frac{\sum\limits_{\text{weekday(date)} = w} \mathbbm{1}[\text{num tickets}(s, t, \text{date}) > 0]}{\text{num\_weekday(date)} = w}$$

The following formula was used to empirically calculate an estimate of the denominator as carried out in [prob_i.ipynb](notebooks/prob_i.ipynb):

$$\widehat{P(I \mid T = t, S = s, W = w)} = \frac{\sum\limits_{\text{weekday(date)} = w} \mathbbm{1}[\text{num unpaid meters}(s, t, \text{date}) > 0]}{\text{num\_weekday(date)} = w}$$

To give an interpretation of these formulas, first consider the numerator. We have that each citation that occurred on day $w$ in street segment $s$ was assigned to a corresponding 15 minute bin. If there were multiple tickets on the same day in the same time bin, we recorded only one ticket, thus giving the indicator of there being at least one instance of enforcement and illegal parking. Lastly, the number of tickets in each time bin $t$ was summed and divided by the total number of weekdays corresponding to day $w$ in the dataset, thus giving an estimate of the numerator. Figure 4 shows a visual representation of how this was calculated:
    \makebox[\textwidth][c]{\includegraphics[width=1.1\textwidth]{numerator_analysis.png}}
    \caption{A simple example estimating the numerator where $W=$ Wednesday on one particular street segment.}
    
Now, considering the denominator, we have that for a street segment $s$ and weekday $w$, the 15 minute time bins that each transaction covers for each meter on street $s$ was recorded. If there were no transactions that covered a 15 minute time bin, or if there were gaps in transactions that exceeded a 3 minute grace period (time allowed for one car to leave and another car to park and pay), we considered the meter to have been unpaid during that time bin.  Next, we aggregated all the time intervals for when there was at least one unpaid meter and used this to generate an indicator of an unpaid meter for the corresponding time bin on street $s$. Lastly, these indicators were summed up over all weekdays corresponding to day $w$ and divided by the total number of weekdays corresponding to day $w$ in the dataset, thus giving an estimate of the denominator. Figure 5 shows a visual representation of how this was calculated over one day:
    \makebox[\textwidth][c]{\includegraphics[width=1.1\textwidth]{denominator_analysis.png}}
    \caption{A simple example estimating the denominator where $W=$ Wednesday on one particular street segment.}
    
In devising this model, the following assumptions were made. The first is that at any given time, every metered spot available will be filled. In this sense, the assumption is made that if there are any meters not being paid for on a particular street segment during a particular time interval, then we conclude that there is someone parking illegally (this is not always true and thus results in many underestimated probabilities). The second assumption is that parking enforcement will spend at most fifteen minutes on a street segment. The final assumption is that if parking enforcement is on a street segment, they will ticket all cars violating parking regulations with 100$\%$ certainty.
