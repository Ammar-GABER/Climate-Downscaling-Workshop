# Climate Change Downscaling and Bias-Correction Training Workshop

This repository contains all the materials for GCF NAP-Readiness Project implemented by FAOSD, a 3-day training workshop designed for SMA meteorologist experts to upgrade their skills in statistical climate change projections downscaling and bias correction.

## Workshop Overview
The workshop focuses on using ground station data for surface temperature and precipitation over the period 1991-2020. It covers:

### Accessing GCM data (CMIP6)

1. Data management using Climate Data Tools (CDT) in R

2. Performing statistical downscaling

3. Performing bias corrections (using Python and R)

4. Evaluating performance

5. Visualizing results spatially and graphically

## Repository Structure

training_materials
	*- day1_foundations/    # Day 1: Foundations of CLimate Change Projections Downscaling and Bias-Correction
	**- slides/ #Markdown slides for Day 1
	**- scripts/ 
	***- shell/ # Shell script for GCM data download
	***- python/ # Python scripts for data generation and GCM preprocessing
	
	*- day2_downscaling_bc/ # Day 2: Statistical Downscaling and Bias-Correction
	**- slides/ # Markdown slides for Day 2
	**- scripts/
	***- python/ # Python scripts for bias correction
	***- r/ # R scripts for CDT data handling and R-based bias correction
	
	*- day3_evaluation-visualization/ #Day 3: Evaluation and Visualization
	**- slides/ # Markdown slides for Day 3
	**- scripts/
	***- python/ # Python scripts for evaluation and visualization
	***- r/ # R scripts for evaluation and visualization
	
	*- data/ # Stores raw and processed data
	**- raw_gcm/ # Downloaded CMIP6 NetCDF files
	**- station_data/ # Generated synthetic station data
	***- processed_gcm/ # Extracted GCM data for station locations
	
	*- output/ # Stores generated results and plots
	**- bias_corrected/ # Bias-Corrected data (Python and R outputs)
	**- evaluation_results/ # Evaluation metrics results
	***- plots/ # Generated plots (Python and R outputs)
