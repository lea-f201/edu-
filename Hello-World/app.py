import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Level of Education",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar collapsed on load
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load and clean data
path = "https://linked.aub.edu.lb/pkgcube/data/2593b20dc9336f21b13c2728bc3927db_20240905_183330.csv"
df = pd.read_csv(path)
df.drop(["Observation URI", "references", "publisher", "dataset"], axis=1, inplace=True)

# Convert percentages
for col in df.columns:
    if "Percentage" in col:
        df[col] = df[col] / 100

# Rename columns
df = df.rename(columns={
    "PercentageofEducationlevelofresidents-illeterate": "Illiteracy (%)",
    "PercentageofSchooldropout": "Dropout (%)",
    "PercentageofEducationlevelofresidents-university": "University Education (%)",
    "PercentageofEducationlevelofresidents-secondary": "Secondary Education (%)",
    "PercentageofEducationlevelofresidents-intermediate": "Intermediate Education (%)",
    "PercentageofEducationlevelofresidents-elementary": "Elementary Education (%)",
    "PercentageofEducationlevelofresidents-highereducation": "Higher Education (%)"
})
df.dropna(inplace=True)

# Sidebar content
with st.sidebar:
    st.title("Level of Education")
    edu_list = [col for col in df.columns if col not in ["refArea", "PercentageofEducationlevelofresidents-vocational", "Town", "Illiteracy (%)", "Dropout (%)"]]
    selected_edu = st.selectbox("Select a Level of Education", edu_list, index=len(edu_list)-1)
    st.title("Insights")

    if 'count' not in st.session_state:
        st.session_state.count = 0

    if 'quotes' not in st.session_state:
        st.session_state.quotes = [
            "The Nabatieh governorate has lower education level percentages at all levels compared to the level averages across lebanon. NGOs and politicians could focus their educational efforts in this region.",
            "More than 10 towns have very low population percentage that finished university. These towns include but not limited to: Ebra WChouan, Tallousa and Aaychiyeh.",
            "The highest rates for higher education levels are located on the lebanese west-side",
            "The maximum level of education achieved that has the lowest percentage across all of Lebanon is the higher education level. It appears that most people who reach the higher education level continue their studies at the university level."
        ]

    def display_quote():
        st.write(st.session_state.quotes[st.session_state.count])

    def next_quote():
        st.session_state.count = (st.session_state.count + 1) % len(st.session_state.quotes)

    def previous_quote():
        if st.session_state.count > 0:
            st.session_state.count -= 1

    display_quote()
    col1, col2 = st.columns(2)
    with col1:
        st.button("⏮️ Previous", on_click=previous_quote)
    with col2:
        st.button("Next ⏭️", on_click=next_quote)

# Cumulative education function
def get_cum(x):
    return sum(df[col].mean() for col in [
        "Elementary Education (%)",
        "Intermediate Education (%)",
        "Secondary Education (%)",
        "Higher Education (%)",
        "University Education (%)"
    ] if col in df.columns and edu_list.index(col) >= edu_list.index(x))

# Layout columns
col = st.columns((2, 1, 4, 2.5), gap="medium")

# Column 0 – Text and Pie
with col[0]:
    st.markdown("<h4 style='text-align: left; color: grey;'>Average Across Lebanon of Last Education Level Secured for</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: left;'>{selected_edu}</p>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: left; color: red;'>{round(df[selected_edu].mean()*100, 2)}%</h4>", unsafe_allow_html=True)

    st.markdown("<h4 style='text-align: left; color: grey;'>Proportion Population that Completed</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: left;'>{selected_edu}</p>", unsafe_allow_html=True)
    cum_val = round(get_cum(selected_edu)*100, 2)
    st.markdown(f"<p style='text-align: left;'>{cum_val}</p>", unsafe_allow_html=True)

    values = [get_cum(selected_edu), 1 - get_cum(selected_edu)]
    labels = [selected_edu, "Other"]
    fig = px.pie(values=values, names=None, hole=0.5, color=labels, color_discrete_sequence=["#FF0000", "#D3D3D3"])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), width=800, height=200, autosize=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig)

# Column 3 – Ranking Table
with col[3]:
    st.markdown("Ranking by Town")
    number = st.slider("Number of Towns Displayed", 0, 50, value=10)
    df_selected_town_edu = df[["Town", selected_edu]]
    sorting_order = st.selectbox("Choose Ranking Order", ["Ascending", "Descending"])
    df_sorted = df_selected_town_edu.sort_values(by=selected_edu, ascending=(sorting_order == "Ascending")).head(number)
    st.dataframe(df_sorted, hide_index=True)

    with st.expander("About", expanded=True):
        st.write("""
        - Data from https://linked.aub.edu.lb:8502/
        - Layout and base code from Streamlit blog
        - Gemini and CharlyWargnier helped shape this version
        """)

with col[2]:
    # ✅ Define valid governorates
    valid_governorates = [
        "Beirut_Governorate",
        "Mount_Lebanon_Governorate",
        "North_Governorate",
        "Akkar_Governorate",
        "Bekaa_Governorate",
        "Baalbek_El_Hermel_Governorate",
        "South_Governorate",
        "Nabatieh_Governorate"
    ]

    # ✅ CRITICAL FIX: Initialize a DataFrame filtered for valid governorates from the main 'df'.
    # Using .copy() is good practice to avoid SettingWithCopyWarning if modifications are made.
    gover_df_filtered = df[df["refArea"].isin(valid_governorates)].copy()

    # ✅ Governorate coordinates (ensure keys match 'valid_governorates' and refArea values)
    coords = {
        "Baalbek_El_Hermel_Governorate": (34.545895, 36.16667),
        "Akkar_Governorate": (34.208272, 36.2625889),
        "North_Governorate": (34.4362, 35.8497),
        "Mount_Lebanon_Governorate": (33.8333, 35.5333),
        "Beirut_Governorate": (33.8886, 35.4955),
        "Bekaa_Governorate": (33.8463, 35.9020),
        "South_Governorate": (33.2721, 35.2033),
        "Nabatieh_Governorate": (33.3777, 35.4839)
    }

    if gover_df_filtered.empty:
        st.warning("No data found for the specified governorates. Map and charts in this column may be empty or incomplete.")
    else:
        # --- Map Plotting ---
        # ✅ Group by 'refArea' to get average education for the map, ensure 'refArea' becomes a column.
        average_education_map_data = gover_df_filtered.groupby("refArea", as_index=False)[[selected_edu]].mean()
        
        # ✅ Assign Latitude and Longitude using the 'coords' dictionary.
        # Use .get() for safety: if a refArea somehow isn't in coords, it will get NaN.
        average_education_map_data["Latitude"] = average_education_map_data["refArea"].map(lambda x: coords.get(x, (np.nan, np.nan))[0])
        average_education_map_data["Longitude"] = average_education_map_data["refArea"].map(lambda x: coords.get(x, (np.nan, np.nan))[1])

        # ✅ Drop rows where Latitude or Longitude is NaN.
        # This ensures that only points with valid coordinates are passed to Plotly.
        # Plotly Express usually ignores NaN coordinates automatically, but this is an explicit cleanup.
        average_education_map_data.dropna(subset=["Latitude", "Longitude"], inplace=True)

        if not average_education_map_data.empty:
            map_plot = px.scatter_mapbox( # Renamed variable from 'map'
                average_education_map_data,
                lat="Latitude",
                lon="Longitude",
                color=selected_edu,
                zoom=7,
                size=selected_edu,  # Governs marker size based on 'selected_edu' values
                hover_name="refArea",
                color_continuous_scale="reds"
            )
            map_plot.update_layout(
                mapbox_style="open-street-map",
                title="Last Level secured (in % Governorate Population)",
                # Removed fixed width/height to allow use_container_width to manage sizing
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            # The marker size set here (40) will override the data-driven 'size=selected_edu'.
            # If you want data-driven sizes, remove marker.size from update_traces or adjust selected_edu values (e.g. scale them).
            # If a fixed size is desired, remove `size=selected_edu` from px.scatter_mapbox.
            # For now, keeping it as in original to focus on coordinate fix.
            map_plot.update_traces(marker=dict(size=40, opacity=0.7)) 
            st.plotly_chart(map_plot, use_container_width=True)
        else:
            st.warning("No data to display on the map after processing (all governorates might have been filtered out or lack coordinates).")

        # --- Bar Chart ---
        gover_names = sorted(gover_df_filtered["refArea"].unique())

        # Lebanon-wide averages (from original 'df')
        average_university = df["University Education (%)"].mean()
        average_higher = df["Higher Education (%)"].mean()
        average_secondary = df["Secondary Education (%)"].mean()
        average_intermediate = df["Intermediate Education (%)"].mean()
        average_elementary = df["Elementary Education (%)"].mean()

        # Governorate-specific averages (from filtered 'gover_df_filtered')
        average_elementaryedu = gover_df_filtered.groupby("refArea")["Elementary Education (%)"].mean()
        average_intermediateedu = gover_df_filtered.groupby("refArea")["Intermediate Education (%)"].mean()
        average_secondaryedu = gover_df_filtered.groupby("refArea")["Secondary Education (%)"].mean()
        average_higheredu = gover_df_filtered.groupby("refArea")["Higher Education (%)"].mean()
        average_universityedu = gover_df_filtered.groupby("refArea")["University Education (%)"].mean()
        
        if gover_names:
            selected_gov = st.selectbox("Select a Governorate", gover_names, key="governorate_selectbox_col2") # Added a unique key

            # Check if selected governorate exists in all aggregated series' indices before plotting
            if all(selected_gov in series.index for series in [average_elementaryedu, average_intermediateedu, average_secondaryedu, average_higheredu, average_universityedu]):
                histogram = go.Figure(data=[
                    go.Bar(name="Elementary Education (%)", x=[selected_gov, "Lebanon"], y=[average_elementaryedu[selected_gov], average_elementary]),
                    go.Bar(name="Intermediate Education (%)", x=[selected_gov, "Lebanon"], y=[average_intermediateedu[selected_gov], average_intermediate]),
                    go.Bar(name="Secondary Education (%)", x=[selected_gov, "Lebanon"], y=[average_secondaryedu[selected_gov], average_secondary]),
                    go.Bar(name="Higher Education (%)", x=[selected_gov, "Lebanon"], y=[average_higheredu[selected_gov], average_higher]),
                    go.Bar(name="University Education (%)", x=[selected_gov, "Lebanon"], y=[average_universityedu[selected_gov], average_university])
                ])
                histogram.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    barmode='group',
                    title="Average Level of Maximum Education for each Governorate (in %)"
                )
                st.plotly_chart(histogram, use_container_width=True)
            else:
                st.warning(f"Complete education data is not available for the selected governorate: {selected_gov}. Some levels might be missing.")
        else:
            st.warning("No governorate data available for the bar chart selection.")
