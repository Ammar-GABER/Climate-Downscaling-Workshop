import xarray as xr
import pandas as pd
import numpy as np
import os

def precipitation_gcm_data(gcm_raw_dir='../../data/raw_gcm', station_metedata_path='../../data/station_data/station_metadata.csv', processed_gcm_dir='../../data/processed_gcm'):
     """
     Load raw GCM NetCDF files, extracts time series for each station using nearest neighbor,
     and perfroms uint conversiond.
     
     """
     print("Starting GCM data perprocessing ...")
     
     # Load station metadata
     station_metadata = pd.read_csv(station_metadata_path)
     stations = station.to_dict('records')
     print(f"Loaded metadata for {len(stations)} stations.")
     
     
     os.makdirs(processed_gcm_dir, exist_ok=True)
     
     # Define GCM models and process (adjust based on ypur downloads)
     # This list should match the files you actually download from ESGF
     
     gcm_configs= []
     
     for config in gcm_configs:
     	model = config['model']
     	scenario = config['scenario']
     	time_period = config['time_period']
     	
     	print(f"\nProcessing {model} - {scenario} ({time_period}) ...")
     	
     	# Define file patterns (adjust based on actual download file names)
     	# CMIP6 file naming convention: var_table_model_experiment_variant_grid_time.nc
     	# Example: tas_day_ACCESS-CM2_historical_r1i1p1f1_gn_19910101-19951231.nc
     	# We assume filess might be split by year or multi-year chuncks.
     	# Use glob to find all relevant files for the period
     	
     	# Adjust this glob pattern to match your download files
     	
     	tas_files = stored([os.path.join(gcm_raw_dir, f) for f in os.listdir(gcm_raw_dir) if f .startwith(f'tas_day_{model}_{scenario}_r1i1p1f1_gn_') and f .endwith('.nc')])
     	pr_files = stored([os.path.join(gcm_raw_dir, f) for f in os.listdir(gcm_raw_dir) if f .startwith(f'pr_day_{model}_{scenario}_r1i1p1f1_gn_') and f .endwith('.nc')])
     	
     	if not tas_files or not pr_files:
     		print(f" No GCM files found for {model} {scenario} in {gcm_raw_dir}. Skipping.")
     	
     	try:
     	     ds_tas = xr.open_mfdataset(tas_files, combine='by_coords'), decode_times=True)
     	     ds_pr = xr.open_mfdataset(pr_files, combine='by_coords', decode_time=True)
     	     print(f"  Loaded {len(tas_files)} TAS files and {len(pr_files)} PR files.")
     	 except Exception as e:
     	     print(f"  Error loading GCM files for {model} {scenario}: {e}. Skipping.")
     	     continue
     	 
     	 # Select relevant time period
     	 
     	 start_date _str, end_date_str = time_period.split('-')
     	 ds_tas = ds_tas.sel(time=slice(start_date_str, end_date_str))
     	 ds_pr = ds_pr.sel(time-slice(start_date_str, end_date_str))
     	 print(f"  Subsetted data to {start_date_str} to {end_date_str}.")
     	 
     	 # Extract data for each station using nearest neighbor
     	 extracted_data_list = []
     	 for station in stations:
     	     stn_id = station
     	     stn_lat = station['Latitude]
     	     stn_lon = station['Longitude']
     	     
     	     # Use .sel(method='nearest') for nearest neighbor extraction
     	     # Ensure longitude is in 0-360 if GCM uses that, or -180 to 180 if GCM uses that.
     	     # Most CMIP6 data is -180 to 180.
     	     
     	     
     	     try:
     	         # Extract temperature
     	         tas_series = ds_tas['tas'].sel(lat=stn_lat, lon=stn_lon, method='nearest')
     	         # Convert Kelvin to Celsius: K - 273.15
     	         tas_series_C = tas_series - 273.15
     	         tas_series_C.name = 'Temperature_C'
     	         
     	         
     	         # Extract precipitation
     	         pr_series = ds_pr['pr'].sel(lat=stn_lat, lon=stn_lon, method='nearest')
     	         # Convert kg m-2 s-1 to mm day-1: kg m-2 s-1 * 86400
     	         per_series_mm_day = pr_series * 86400
     	         per_series_mm_day.name = 'Precipitation_mm_day'
     	         
     	         df_extracted = pd.DataFrame({
     	             'Date': tas_series.time.values,
     	             'Station_ID': stn_id,
     	             'Latitude': tas_series.lat.item(), # GCM grid point lat
     	             'Longitude': tas_series.lon.item(), # GCM grid lon
     	             'Temperature_C': tas_series_C.values,
     	             'Precipitation_mm_day': pr_series_mm_day.values   	         
     	         })
     	         
     	         extractedP_data_list.append(df_extracted)
     	         print(f"   Extracting data for {stn_id}.")
     	     except KeyError as e:
     	         print(f"    Extracting data for {stn_id} (variable not found or coordinate issue): {e}")
     	         except Exception as e:
     	             print(f"     An unexpected error occurred for {stn_id}: {e}")
     	     if extracted_data_list:
     	         combined_extracted_df = pd.concat(extracted_data_list, ignore_index=True)
     	         output_filename = f"gcm_extracted_{model}_{scenario}_{time_peeriod}.csv"
     	         output_path = os.path.join(processed_gcm_dir, output_filename)
     	         combined_extracted_df.to_csv(output_path, index=False)
     	         print(f"     Combined extracted GCM data saved to :{output_path}")
     	     else:
     	         print(f"     No data extracted for {model} {scenario}. Check GCM files and station coordinates.")
if __name__ == "__main__":
    # Ensure raw GCM data is downloaded and station metadata is generated first.
    # Run 01_generate_station_data.py before this script.
    # Place your download CMIP6 NetCDF files in data/raw_gcm/
    
    preprocess_gcm_data()
     	     
     	     
     	     
     	     
     	     
     	     
     	     
     	     
     	     
     	     
     	     
     	     
     	     
     	
