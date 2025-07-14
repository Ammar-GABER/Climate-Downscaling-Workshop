# R Script: Statistical Downscaling and Bias Correction using CDFt (Quantile Mapping)

#1. Install and Load necessary packages

# install.packages("CDFt")
# install.packages("dplyr")
# install.packages("tidyr")
# install.packages("ncdf4") # For reading NetCDF files

# Load the libraries
library(CDFt)
library(dplyr)
library(tidyr)
library(ncdf4)

# Set working directory to the root of your workshop_downscaling folder
#setwd("/path/to/your/training_materials")

# Define paths (relative to the script's location: training_materials/day2_downscaling_bc/scripts/r/)
station_data_path <- "../../data/staton_data/generated_station_data.csv"
processed_gcm_dir <- "../../data/processed_gcm"
output_dir_bc_r <- "../../output/bias_corrected/r_cdft"
dir.create(output_dir_bc_r, recursive = TRUE, showWarnings = FALSE)

# Define historical and future periods
historical_period_start <- "1991-01-01"
historical_period_end <- "2020-12-31"

future_period_start <- "2041-01-01"
future_period_end <- "2070-12-31"

# Define GCM model and scenarios (must match perprocessed files from Python)
model_name <- "ACCESS-CM2"      # Example model
scenario<- c("historical","ssps245","ssp585")

message(paste("Starting bias correction using CDFt for model: ", model_name))

# Load observed station data
obs_df <- read.csv(station_data_path, stringAsFactors=FALSE)
obs_df$Date <- as.Date(obs_df$Date)
obs_df_hist <- obs_df %>% filter(Date >= as.Date(historical_period_start) & Date <= as.Date(historical_period_end))

station_ids <- unique(obs_df$Station_ID)

for (stn_id in station_ids){
    message(paste("Processing station:", stn_id))
    
    obs_stn_hist <- obs_df_hist %>% filter(Station_ID ==stn_id)
    
    # Load GCM historical data for training (DataGp)
    # Adjust filename if your Python script saves with different time period format
    gcm_hist_filepath <- file.path(processed_gcm_dir, paste0("gcm_extracted_", model_name, "_historical_", historical_period_start, "-", historical_period_end, ".csv"))
    if (!file.exists(gcm_hist_filepath)){
        message(paste("GCM historical data not found for", model_name,"Skipping station."))
        next
    }
    gcm_hist_df <- read.csv(gcm_hist_filepath, stringAsFactors=FALSE)
    gcm_hist_df$Date <- as.Date(gcm_hist_df$Date)
    gcm_hist_stn <- gcm_hist_df %>% filter(Station_ID == stn_id) %>%
    		    filter(Date >= as.Date(historical_period_start) & Date <= as.Date(historical_period_end)) 
    if (nrow(obs_stn_hist) == 0 | nrow(gcm_hist_stn) == 0) {
        message(paste("Insufficient historical data for station", stn_id, ". Skipping."))
        next
    }
    # Align dates for historical period
    common_dates_hist <- intersect(obs_stn_hist$Date, gcm_hist_stn$Date)
    obs_stn_hist_aligned <- obs_stn_hist %>% filter(Date %in% common_dates_hist) %>% arrange(Date)
    gcm_hist_stn_aligned <- gcm_hist_stn %>% filter(Date %in% common_dates_hist) %>% arrange(Date)
    
    # Perform bias correction for each scenario (including historical for evaluation)
    for (scenario in scenarios){
        message(paste("Applying BC for scenario:", scenario))
        current_period_start <- if (scenario == "historical") historical_period_start else future_period_start
        current_period_end <- if (scenario == "historical") historical_period_end else future_period_end
        
        gcm_sim_filepath <- file.path(processed_gcm_dir, paste0("gcm_extracted_", model_name, "_", scenario, "_", current_period_start, "_", current_period_end, ".csv"))
        if (!file.exists(gcm_sim_filepath)){
            message(paste("GCM simulated data not found for", model_name, scenario, ".Skipping scenario."))
            next
        }
        gcm_sim_df <- read.csv(gcm_sim_filepath, stringAsFactors=FALSE)
        gcm_sim_df$Date <- as.Date(gcm_sim_df$Date)
        gcm_sim_stn <- gcm_sim_df %>% filter(Station_ID == stn_id) %>% filter(Date >= as.Date(current_period_start) & Date <= as.Date(current_period_end))
        
        if (nrow(gcm_sim_stn) == 0){
            message(paste("No simulated data for station", stn_id, "in scenario", scenario, ".Skipping."))
            next
        }
        
        # --- Temperature Bias Correction ---#
        ObsRp: Observed historical data
        # DataGp: GCM historical data (for calibration)
        # DataGf: GCM future/simulated data (to be downscaled/corrected)
        
        #CDFt expects numeric vectors
        ObsRp_temp <- obs_stn_hist_aligned$Temperature_C
        DataGp_temp <- gcm_hist_stn_aligned$Temperature_C
        DataGf_temp <- gcm_sim_stn$Temperature_C
        
        # Ensure data is numeric and handle potential NA/Inf
        ObsRp_temp <- as.numeric(ObsRp_temp)
        DataGp_temp <- as.numeric(DataGp_temp)
        DtaGf_temp <- as.numeric(DataGf_temp)
        
        # Remove NA  values for CDFt, it's sensetive to them
        valid_indices_hist_temp <- !is.na(ObsRp_temp) & !is.na(Data_Gp_temp)
        ObsRp_temp_clean <- ObsRp_temp[valid_indices_hist_temp]
        DataGp_tem_clean <- DataGp_temp[valid_indices_hist_temp]
        
        if (length(ObsRp_temp_clean) < 100 | length(DataGp_temp_clean) < 100) {# CDFt needs sufficient data
            message(paste("Not enough valid historical temperature data for  CDFt for station", stn_id, ".Skipping temperature BC."))
        } else {
            tryCatch({
                bc_temp_result <- CDFt(ObsRp = ObsRp_temp_clean, DataGp = DataGp_temp_clean, DataGf = DataGf_temp)
                bc_temp_values <- bc_temp_results$DS
                
                # Create a dataframe for bias-corrected temperature
                bc_temp_df <- data,frame(
                    Date = gcm_sim_stn$Date,
                    Station_ID = stn_id,
                    Temperature_C_BC = bc_temp_values
                )
                write.csv(bc_temp_df, file,path(output_dir_bc_r, paste0("temp_bc_cdft_", model_name, "_", scenario, "_", stn_id, ".csv")), row,names = FALSE)
                message(paste("Temperature BC (CDFt) saved for", stn_id, scenario))
                }, error = function(e){
                message(paste("Error in Temperature BC (CDFt) for", stn_id, scenario, ":", e$message))
                }
            })
        }
        #--- Precipitation Bias Correction ---#
        ObsRp_pr <- obs_stn_hist_aligned$Precipitation_mm_day
        Data_Gp_pr <- gcm_hist_stn_aligned$Precipitation_mm_day
        Data_Gf_pr <- gcm_sim_stn$Precipitation_mm_day
        
        Obs_Rp_pr <- as.numeric(ObsRp_pr)
        DataGp_pr <- as.numeric(DataGp_pr)
        DataGf_pr <- as.numeric(DataGf_pr)
        
        # Handle Zeros for precipitation (CDFt handles this internally for non-negative data)
        # Ensure no negative values
        ObsRp_pr <- 0
        DataGp_pr <- 0
        DataGf_pr <- 0
        
        valid_indices_hist_pr <- !is.na(ObsRp_pr) & !is.na(DataGp_pr)
        ObsRp_pr_clean <- ObsRp_pr[valid_indices_hist_pr]
        DataGp_pr_clean <- DataGp_pr[valid_indices_hist_pr]
        
        if (length(ObsRp_pr_clean) < 100| length(DataGp_pr_clean) < 100) {
            messsage(paste(" No enough valid historical precipitation data found for CDFt for station", stn_id, ".Skipping precipitation BC."))
        } else{
            tryCatch({
                bc_pr_result <- CDFt(ObsRp = ObsRp_pr_clean, DataGp = DataGp_pr_clean, DataGf = DataGf_pr)
                bc_pr_values <- bc_pr_result$DS
                
                # Create a dataframe for bias-corrected precipitation
                bc_pr_df <- data,frame(
                    Date = gcm_sim_stn$Date,
                    Station_ID = stn_id,
                    Precipitation_mm_day_BC = bc_pr_values
                )
                write.csv(bc_pr_df, file.path(output_dir_bc_r, paste0("precip_bc_cdft_", model_name, "_", scenario, "_", stn_id, ".csv")), row.names = FALSE)
                message(paste(" Precipitation BC (CDFt) saved for", stn_id, scenario,))
            }, error = function(e){
                message(paste("Error in Precipitation BC (CDFt) for", stn_id, scenario, ":", e$message))
            })
        }
    }

}
message("\nCDFt bias correction process completed.")
message("Bias-corrected data saved in 'output/bias_corrected/r_cdft' folder.")
