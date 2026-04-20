# DATA_ENG 300 - Homework 1: Aircraft Inventory Data Engineering
Maya Westra 

## How to Run
- Ensure the dataset file T_F41SCHEDULE_B43_with_missing.zip is in the same directory as the notebook.
- Open DATA_ENG_300_HW1_Westra_Maya.ipynb in Jupyter Notebook or JupyterLab.
- Run all cells in order from top to bottom (Kernel → Restart & Run All).

## Required Packages 
pandas
numpy
matplotlib
seaborn
scipy
scikit-learn

**Install With** 
pip install pandas numpy matplotlib seaborn scipy scikit-learn

## Expected Outputs 
- Question 1: Missing value investigation and imputation for 6 columns (CARRIER, CARRIER_NAME, MANUFACTURE_YEAR, NUMBER_OF_SEATS, CAPACITY_IN_POUNDS, and AIRLINE_ID)
- Question 2: Standardized MANUFACTURER, MODEL, AIRCRAFT_STATUS, and OPERATING_STATUS columns.
- Question 3: Missing rows dropped, 98,220 rows retained.
- Question 4: Histograms and skewness values before/after Box-Cox transformation for NUMBER_OF_SEATS and CAPACITY_IN_POUNDS.
- Question 5: SIZE column created from quartiles of NUMBER_OF_SEATS. Proportion plots by size group.
- Question 6: RMSE results for linear regression and random forest models predicting NUMBER_OF_SEATS and CAPACITY_IN_POUNDS.

## Files

DATA_ENG_300_HW1_Westra_Maya.ipynb — source code
DATA_ENG_300_HW1_Westra_Maya.html — written analysis report (code hidden)
