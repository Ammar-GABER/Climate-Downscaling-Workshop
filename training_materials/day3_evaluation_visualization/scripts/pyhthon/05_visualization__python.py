import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import os

def visualize_results(
    station_data_path ='../../data/station_data/generated_station_data.csv',
    processed_gcm_dir = '../../data/processed_gcm',
    bias_corrected_dir = '../../output/bias_corrected',
    output_dir = '../../output/plots'
):
    """
    Generates time series plots, spatial maps, and distribution plots.    
    """
    print("Starting visualization of results ...")
    os.makedirs(output_dir, exists_ok = True)
    
    # Load observed station data
    obs_df = pd.read_csv(station_data_path, parse_dates= True)
    obs_df = obs_df.set_index('Date')
    station_metadata = obs_df.drop_duplicates().set_index('Station_ID')
    
    # Select a few stations for time series and distribution plots
    selected_stations = station_metadata.sample(3, random_state = 42).index.tolist()  # Randomly pick 3 stations for reproducibility
    print(f"Selected stationd for detailed plots: {selected_stations}")
    
    # Define GCM model and scenarios to visualize
    model_to_visualize = 'ACCESS-CM2'        # Choose one model for visualization
    scenarios_to_visualize = ['historical', 'ssp245', 'ssp585']
    historical_period = '1991-2020'
    future_period = '2041-2070'
    
    # --- 1. Time Series Plots (for selected stations) -----
    print("\nGenerating time series plots ...")
    for stn_id in selected_stations:
        obs_stn_df = [obs_df == stn_id]
        
        for var in:
            plt.figure(figsize=(12,6))
            plt.plot(obs_stn_df.index, obs_stn_df[var], label='Obsered', color='black', linewidth=1)
            
            for scenario in scenarios_to_visualize:
                period = historical_period if scenario == 'historical' else future_period
                
                # Load raw GCM data
                raw_gcm_filepath = os.path.join(processed_gcm_dir, f'gcm_extracted_{model_to_visualize}_{scenario}_{period}.csv')
                if os.path.exists(raw_gcm_filepath):
                    raw_gcm_df = pd.read_csv(raw_gcm_filepath, parse_dates=True).set_index('Date')
                    raw_gcm_stn_df = [raw_gcm_df == stn_id]
                    plt.plot(raw_gcm_stn_df.index, raw_gcm_stn_df[var], label='Raw GCM ({scenario})', linestyle='--', alpha=0.7)
                    
                # Load Python bias-corrected GCM data
                bc_py_filepath = os.path.join(bias_corrected_dir, f'{var.split("_").lower()}_bc_{model_to_visualize}_{scenario}_{stn_id}.csv')
                if os.path.exissts(bc_py_filepath):
                    bc_py_df = pd.read_csv(bc_py_filepath, parse_dates=True).set_index('Date')
                    bc_py_df = [bc_py_df == stn_id]]
                    plt.plot(bc_py_stn_df.index, bc_py_stn_df, label= f'BC (Python) ({scenario})', linestyle="-", alpha=0.8)
                    
                # Load R CDFt bias-corrected GCM data
                bc_r_filepath = os.path.join(bias_corrected_dir, 'r_cdft', f'{var.split("_").lower()}_bc_cdft_{model_to_visualize}_{scenario}_{stn_id}.csv')
                if os.path.exists(bc_r_filepath):
                    bc_r_df = pd.read_csv(bc_r_filepath, parse_dates=True).set_index('Date')
                    bc_r_stn_df = [bc_r_df == stn_id]
                    plt.plot(bc_r_stn_df.inde, bc_r_stn_df, label= f'BC (R'CDFt) ({scenario})', linestyle=':', alpha=0.8)
                    
            plt.title(f'{var} Time Series for Station {stn_id} ({model_to_visualize})')
            plt.xlabel('Date')
            plt.ylabel(f'{var} {"(°C)" if "Temperature" in var else "(mm/day)"}')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'timeseries_{var.split("_").lower()}_{stn_id}.png'))
            plt.close()
            print(f"    Saved time series for {var} at {stn_id}.")
            
            
    # ---- 2. Spatial Maps (Mean Temperature/Precipitation for Historical Period) ----
    print("\nGenerating spatial maps ....")
    
    # Calculate mean for observed data (1991-2020)
    obs_mean_temp = obs_df.loc[historical_period].groupby('Station_ID').mean()
    obs_mean_pr = obs_df.loc[historical_period].groupby('Station_ID')['Precipitation_mm_day'].mean()
    
    # Get GCM historical data (raw) for spatial comparison
    raw_gcm_hist_df = pd.read_csv(os.path.join(processed_gcm_dir, f'gcm_extracted_{model_to_visualize}_historical_{historical_period}.csv'), parse_dates=True).set_index('Date')
    
    # For bias-corrected historical, we need to aggregate the station-wise BC files.
    bc_hist_temp_dfs_py = []
    bc_hist_pr_dfs_py = []
    bc_hist_temp_dfs_r = []
    bc_hist_pr_dfs_r = []
    
    for stn_id in station_metadata.index:
        # Python BC
        temp_bc_py_path = os.path.join(bias_corrected_dir, f'temp_bc_{model_to_visualize}_historical_{stn_id}.csv')
        pr_bc_py_path = os.path.join(bias_corrected_dir, f'precip_bc_{model_to_visualize}_historical_{stn_id}.csv')
        
        if os.path.exists(temp_bc_py_path):
            bc_hist_temp_dfs_py.append(pd.read_csv(temp_bc_py_path, parse_dates=True))
        if os.path.exists(pr_bc_py_path):
            bc_hist_pr_dfs_py.append(pd.read_csv(pr_bc-py_path, parse_dates=True))
            
        # R CDFt BC
        temp_bc_r_path = os.path.join(bias_corrected_dir, 'r_cdft', f'temp_bc_cdft_{model_to_visualize}_historical_{stn_id}.csv')
        pr_bc_r_path = os.path.join(bias_corrected_dir, 'r_cdft', f'precip_bc_cdft_{model_to_visualize}_historical_{stn_id}.csv')
        if os.path.exists(temp_bc_r_path):
            bc_hist_temp_dfs_r.append(pd.read_csv(temp_bc_r_path, parse_dates=True))
        if os.path.exists(pr_bc_r_path):
            bc_hist_pr_dfs_r.append(pd.read_csv(pr_bc_r_path, parse_dates=True))
        
    bc_mean_temp_py = pd.Series(dtype=float)
    bc_mean_pr_py = pd.Series(dtype=float)
    bc_mean_temp_r = pd.Series(dtype=float)
    bc_mean_pr_r = pd.Series(dtype=float)
    
    if bc_hist_temp_dfs_py:
        bc_hist_temp_df_all_py = pd.concat(bc_hist_temp_dfs_py).set_index('Dae')
        bc_mean_temp_py = bc_hist_temp_df_all_py.loc[historical_period].groupby('Station_ID').mean()
    if bc_hist_pr_dfs_py:
        bc_hist_pr_df_all_py = pd.concat(bc_hist_pr_dfs-py).set_index('Date')
        bc_mean_pr_py = bc_hist_pr_df_all_py.loc[historical_period].groupby('Station_ID').mean()
    
    if bc_hist_temp_dfs_r:
        bc_hist_temp_df_all_r = pd.concat(bc_hist_temp_dfs_r).set_index('Date')
        bc_mean_temp_r = bc_hist_temp_df_all_r.loc[historical_period].groupby('Station_ID').mean()
    if bc_hist_pr_dfs_r:
        bc_hist_pr_df_all_r = pd.concat(bc_hist_pr_dfs_r).set_index('Date')
        bc_mean_pr_r = bc_hist_pr_df_all_r.loc[historical_period].groupby('Station_ID').mean()
        
    # Merg mean values with station metadata for plotting
    plot_data_temp = station_metadata.merge(obs_mean_temp.rename('Observed'), left_index=True, right_index=True, how ='left')
    plot_data_temp = plot_data_temp.merge(raw_gcm_hist_df.loc[historical_period].groupby('Station_ID').mean().rename('Raw_GCM'), left_index=True, right_index=True, how='left')
    plot_data_temp = plot_data_temp.merge(bc_mean_temp_py.rename('Bias_Corrected_Python'), left_index=True, right_index+True, how=left')
    plot_data_temp = plot_data_temp.merge(bc_mean_temp_r.rename('Bias_Corrected_R_CDFt'), left_index=True, right_index=True, how='left')
    
    plot_data_pr = station_metadata.merge(obs_mean_pr.rename('Observed'), left_index=True, right_index=True, how='left')
    plot_data_pr = plot_data_pr.merge(raw_gcm_hist_df.loc[historical_period].groupby('Station_ID')['Precipitation_mm_day'].mean().rename('Raw_GCM'), left_index=True, right_index=True, how='left')
    plot_data_pr = plot_data_pr.merge(bc_mean_pr_py.rename('Bias_Corrected_Python'), left_index+True, right_index=True, how='left')
    plot_data_pr = plot_data_pr.merge(bc_mean_pr_r.rename('Bias_Corrected_R_CDFt'), left_index=True, right_index+True, how='left')
    
    # Plotting function for spatial maps
    def plot_spatial_map(data_df, var_name, title_suffix, unit, filename_suffix):
        if data_df.empty:
            print(f" No data to plot for spatial map: {title_suffix}. Skipping")
            return
            
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
        ax.set_extent([20.0, 39.5, 8.6, 24.5], crs=ccrs.PlateCarree())    $ Sudan extent
        
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, alpha=0.5)
        ax.add_feature(cfeature.RIVERS)
        
        # Add a light background for land
        ax.add_feature(cfeature.LAND, edgecolors = 'black', facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        
        sc = ax.scatter(data_df['Longitude'], data_df['Latitude'], c=data_df[var_name],
        cmap= 'viridis' if 'Temperature' in var_name else 'Blues',
        s=100, edgecolors='black', transform= ccrs.PlateCarree())
        
        plt.colorbar(sc, label=f'Mean {var_name.replace("_", " ")} {unit}')
        ax.set_title(f'Mean {title_suffix}  ({historical_period})')
        ax.gridlines(draw_labels=True, dms=Tue, x_inline=False, y_inline=False)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'spatial_map_{filename_suffix}.png'))
        plt.close()
        
        print(f" Saved spatial map for {title_suffix}.")
        
    # Plot for Temperature
    plot_spatial_map(plot_data_temp, 'Observed', 'Observed Temperature', '(°C)', 'temp_observed')
    plot_spatial_map(plot_data_remp, 'Raw_GCM', 'Raw GCM Temperature', '(°C)', 'temp_raw_gcm')
    plot_spatial_map(plot_data_temp, 'Bias_Corrected_Python', 'Bias Cprrected (Python) Temperature', '(°C)', 'temp_bc_python')
    plot_spatial_map(plot_data_temp, 'Bias_Corrected_R_CDFt', 'Bias Corrected (R/CDFt) Temperature', '(°C)', 'temp_bc_r_cdft')
    
    
    # Plot for Precipitation
    plot_spatial_map(plot_data_pr, 'Observed', 'Observed Precipitation', '(mm/day)', 'precip_observed')
    plot_spatial_map(plot_data_pr, 'Raw_GCM', 'Raw GCM Precipitation', '(mm/day)', 'precip_raw_gcm')
    plot_spatial_map(plot_data_pr, 'Bias_Corrected_Python', 'Bias Corrected (Python) Precipitation', '(mm/day)', 'precip_bc_python')
    plot_spatial_map(plot_data_pr, 'Bias_Corrected_R_CDFt', 'Bias Corrected (R/CDFt) Precipitation', '(mm/day)', 'precip_bc_r_cdft')
    
    #--- 3. Distribution Plots (Histograms/PDFs for selected stations) ----- #
    print("\nGenerating distribution plots ....")
    
    for stn_id in selected_stations:
        obs_stn_df_hist = [obs_df == stn_id].loc[historical_period]
        
        for var in station_metadata:
            plt.figure(figsize=(10,6))
            
            # Load raw GCM historical data for this station
            raw_gcm_hist_df = pd.read_csv(os.path.join(processed_gcm_dir, f'gcm_extracted_{model_to_visualize}_historical_{historical_period}.csv'), parse_dates=True).set_index('Date')
            raw_gcm_stn_hist_df = [raw_gcm_hist_df == stn_id].loc[historical_period]
            
            # Load Python bias-corrected historical data for this station
            bc_py_filepath = os.path.join(bias_corrected_dir, f'{var.split("_").lower()}_bc_{model_to_visualize}_historical_{stn_id}.csv')
            bc_py_df = pd.read_csv(bc_py_filepath, parse_dates=True).set_index('Date')
            bc_py_stn_hist_df = [bc_py_df == stn_id].loc[historical_period]
            
            # Load R CDFt bias-corrected historical data for this station
            bc_r_filepath = os.path.join(bias_corrected_dir, 'r_cdft', f'{var_split("_").lower()}_bc_cdft_{model_to_visualize}_historical_{stn_id}.csv')
            bc_r_df = pd.read_csv(bc_r_filepath, parse_dates=True).set_index('Date')
            bc_r_stn_hist_df = [bc_r_df == stn_id].loc[historical_period]
            
            # Plot histograms
            bins = 30 if 'Temperature' in var_name else 50        # More bins for precipitation due to  zeros
            
            # Determine common range for consistent plotting
            all_data = []
            if not obs_stn_df_hist[var_name],empty: all_data.extend(obs_stn_df_hist[var_name].tolist())
            if not raw_gcm_stn_hist_df[var_name].empty: all_data.extend(raw_gcm_stn_hist_df[var_name].tolist())
            if not bc_py_stn_hist_df.empty: all_data.extend(bc_py_stn_hist_df.tolist())
            if not bc_r_stn_hist_df.empty: all_data.extend(bc_r_stn_hist_df.tolist())
            
            if not all_data:
                print(f" No data for distirbution plot for {var_name} at {stn_id}. Skipping")
                continue
                
            min_val = np.min(all_data)
            max_val = np.max(all_data)
            range_val = (min_val, max_val)
            
            plt.hist(obs_stn_df_hist[var_name], bins=bins, density=True, alpha=0.6, label='Observed', color+'black', range=range_val)
            plt.hist(raw_gcm_stn_hist_df[var_name], bins=bins, density =True, alpha=0.6, label='Raw GCM', color='red', range=range_val)
            plt.hist(bc_py_stn_hist_df, bins=bins, density =True, alpha=0.6, label = 'Bias-Corrected (Python)', color = 'blue', range=range_val)
            plt.hist(bc_r_stn_hist_df, bins=bins, density= True, alpha =0.6, label= 'Bias-Corrected (R/CDFt)', color = 'darkgreen', range=range_val)
            
            plt.title(f 'Distribution of {var_name} for station {stn_id} ({model_to_visualize})')
            plt.xlabel(f'{var_name} {"(°C)" if "Temperature" in var_name else "(mm/day)"}')
            plt.ylabel('Density')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'distribution_{var_name.split("_").lower()}_{stn_id}.png'))
            plt.close()
            print(f" Saved distribution plot for {var_name} at {stn_id}.")
            
if __name__ == "__main__":
    # Ensure all previous scripts have been run and data is avilable.
    # Run 01_generate_station_data.py, 02_gcm_preprocessing.py, and 03_bias_correction_pythob.py (and 07_cdt_bias_correction_cdft.R) before this script.
    visualize_results()
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
