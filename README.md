# Bixi Most Popular Rides 2019/2020

This project analyzes bixi's most popular rides from 2019 and 2020. 

The data used for that project was obtained from bixi's website. A 5M rows dataset describing every single ride on the network for each year.

The data was processed by compute_top_routes.py to generate the top 100 or 500 most popular routes by bixi's users (members and non-members). The generated data can be found in ./results subdirectory.

This data was then visualized using Tableau to create an interactive map of Montreal showcasing the most popular routes, by ride duration, member or non-member, and time period.

## Project Intention

You can run and use the python script. However, you will have to change the hardcoded year and length of the top routes generated. 

The purpose of this repository is mostly to visualize the data using the Tableau Workbook 'most_popular_route_analysis.twb'.

NOTE:
Popular rides which have the same starting and ending bixi station is not an anomaly. They mostly represent tourists going on a loop ride around a popular area.