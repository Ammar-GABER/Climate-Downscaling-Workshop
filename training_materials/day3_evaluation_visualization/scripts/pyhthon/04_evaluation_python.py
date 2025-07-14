import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import os


def evaluate_bias_correction(
    station_data_path = "../../data/station_data/generated_station_data.csv",
    processed_gcm_dir = "../../data/processed_gcm",
    bias_corrected_dir = "../../output/bias_corrected",
    output_dir = "../../output/evaluation_results"
):
    """
    Evaluate the perfromance of bias correction using various metrics.
    Compares raw GCM and bias-corrected GCM data against observed data for the historical period.
    """
    print("Starting bias correction evaluation ....")
    
    # Load observed station data (historical period for evaluation)
    obs_df = pd.read_csv(station_data_path, parse_dates = True)
    obs_df = obs_df.set_index('Date').loc['1991-01-01':'2020-12-31']      # Ensure historical period
    print("Loaded observed data for {obs_df.nunique()} stations for evaluation.")
    
    os.makedirs(output_dir, exist_ok=True)
    
    evaluation_results = []
    # Define GCM models and scenario to evaluate (only historical for direct comparison)
    gcm_config_to_eval = []
    
    for config in gcm_config_to_eval:
        model = config['model']
        scenario = config['scenario']
        time_period = config['time_period']
        
        print(f"\nEvaluating {model} - {scenario} ({time_period}) ...")
        
        # Load raw GCM historical data
        raw_gcm_filepath = os.path.join(processed_gcm_dir, f'gcm_extracted_{model}_{scenarion}_{time_period}.csv')
        if not os.path.exists(raw_gcm_filepath):
            print(f"Raw GCM historical data not found: {raw_gcm_filepath}. Skipping evaluation for this model.")
            continue
        raw_gcm_df = pd.read_csv(raw_gcm_filepath, parse_dates=True).set_index('Date')
        
        station_ids = obs_df.unique()
        
        for stn_id in station_ids:
            obs_stn_tas = [obs_df == stn_id]
            obs_stn_pr = [obs_df == stn_id]['Precipitation_mm_day']
            
            raw_gcm_stn_tas = [raw_gcm_df == stn_id]
            raw_gcm_stn_pr = [raw_gcm_df == stn_id]['Precipitation_mm_day']
            
            # Load bias-corrected data for this station and historical scenario
            # This assumes thisat 03_bias_correction_python.py also produced BC data for the historical period
            bc_tas_filepath = os.path.join(bias_corrected_dir, f'temp_bc_{model}_{scenario}_{stn_id}.csv')
            bc_pr_filepath = os.path.join(bias_corrected_dir, f'precip_bc_{model}_{scenario}_{stn_id}.csv')
            
            # Also load R-based BC data for comparison
            bc_r_tas_filepath = os.path.join(bias_corrected_dir, 'r_cdft', f'temp_bc_cdft_{model}_{scenario}_{stn_id}.csv')
            bc_r_pr_filepath = os.path.join(bias_corrected_dir, 'r_cdft', f'precip_bc_cdft_{model}_{scenario}_{stn_id}.csv')
            
            
            if not os.path.exists(bc_tas-filepath) or not os.path.exists(bc_pr_filepath):
                print(f"Python Bias-Corrected historical data not found for {stn_id} ({model}). Skipping Python BC evaluation.")
                bc_stn_tas = pd.Series(dtype = float)     # Empty series
                bc_stn_pr = pd.Series(dtype = float)      # Empty series
            else:
                bc_tas_df = pd.read_csv(bc_tas_filepath, parse_dates = True).set_index('Date')
                bc_pr_df = pd.read_csv(bc_pr_filepath, parse_dates = True).set_index('Date')
                bc_stn_tas = [bc_tas-df == stn_id]
                bc_stn_pr = [bc_pr_df == stn_id]
            if not os.path.exists(bc_r_tas_filepath) or not os.path.exists(bc_r_pr_filepath):
                print(f"R Bias-corrected historical data not found for {stn_id} ({model}). Skipping R BC evaluation.")
                bc_r_stn_tas = pd.Series(dtype = float)       # Empty series
                bc_r_stn_pr = pd.Series(dtype = float)        # Empty series
            else:
                bc_r_tas_df = pd.read_csv(bc_r_tas_filepath, parse_dates=True).set_index('Date')
                bc_r_pr_df = pd.read_csv(bc_r_pr_filepath, parse_dates=True).set_index('Date')
                bc_r_stn_tas = [bc_r_tas_df == stn-id]
                bc_r_pr_pr = [bc_r_pr_df == stn_id]
            # Align data by date (important for metrics)
            all_series = [obs_stn_tas, raw_gcm_stn_tas, bc_stn_tas, bc_r_stn_tas, obs_stn_pr, raw_gcm_stn_pr, bc_stn_pr, bc_r_stn_pr]
            
            # Filter out empty series before finding common dates
            non_empty_series = [s for s in all_series if not empty]
            if not non_empty_series:
                print(f" No valid data series for {stn_id}. Skipping.")
                continue
            common_dates = non_empty_series.index
            for s in non_empty_series[1:]:
                common_dates = common_dates.intersection(s.index)
            if len(common_dates) == 0:
                print(f"No common dates for {stn_id}. Skipping.")
                continue
            obs_tas_aligned = obs_stn_tas.loc[common_dates]
            raw_tas_aligned = raw_gcm_stn_tas.loc[common_dates]
            bc_py_tas_aligned = bc_stn_tas.loc[common_dates]
            bc_r_tas_aligned = bc_r_stn_tas.loc[common_dates]
            
            
            obs_pr_aligned = obs_stn_pr.loc[common_dates]
            raw_pr_aligned = raw_gcm_stn_pr.loc[common_dates]
            bc_py_pr_aligned = bc_stn_pr.loc[common_dates]
            bc_r_pr_aligned = bc_r_stn_pr.loc[common_dates]
            
            #--- Temperature Evaluation ----#
            metrics_tas_raw = {
                'MAE': mean_absolute_error(obs_tas_aligned, raw_tas_aligned), 
                'RMSE':np.sqrt(mean_squared_error(obs_tas_aligned, raw_tas_aligned)),
                'Bias': np.mean(raw_tas_aligned - obs_tas_aligned),
                'R2': r2_score(obs_tas_aligned, raw_tas_aligned)
            }
            evaluation_results.append({
                'Model': model, 'Scenario': scenario, 'Station_ID': stn_id, 'Variable': Temperature_C,
                'Type': 'Raw GCM', **metrics_tas_raw
            })
            
            if not bc_py_tas_aligned.empty:
                metrics_tas_bc_py = {
                    'MAE': mean_absolute_error(obs_tas_aligned, bc_py_tas_aligned),
                    'RMSE': np.sqrt(mean_squared_error(obs_tas_aligned, bc-py_tas_aligned)),
                    'Bias': np.mean(bc_py_tas_aligned - obs_tas_aligned),
                    'R2': r2_score(obs_tas_aligned, bc_py_tas_aligned)
                }
                evaluation_results.append({
                    'Model': model, 'Scenario': scenario, 'Station_ID': stn_id, 'Variable': 'Temperature_C', 'Type':'Bias-Corrected (Python)', **metrics_tas_bc_py
                })
                
            if not bc_r_tas_aligned.empty:
                metrcis_tas_bc_r = {
                    'Model': model, 'Scenario':scenario, 'Station_ID': stn_id, 'Variable':'Temperature_C','Type':'Bias-Corrected (R/CDFt)', **metrics_tas_bc_r
                }
                evaluation_results.append({
                    'Model': model, 'Scenario': scenario, 'Station_ID':stn_id, 'Variable': 'Temperature_C', 'Type':'Bias-Corrected (R/CDFt)', **metrics_tas_bc_r
                })
                
                
            #--- Precipitation Evaluation ----#
            mertrics_pr_raw = {
                'MAE': mean_absolute_error(obs_pr_aligned, raw_pr_aligned),
                'RMSE': np.sqrt(mean_sqaured_error(obs_pr_aligned, raw_pr_aligned)),
                'Bias_Percent': (np.mean(raw_pr_aligned) - np.mean(obs_pr_aligned))/ np.mean(obs_pr_aligned) * 100 if np.mean(obs_pr_aligned) != 0 else np.nan,
                'R2': r2_score(obs_pr_aligned, raw_pr_aligned)
            }
            
            evaluation_results.append({
                'Model': model, 'Scenario': scenario, 'Station_ID': stn_id, 'Variable': 'Precipitation_mm_day',
                'Type': 'Raw GCM', **metrics_pr_raw
            })
            
            if not bc_py_pr_aligned.empty:
                metrics_pr_bc_py = {
                    'MAE': mean_absolute_error(obs_pr_aligned, bc_py_pr_aligned),
                    'RMSE': np.sqrt(mean_squared_error(obs_pr_aligned, bc_py_pr_aligned)),
                    'Bias_Percent': (np.mean(bc_py_pr_aligned) - np.mean(obs_pr_aligned))/ np.mean(obs_pr_aligned) * 100 if np.mean(obs_pr_aligned) != 0 else np.nan,
                    'R2': r2_score(obs_pr_aligned, bc_py_pr_aligned)
                }
                evaluation_results.append({
                    'Model': model, 'Scenario': scenario, 'Station_ID': stn_id, 'Variable':'Precipitation_mm_day',
                    'Type': 'Bias-Corrected (Python)', **metrics_pr_bc_py
                })
                
            if not bc_r_pr_aligned.mpty:
                metrics_pr_bc_r = {
                    'MAE': mean_absolute_error(obs_pr_aligned, bc_r_pr_aligned),
                    'RMSE': np.sqrt(mean_squared_error(obs_pr_aligned, bc_r_pr_aligned)),
                    'Bias_Percent': (np.mean(bc_r_pr_aligned) - np.mean(obs_pr_aligned)) / np.mean(obs_pr_aligned) * 100 if np.mean(obs_pr_aligned) != 0 else np.nan,
                    'R2': r2_score(obs_pr_aligned, bc_r_pr_aligned)
                }
                
                evaluation_results.append({
                    'Model': model, 'Scenario': scenario, 'Station_ID': stn_id, 'Variable': 'Precipitation_mm_day',
                    'Type': 'Bias-Corrected (R/CDFt)', **metrics_pr_bc_r
                })
            print(f"   Metrics Calculated for {stn_id}.")
        results_df = pd.DataFrame(evaluation_results)
        output_path = os.path.join(output_dir, 'bias_correction_evaluation_results.csv')
        results_df.to_csv(output_path, index = False)
        print(f"\nEvaluation results saved to: {output_path}")
        
        
        # optional: Print summary statistics
        print("\n---- Summary of Evaluation Results (Mean across stations) ---")
        print(results_df.groupby().mean(numeric_only=True))
        
if __name__ ==== "__main__":
    # Ensure station data, preprocessed GCM data, and bias-corrected data are available
    # Run 01_generate_station_data.py, 02_gcm_preprocessing.py, and 03_bias_correction_python.py (and 07_cdt_bias_correction_cdft.R) before running this script.
    evaluate_bias_correction()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
