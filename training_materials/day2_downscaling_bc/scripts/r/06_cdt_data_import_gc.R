# R script : Data Import and Quality COntrol using CDT functionalities

#1. Install and Load CDT (if not already installed)
# install.packages("devtools)
#devtools::install_github("rijaf-iri/CDT")
library(CDT)
# To start the CDT GUI:
#CDT()


# Set working directory to the root of your workshop_downscaling folder
# setwd("/path/to/your/training_materials")

# Define paths (relevant to the script's location: training_materials/day2_downscaling_bc/scripts/r/)

station_data_path <- "../../data/station_data/generated_station_data.csv"
output_dir_cdt_processed <- "../../data/station_data/cdt_processed"
dir.create(output_dir_cdt_processed, recursive = TRUE, showWarnings = FALSE)

#2. Import Station Data into CDT format
#CDT prefers a speific station data format.
# We'll read the CSV and convert it into a format CDT can easly use or simulate its import.
# For direct use with CDT functions, it' often easier to prepare the CSV in a specific way or use the GUI's import function.

# Example of reading a CSV and preparing for CDT (conceptual, as CDT GUI handle this interactively)
# This part deminstrates how you  might prepare your data if you were to use CDT's command-line functions that exepect a CDT-formatted station data object.
# In the GUI, you would go to 'Data'-> 'Import Data' -> 'From CSV/TXT' and follow the prompts.

# Read the generated CSV
station_df <- read.csv(station_data_path)
station_df$Date <- as.Date(station_df$Date)

# For CDT, you would typically save this into a specific structure or use the GUI.
# Let's simulate saving it in a simple text format that CDT might read, or just acknowledge that the GUI is the primary way for this step.

# Example of a simple text format for CDT (Station_ID, Latitude, Longitude, Date, Varibale_Value)
# This is a simplified representation; CDT's internal format is more complex.
# For actual CDT command-line functions, you'd typically use 'readCDTStationData' which expects a specific file structure.

#cdt_station_data_obj <- readCDTStationData("path/to/your/cdt_station_file.csv")
# print(cdt_station_data_obj)

message("--- Data Import (Concetual with CDT GUI) ----")
message(" In CDT GUI: Go to 'Data' -> 'Import Data' -> 'From CSV/TXT'.")
message("Select 'generated_station_data.csv'. Map 'Date', 'Station_ID', 'Latitude', 'Longitude','Temperature_C', 'Precipitation_mm_day' columns.")
message("This will create an internal CDT station data object.")


#3. Basic QUality Control (Conceptual with CDT GUI)

message("\n---- Basic Quality Control (Cpnceptual with CDT GUI) ---")
message("CDT offers robust QC functionalities, primarily through its GUI:")
messages("-- 'QC' -> 'Data Availability': To check for missing values and gaps.")
messages("-- 'QC' -> 'False-Zeros Check for daily rainfall': To identify and correct erroneous zero precipitation values. ")
messages("-- 'QC' -> 'Outliers Check for rainfall data'/ 'Outliers Check for temperature data': To detect and flag outliers. ")
message("-- 'QC' -> 'Homogeneity Test': To check for inhomogeneities in time series.")
message("These steps are typically perfromed interactivelly in the GUI to visualize and apply corrections.")

#4. Merging for Gap Filling (Conceptual with CDT GUI)

message("\n--- Merging fro Gap Filling (Conceptual with CDT GUI) ---")
message("CDT can merge station observations with gridded proxies (e.g., reanalysis, satellite data) to fill gaps.")
message("-- In CDT GUI: Go to 'Gridding' -> 'Merging Climate Data' -> 'Temperature' or 'Rainfall'. ")
message("Select your sation data and specify proxy gridded prodycts.")
message("-- This creates a more complete and spatially cohernt dataset for downscaling.")
message("-- Example function (command line, but typically used via GUI): cdtMegingClimDataCMD ")

# Example of how cdtMergingClimDataCMD might be called (requires specific CDT data objects and Netcdf paths)
# This is illustrative and won't run without prper CDT data objects and NetCDF files.

# cdtMergingClimDataCMD(
	variable = "temp",
	time.step = "daily",
	dates = list(from = "range", pars = list(start="19910101", end = "20201231")),
	station.data = list(file = "path/to/your/cdt_station_file.csv", sep = ",", na.strings = "-99"),
	netcdf.data = list(file = "path/to/your/reanalysis_temp_netcdf_dir", fromat = "reanalysis_temp_%s%s%s.nc", varid = "temp", ilon = 1, ilat = 2),
	merge.method = list(method = "SBA"),     # Simple Bias Adjustment for merging
	output = list(dir = output_dir_cdt_processed, format = ""merged_temp_%s%s%s.nc)
)

message("\nData import and QC in CDT are primarly interactive via the GUI for ease of use.")
message("The next script will demonstrate bias correction using the CDFt R package, which is related to CDT's QM functionality.")


























