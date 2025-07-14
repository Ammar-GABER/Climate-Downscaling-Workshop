import xarray as xr
import pandas as pd
import numpy as np
from cmethods import adjust       # For bias correction
import os

def perform_bias_correction(
    station_data_path = '../../data/station_data/generated_station_data.csv',
    processed_gcm_dir= '../../data/processed_gcm',
    output_dir = '../../output/bias_corrected'
):
    """
    Performs bias correction using Quantile Mapping from python-cmethods library.
    Trains on hostorical period (1991-2020) and applies to future scenarios (2041-2070) 
    """
    print("Starting bias correction using python-cmethods library ....")
    
    # Load observed station data
    obs_df = pd.read_csv(station_data_path, parse_dates=True)
    obs_df = obs_df.set_index('Date')
    print(f"   Loaded observed data for {obs_df.unique()} stations.")
    
    os.makedirs(output_dir, exist_ok= True)
    
    # Define historical and future periods
    historical_period = '1991-2020'
    future_period = '2041-2070'           # Example future period
    
    # Define GCM models and scenarios to process (must match preprocessed files)
    
    gcm_config= []
    
    # Group GCM data by model for eaiser processing
    gcm_data_by_model = {}
    for config in gcm_config:
        model = config['model']
        scenario = config['scenario']
        time_period = config['time_period']
        filename = f"gcm_extracted_{model}_{scenario}_{time_period}.csv"
        filepath = os.path.join(processed_gcm_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: Preprocessed GCM file not found: {filepath}. Skipping this config.")
            continue
        df = pd.read_csv(filepath, parse_dates = True)
        df = df.set_index('Date')
        
        if model not in gcm_data_by_model:
            gcm_data_by_model[model] = {}
        gcm_data_by_model[model][(scenario, time_period)] = df
        
    if not gcm_data_by_model:
        print("No preprocessed GCM data to perfrom bias correction. Exiting.")
        return
        
    # Loop through each model, station, and variable
    for model, scenarios_data in gcm_data_by_model.items():
        print(f"\nProcessing bias correction for model: {model}")
        
        # Get historical GCM data for training
        hist_key = ('historical, historical_period')
        if hist_key not in scenarios_data:
            print(f"    Historical data for {model} not found. Skpping bias correction for this model.")
            continue
        gcm_hist_df = scenarios_data[hist_key]
        
        # Get unique station IDs from observed data
        station_ids = obs_fd.unique()
        
        for stn_id in station_ids:
            print(f"     Bias correction for station: {stn_id}")
            obs_stn = [obs_df == stn_id]
            gcm_hist_stn = [gcm_hist_df == stn_id]
            
            # Convert observations and model data to xarray DataArray for cmethods
            # Ensure 'time' dimension is present and data is aligned
            
            obs_tas_xr = obs_stn['Temperature_C'].to_xarray().rename({'Date': 'time'})
            obs_pr_xr = obs_stn['Precipitation_mm_day'].to_xarray().rename({'Date':'time'})
            
            gcm_hist_tas_xr = gcm_hist_stn.to_xarray().rename({'Date':'time'})
            gcm_hist_pr_xr = gcm_hist_stn['Precipitation_mm_day'].to_xarray().rename({'Date':'time'})
            
            
            # Ensure data is by time
            obs_tas_xr = obs_tas_xr.sortby('time')
            obs_pr_xr = obs_pr_xr.sortby('time')
            gcm_hist_tas_xr = gcm_hist_tas_xr.sortby('time')
            gcm_hist_pr_xr = gcm_hist_pr_xr.sortby('time')
            
            # Apply bias correction for future scenarios (and historical for aevaluation purposes)
            for (scenario, period), gcm_sim_df in scenarios_data.items():
                gcm_sim_stn = [gcm_sim_df == stin_id]
                gcm_sim_tas_xr = gcm_sim_stn.to_xarray().rename({'Date':'time'})
                gcm_sim_pr_xr = gcm_sim_stn['Precipitation_mm_day'].to_xarray().rename({'Date':'time'})
                
                gcm_sim_tas_xr = gcm_sim_tas_xr.sortby('time')
                gcm_sim_pr_xr = gcm_sim_pr_xr.sortby('time')
                
                # --- Temperature Bias Correction (Quantile Mapping, Additive) -----#
                try:
                    bc_tas = adiust(
                        method= "quantile_mapping",
                        obs = obs_yas_xr,
                        simh = gcm_hist_tas_xr,
                        simp = gcm_sim_tas_xr,
                        kind = "+",             # Additive correction for temperature
                        group = "time.month"     # Apply monthly  
                    )
                    bc_tas_df = bc_tas.to_dataframe(name='Temperature_C_BC')
                    bc_tas_df = stn_id
                    bc_tas_df = scenario
                    bc_tas_df['Model'] = model
                    bc_tas_df['Variable'] = 'Temperature_C'
                    
                    # Save raw GCM data for comparison
                    raw_tas_df = gcm_sim_tas_xr.to_dataframe(name='Temperature_C_Raw')
                    raw_tas_df = stn_id
                    raw_tas_df = dcenario
                    raw_tas_df['Model'] = model
                    raw_tas_df['Variable'] = 'Temperature_C'
                    
                    # Combine raw and bias-corrected for this station/scenario/model
                    combined_tas_df = pd.merge(raw_tas_df, bc_tas_df, left_index = True, right_index=True, how='outer')
                    combined_tas_df = combined_tas_df.reset_index().rename(columns={'index':'Date'})
                    combined_tas_df.to_csv(os.path.join(output_dir, f'temp_bc_{model}_{scenario}_{stn_id}.csv'), index = False)
                    print(f"  Temperature BC saved for {stn_id} ({scenario}).")
                    
                except Exception as e:
                    print(f"  Error in Temperature BC {stn_id} {scenario} : {e}")
                # --- Precipitation Bias Correction (Quantile Mapping, Multiplicative) ----#
                try:
                    # cmethods' quantile_mapping handles zeros by default for multiplicative kind
                    bc_pr = adjust(
                        method= "quantile_mapping",
                        obs = obs_pr_xr,
                        simh = gcm_hist_pr_xr,
                        simp = gcm_sim_pr_xr,
                        kind = "*",            # Multiplicative correction for precipitation
                        group = "time.month"    # Apply monthly  
                    )        
                    bc_pr_df = bc_pr.to_dataframe(name='Precipitation_mm_day_BC')
                    bc_pr_df = stn_id
                    bc_pr_df = scenario
                    bc_pr_df['Model'] = model
                    bc_pr_df['Variable'] = 'Precipitation_mm_day'
                    
                    
                    # Save raw GCM data for comparison
                    raw_pr_df = gcm_sim_pr_xr.to_dataframe(name='Precipitation_mm_day_Raw')
                    raw_pr_df = stn_id
                    raw_pr_df = scenario
                    raw_pr_df['Model'] = model
                    raw_pr_df['Variable'] = 'Precipitation_mm_day'
                    
                    
                    # Combine raw and bias-corrected for this station/scenario/model
                    combined_pr_df = pd.merge(raw_pr_df, bc_pr_df, left_index=True, right_index=True, how='outer')
                    combined_pr_df = combined_pr_df.reset_index().rename(columns={'index':'Date'})
                    combined_pr_df.to_csv(os.path.join(output_dir, f'precip_bc_{model}_{scenario}_{stn_id}.csv'), index=False)
                    print(f"    Precipitation BC saved for {stn_id} {scenario}.")
                    
                except Exception as e:
                    print(f"    Error in Precipitation BC for {stn_id} {scenario}: {e}")
                    
if __name__ == "__main__":
    # Ensure station data and preprocessed GCM data are available
    # Run 01_generate_station_data.py and 02_gcm_preprocessing.py before this script
    perform_bias_correction()
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
