import pandas as pd
import numpy as np
import os

def generate_station_data(num_station=40, start_date='1991-01-01', end_date='2020-12-31', output_dir='../../Data/station_data'):
     """
generate synthetic daily surface temperature and precipitation data for agiven number of stations.
Stations are randomly placed within Sudan's approximate bounding box.
Temperature follows a sinusoidal pattern with noise.
Precipitation follows a gamma distribution with wet/dry days.
     """

     print(f"Generate synthetic data for {num_station} stations from {start_date} to {end_date} ....")

     # Approximate bounding box for Sudan
     min_lat, max_lat = 8.6, 23.4
     min_lon, max_lon =  20.2, 39.8

     dates = pd.date_range(start=start_date, end=end_date, freq='D')
     num_days = len(dates)

     station_data_list = []
     station_metadata = []
     for i in range(num_stations):
   	station_id = f'STN_{i+1:02d}'
   	lat = np.random.uniform(min_lat, max_lat)
   	lon = np.random.uniform(min_lon, max_lon)
   


   	# Generate temperature (sinusoidal + noise)
   	# Annual cycle (approximate for tropical region)
   
   	day_of_year = dates.dayofyear
   	temp_annual_cycle = 25 + 5 * np.sin(2*np.pi*(day_of_year - 80)/365.25)  # Mean 25C amplitude 5C
   	temp_noise = np.random.normal(0, 2, num_days)     # Daily noise
   	temperature = temp_annual_cycle + temp_noise
   
   	# Generate precipitation (wet/dry days + gamma distribution for wet days)
  	 wet_day_prob = 0.3         # Probability of a wet day
   	precipitation = np.zeros(num_days)
   	wet_days_indices = np.random.rand(num_days) < wet_prob
   
   	# Gamma distribution parameters for wet days (shape, noise)
   	# Adjust parameters to get plausible daily rainfall amoiunts (e.g., mean 5-10 mm/day on wet days)
   	# For gamma distribution, mean = shape * scale
   	# Let's aim for a mean of 8 mm on wet days. If shape = 2, then scale = 4.
   
   	precipitation [wet_days_indices] = np.random.gamma(shaape=2, scale=4, size=wet_day_indices.sum())
   
   	# Ensure no negative values for precipitation
   	precipitation[precipitation < 0] = 0
   
   	df_station = pd.DataFrame({
   	    'Date': dates,
   	    'Station_ID': station_id,
   	    'Latitude': lat,
   	    'Longitude': lon,
   	    'Temperature_C': temperature,
   	    'Precipitation_mm_day': precipitation  
   	})
   	station_data_list.append(df_station) 
     full_df = pd.concat(station_data_list, ignor_index=True)

     # Save to CSV

     os.makedirs(output_dir, exist_ok=True)
     output_path = os.path.join(output_dir, 'generated_station_data.csv')
     full_df.to_csv(output_path, index=False)

     print(f"Generated station data saved to: {output_path}")

     # Save station metadata separately for easier access
     metadata_ddf = pd.DataFrame(station_metadata)
     metadata_path = os.path.join(output_dir, 'station_metadata.csv')
     metadata_df.to_csv(metadata_path, index=False)
     print(f"Station metadata saved to : {metadata_path}")
if __name__ == "__main__":
     generate_station_data()





















