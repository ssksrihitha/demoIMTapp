import streamlit as st
import pandas as pd
import numpy as np
import io

# Streamlit UI setup
st.title("GTL Deep locations suggestion app")

# File upload section
fwd_file = st.file_uploader("Upload FWD Locations CSV", type="csv")
deep_file = st.file_uploader("Upload Deep Locations CSV", type="csv")

if fwd_file and deep_file:
    # Read the uploaded CSV files
    fwd_locations = pd.read_csv(fwd_file)
    deep_locations = pd.read_csv(deep_file)
    st.write("Columns in FWD Locations:")
    st.dataframe(fwd_locations)
    # Add a column to store the Location ID in "FWD Locations"
    fwd_locations['LocDeep'] = np.nan

    # Apply flexible date parsing to the 'mfd' column
    deep_locations['mfd'] = pd.to_datetime(deep_locations['mfd'], errors='coerce', dayfirst=True)


    # # Iterate over each FSN in the "FWD Locations" DataFrame
    # for index, row in fwd_locations.iterrows():
    #     fsn = row['FSN']
    #     wid_fwd = row['WID']
    #     sort = row['Sort']  # Assuming f_sort is in the "FWD Locations" file
        
    #     # Check 1: Search for FSN in "Deep Locations"
    #     deep_fsn_rows = deep_locations[deep_locations['fsn'] == fsn]
        
    #     if deep_fsn_rows.empty:
    #         # FSN not found in "Deep Locations"
    #         fwd_locations.at[index, 'LocDeep'] = "Not actionable"
    #         continue  # Move to the next FSN
        
    #     # Check 2: Search for WID in "Deep Locations" with the same FSN
    #     deep_wid_rows = deep_fsn_rows[deep_fsn_rows['wid'] == wid_fwd]
        
    #     if not deep_wid_rows.empty:
    #         # Check 3: Select the minimum quantity for the found WID
    #         min_qty_row = deep_wid_rows.loc[deep_wid_rows['qty'].idxmin()]
    #         fwd_locations.at[index, 'LocDeep'] = min_qty_row['Loc']
    #     else:
    #         # Check 4: WID not found, select earliest date from remaining WIDs
    #         # Filter rows with non-empty 'mfd'
    #         valid_deep_fsn_rows = deep_fsn_rows[deep_fsn_rows['mfd'].notna()]
            
    #         if not valid_deep_fsn_rows.empty:
    #             # # Convert 'mfd' to datetime for comparison
    #             # deep_fsn_rows['mfd'] = pd.to_datetime(deep_fsn_rows['mfd'], format='%d/%m/%y')
                
    #             # Find the row with the earliest 'mfd' date
    #             earliest_date_row = deep_fsn_rows.loc[deep_fsn_rows['mfd'].idxmin()]
                
    #             # Handle case if 'mfd' is the same for multiple rows
    #             earliest_mfd_date = earliest_date_row['mfd']
    #             earliest_date_rows = deep_fsn_rows[deep_fsn_rows['mfd'] == earliest_mfd_date]
                
    #             if len(earliest_date_rows) > 1:
    #                 # Check 5: Handle tie by finding the least abs(d_sort - f_sort)
    #                 earliest_date_rows['sort_diff'] = abs(earliest_date_rows['d_sort'] - sort)
    #                 min_sort_diff_row = earliest_date_rows.loc[earliest_date_rows['sort_diff'].idxmin()]
    #                 fwd_locations.at[index, 'LocDeep'] = min_sort_diff_row['Loc']
    #             else:
    #                 # Use the earliest 'mfd' date's Location ID
    #                 fwd_locations.at[index, 'LocDeep'] = earliest_date_row['Loc']
    #         else:
    #             # No valid 'mfd' found, go to Check 3
    #             min_qty_row = deep_fsn_rows.loc[deep_fsn_rows['qty'].idxmin()]
    #             fwd_locations.at[index, 'LocDeep'] = min_qty_row['Loc']
# Iterate over each FSN in the "FWD Locations" DataFrame
for index, row in fwd_locations.iterrows():
    fsn = row['FSN']
    wid_fwd = row['WID']
    f_sort = row['Sort']  # Assuming f_sort is in the "FWD Locations" file
    
    # Check 1: Search for FSN in "Deep Locations"
    deep_fsn_rows = deep_locations[deep_locations['fsn'] == fsn]
    
    if deep_fsn_rows.empty:
        # FSN not found in "Deep Locations"
        fwd_locations.at[index, 'LocDeep'] = "Not actionable"
        continue  # Move to the next FSN
    
    # Check 2: Search for WID in "Deep Locations" with the same FSN
    deep_wid_rows = deep_fsn_rows[deep_fsn_rows['wid'] == wid_fwd]
    
    if not deep_wid_rows.empty:
        # Check 3: Select the minimum quantity for the found WID
        min_qty_row = deep_wid_rows.loc[deep_wid_rows['qty'].idxmin()]
        
        # Check if multiple rows have the minimum quantity
        min_qty = min_qty_row['qty']
        min_qty_rows = deep_wid_rows[deep_wid_rows['qty'] == min_qty]
        
        if len(min_qty_rows) == 1:
            # Only one row with minimum quantity
            fwd_locations.at[index, 'LocDeep'] = min_qty_row['Loc']
        else:
            # Multiple rows with the same minimum quantity
            # Check 5: Handle tie by finding the least abs(d_sort - f_sort)
            min_qty_rows['sort_diff'] = abs(min_qty_rows['d_sort'] - f_sort)
            min_sort_diff_row = min_qty_rows.loc[min_qty_rows['sort_diff'].idxmin()]
            fwd_locations.at[index, 'LocDeep'] = min_sort_diff_row['Loc']
    
    else:
        # Check 4: WID not found, select earliest date from remaining WIDs
        # Filter rows with non-empty 'mfd'
        valid_deep_fsn_rows = deep_fsn_rows[deep_fsn_rows['mfd'].notna()]
        
        if not valid_deep_fsn_rows.empty:
            # Convert 'mfd' to datetime for comparison
            valid_deep_fsn_rows['mfd'] = pd.to_datetime(valid_deep_fsn_rows['mfd'], format='%d/%m/%y', errors='coerce')
            
            # Find the row with the earliest 'mfd' date
            earliest_date_row = valid_deep_fsn_rows.loc[valid_deep_fsn_rows['mfd'].idxmin()]
            
            # Handle case if 'mfd' is the same for multiple rows
            earliest_mfd_date = earliest_date_row['mfd']
            earliest_date_rows = valid_deep_fsn_rows[valid_deep_fsn_rows['mfd'] == earliest_mfd_date]
            
            if len(earliest_date_rows) > 1:
                # Check 5: Handle tie by finding the least abs(d_sort - f_sort)
                earliest_date_rows['sort_diff'] = abs(earliest_date_rows['d_sort'] - f_sort)
                min_sort_diff_row = earliest_date_rows.loc[earliest_date_rows['sort_diff'].idxmin()]
                fwd_locations.at[index, 'LocDeep'] = min_sort_diff_row['Loc']
            else:
                # Use the earliest 'mfd' date's Location ID
                fwd_locations.at[index, 'LocDeep'] = earliest_date_row['Loc']
        else:
            # No valid 'mfd' found, go to Check 3 and Check 5 again if necessary
            # Check 3: Select the minimum quantity for the found FSN
            min_qty_row = deep_fsn_rows.loc[deep_fsn_rows['qty'].idxmin()]
            
            # Check if multiple rows have the minimum quantity
            min_qty = min_qty_row['qty']
            min_qty_rows = deep_fsn_rows[deep_fsn_rows['qty'] == min_qty]
            
            if len(min_qty_rows) == 1:
                # Only one row with minimum quantity
                fwd_locations.at[index, 'LocDeep'] = min_qty_row['Loc']
            else:
                # Multiple rows with the same minimum quantity
                # Check 5: Handle tie by finding the least abs(d_sort - f_sort)
                min_qty_rows['sort_diff'] = abs(min_qty_rows['d_sort'] - f_sort)
                min_sort_diff_row = min_qty_rows.loc[min_qty_rows['sort_diff'].idxmin()]
                fwd_locations.at[index, 'LocDeep'] = min_sort_diff_row['Loc']

# Display the updated "FWD Locations" DataFrame
st.write("FWD Locations after processing:")
st.dataframe(fwd_locations)

# Show the updated DataFrame in the Streamlit app
st.write("meh")
st.dataframe(fwd_locations)
st.write("deep meh")
st.dataframe(deep_locations)

# Function to convert DataFrame to CSV for download
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')
    
# Convert the updated DataFrame to CSV
csv_data = convert_df_to_csv(fwd_locations)
    
# Download button for the updated "FWD Locations" file
st.download_button(
    label="Download Updated FWD Locations",
    data=csv_data,
    file_name='FWD_Locations_Updated.csv',
    mime='text/csv'
    )
  