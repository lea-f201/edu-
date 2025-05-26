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
    map = px.scatter_mapbox(average_education, lat="Latitude", lon="Longitude", color= selected_edu, zoom=7, color_continuous_scale='reds')
    map.update_layout(mapbox_style='open-street-map', title='Last Level secured (in % Governorate Population)', width=500, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    map.update_traces(marker=dict(size=40, opacity=0.7))
    st.plotly_chart(map, use_container_width=True)
    
    gover_names = sorted(gover_df["refArea"].unique())
    average_university = df["University Education (%)"].mean()
    average_higher = df["Higher Education (%)"].mean() 
    average_secondary = df["Secondary Education (%)"].mean() 
    average_intermediate = df["Intermediate Education (%)"].mean() 
    average_elementary = df["Elementary Education (%)"].mean() 

    leb_data = {"Education" : ["Elementary" , "Intermediate", "Secondary", "Higher", "University"],
                "percentage" : [average_elementary, average_intermediate, average_secondary, average_higher, average_university]}

    average_elementaryedu = gover_df.groupby("refArea")["Elementary Education (%)"].mean()
    average_intermediateedu = gover_df.groupby("refArea")["Intermediate Education (%)"].mean()
    average_secondaryedu = gover_df.groupby("refArea")["Secondary Education (%)"].mean()
    average_higheredu = gover_df.groupby("refArea")["Higher Education (%)"].mean()
    average_universityedu = gover_df.groupby("refArea")["University Education (%)"].mean()
    
    selected_gov = st.selectbox("Select a Governorate", gover_names)

    import plotly.graph_objects as go
    histogram = go.Figure(data=[
        go.Bar(name="Elementary Education (%)", x=(selected_gov,"Lebanon"), y=(average_elementaryedu[selected_gov], average_elementary)),
        go.Bar(name="Intermediate Education (%)", x=(selected_gov,"Lebanon"), y=(average_intermediateedu[selected_gov], average_intermediate)),
        go.Bar(name="Secondary Education (%)", x=(selected_gov,"Lebanon"), y=(average_secondaryedu[selected_gov], average_secondary)),
        go.Bar(name="Higher Education (%)", x=(selected_gov,"Lebanon"), y=(average_higheredu[selected_gov], average_higher)),
        go.Bar(name="University Education (%)", x=(selected_gov,"Lebanon"), y=(average_universityedu[selected_gov], average_university))
    ])
    histogram.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', barmode='group', title="Average Level of Maximum Education for each Governorate (in %)")
    st.plotly_chart(histogram, use_container_width=True)

