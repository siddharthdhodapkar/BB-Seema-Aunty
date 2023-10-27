import streamlit as st
import pandas as pd
from geopy.distance import geodesic

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
                    'Coach Name': nearest_coach['Coach Name']
                })

        if assigned_data:
            # Display results
            assigned_df = pd.DataFrame(assigned_data)
            st.subheader("Assigned Coaches to Schools")
            st.write(assigned_df)
        else:
            st.warning("No matches found for the given criteria.")

if __name__ == '__main__':
    main()
