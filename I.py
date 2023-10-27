# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 21:30:18 2023

@author: lenovo
"""

import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static  # Add this line

# Load the Excel sheets
@st.cache_data
def load_data(sheet1_path, sheet2_path):
    schools = pd.read_excel(sheet1_path)
    coaches = pd.read_excel(sheet2_path)
    return schools, coaches

# Function to find nearest coach for a given school
def find_nearest_coach(school, coaches):
    try:
        school_coords = (float(school['School Latitude']), float(school['School Longitude']))
    except (ValueError, TypeError):
        return None

    same_category_coaches = coaches[coaches['Coach Category'] == school['School Category']]
    if same_category_coaches.empty:
        return None

    try:
        same_category_coaches['Distance'] = same_category_coaches.apply(
            lambda row: geodesic((float(row['Coach Latitude']), float(row['Coach Longitude'])), school_coords).miles,
            axis=1
        )
        nearest_coach = same_category_coaches['Distance'].idxmin()
        return coaches.loc[nearest_coach]
    except (ValueError, TypeError):
        return None

# Main function
def main():
    st.title("Coach Assignment App")

    # Upload files
    sheet1_path = st.file_uploader("Upload first Excel sheet (Schools)", type=["xlsx"])
    sheet2_path = st.file_uploader("Upload second Excel sheet (Coaches)", type=["xlsx"])

    if sheet1_path and sheet2_path:
        schools, coaches = load_data(sheet1_path, sheet2_path)

        # Assign coaches to schools
        assigned_data = []
        for _, school in schools.iterrows():
            nearest_coach = find_nearest_coach(school, coaches)
            if nearest_coach is not None:
                assigned_data.append({
                    'School Name': school['School Name'],
                    'Coach Name': nearest_coach['Coach Name'],
                    'Coach Latitude': nearest_coach['Coach Latitude'],
                    'Coach Longitude': nearest_coach['Coach Longitude'],
                    'School Latitude': school['School Latitude'],  # Add these lines
                    'School Longitude': school['School Longitude']  # Add these lines
                })

        if assigned_data:
            # Display results
            assigned_df = pd.DataFrame(assigned_data)

            # Show map
            st.subheader("Map of Coaches and Schools")
            selected_coach = st.selectbox("Select Coach:", assigned_df['Coach Name'].unique())
            filtered_data = assigned_df[assigned_df['Coach Name'] == selected_coach]

            # Create a map centered around the average of all coordinates
            map_center = [filtered_data['Coach Latitude'].mean(), filtered_data['Coach Longitude'].mean()]
            m = folium.Map(location=map_center, zoom_start=10)

            # Add markers for coaches and schools
            for _, row in filtered_data.iterrows():
                folium.Marker(
                    location=[row['Coach Latitude'], row['Coach Longitude']],
                    popup=row['Coach Name'],
                    icon=folium.Icon(color='blue')
                ).add_to(m)

                folium.Marker(
                    location=[row['School Latitude'], row['School Longitude']],
                    popup=row['School Name'],
                    icon=folium.Icon(color='green')
                ).add_to(m)

            # Display the map
            folium_static(m)

            # Display table
            st.subheader("Assigned Coaches to Schools")
            st.write(filtered_data)
        else:
            st.warning("No matches found for the given criteria.")

if __name__ == '__main__':
    main()