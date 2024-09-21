import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Level of Education",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")
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

path = "https://linked.aub.edu.lb/pkgcube/data/2593b20dc9336f21b13c2728bc3927db_20240905_183330.csv"
df = pd.read_csv(path)
# delete reference columns
df.drop(["Observation URI","references","publisher","dataset"], axis = 1, inplace = True)
df["PercentageofEducationlevelofresidents-illeterate"]= df["PercentageofEducationlevelofresidents-illeterate"]/100
df["PercentageofSchooldropout"]= df["PercentageofSchooldropout"]/100
df["PercentageofEducationlevelofresidents-university"]= df["PercentageofEducationlevelofresidents-university"]/100
df["PercentageofEducationlevelofresidents-secondary"]= df["PercentageofEducationlevelofresidents-secondary"]/100
df["PercentageofEducationlevelofresidents-intermediate"]= df["PercentageofEducationlevelofresidents-intermediate"]/100
df["PercentageofEducationlevelofresidents-vocational"]= df["PercentageofEducationlevelofresidents-vocational"]/100
df["PercentageofEducationlevelofresidents-elementary"]= df["PercentageofEducationlevelofresidents-elementary"]/100
df["PercentageofEducationlevelofresidents-highereducation"]= df["PercentageofEducationlevelofresidents-highereducation"]/100
# rename columns
df = df.rename(columns = {"PercentageofEducationlevelofresidents-illeterate":"Illiteracy (%)","PercentageofSchooldropout":"Dropout (%)","PercentageofEducationlevelofresidents-university":"University Education (%)", "PercentageofEducationlevelofresidents-secondary":"Secondary Education (%)","PercentageofEducationlevelofresidents-intermediate":"Intermediate Education (%)","PercentageofEducationlevelofresidents-elementary":"Elementary Education (%)","PercentageofEducationlevelofresidents-highereducation":"Higher Education (%)"})
df.dropna(inplace = True)

# add side bar
with st.sidebar:
    st.title("Level of Education")
    edu_list = list(df.columns)
    excluded_columns = ["refArea", "PercentageofEducationlevelofresidents-vocational", "Town", "Illiteracy (%)", "Dropout (%)"]  
    edu_list = [col for col in edu_list if col not in excluded_columns]
    selected_edu = st.selectbox("Select a Level of Education", edu_list, index=len(edu_list)-1)
    df_selected_edu = df[selected_edu]
    st.title("Insights")

    if 'count' not in st.session_state:
        st.session_state.count = 0

    if 'quotes' not in st.session_state:
        st.session_state.quotes = [
        "The Nabatieh governorate has lower education level percentages at all levels compared to the level averages across lebanon. NGOs and politicians could focus their educational efforts in this region. ",
        "More than 10 towns have very low population percentage that finished university. These towns include but not limited to: Ebra WChouan, Tallousa and Aaychiyeh. ",
        "The highest rates for higher education levels are located on the lebanese west-side",
        "The maximum level of education achieved that has the lowest percentage across all of Lebanon is the higher education level. It appears that most people who reach the higher education level continue their studies at the university level. ",
    ]

    def display_quote():
       quote = st.session_state.quotes[st.session_state.count]
       st.write(quote)

    def next_quote():
        if st.session_state.count + 1 >= len(st.session_state.quotes):
            st.session_state.count = 0
        else:
            st.session_state.count += 1

    def previous_quote():
       if st.session_state.count > 0:
           st.session_state.count -= 1

    display_quote()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏮️ Previous", on_click=previous_quote):
            pass
    with col2:
        if st.button("Next ⏭️", on_click=next_quote):
            pass
    
# function to get cumulative education
def get_cum(x):
    if x == "Higher Education (%)":
        return(df["Higher Education (%)"].mean()+ df["University Education (%)"].mean())
    elif x == "Secondary Education (%)":
        return(df["University Education (%)"].mean() + df["Secondary Education (%)"].mean() + df["Higher Education (%)"].mean())
    elif x == "Intermediate Education (%)":
        return(df["Intermediate Education (%)"].mean()+ df["University Education (%)"].mean() + df["Secondary Education (%)"].mean() + df["Higher Education (%)"].mean())
    elif x == "Elementary Education (%)":
        return(df["Intermediate Education (%)"].mean()+ df["Elementary Education (%)"].mean() + df["Secondary Education (%)"].mean() + df["Higher Education (%)"].mean() + df["University Education (%)"].mean())
    else:
        return df[x].mean()


col = st.columns((2, 1, 4, 2.5), gap="medium")
with col[0]:
    st.markdown("<h4 style='text-align: center; color: grey;'>Average Across Lebanon of Last Education Level  Secured for", unsafe_allow_html=True)
    average_edu = str(round(df[selected_edu].mean()*100,2)) + "%"
    text = selected_edu
    st.markdown(f"<p style='text-align: center;'>{text}</p>", unsafe_allow_html=True)
    Text = average_edu
    st.markdown(f"<h4 style='text-align: center; color: red;'>{Text}</p>", unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
    st.markdown("<h4 style='text-align: center; color: grey;'>Proportion Population that   Completed", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{text}</p>", unsafe_allow_html=True)
    text1 = round(get_cum(selected_edu)*100,2)
    st.markdown(f"<p style='text-align: center;'>{text1}</p>", unsafe_allow_html=True)
    values = [get_cum(selected_edu), 1 - get_cum(selected_edu)]
    labels = [selected_edu, "Other"]
    fig = px.pie(values=values, names=None, hole=0.5,
            title=None, color = labels, color_discrete_sequence=["#FF0000", "#D3D3D3"])
    fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    width=800,
    height=200,
    autosize=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
    st.plotly_chart(fig)

with col[3]:
    st.markdown("Ranking by Town")
    number = st.slider("Number of Towns Displayed",0,50)
    df_selected_town_edu = df[["Town", selected_edu]]
    sorting_order = st.selectbox("Choose Ranking Order", ["Ascending", "Descending"])
    if sorting_order == "Ascending":
        df_selected_town_edu= df_selected_town_edu.sort_values(by=selected_edu, ascending=True).head(number)
    elif sorting_order == "Descending":
        df_selected_town_edu = df_selected_town_edu.sort_values(by=selected_edu, ascending=False).head(number)
    st.dataframe(df_selected_town_edu,
                 column_order=("Town", selected_edu),
                 hide_index=True,
                 width=None,
                 column_config={
                    "Town": st.column_config.TextColumn(
                        "Town",
                    ),
                    selected_edu: st.column_config.ProgressColumn(
                        "Highest Level Achieved",
                        format="%f",
                        min_value=0,
                        max_value=1,
                     )}
                 )
    with st.expander('About', expanded=True):
        st.write('''
            - Data from https://linked.aub.edu.lb:8502/
            - Layout and base code from https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/
            - Gemini helped in understanding some code as well as finding alternative coding options 
            - Code for buttons from https://gist.github.com
                 CharlyWargnier
            ''')

df["refArea"] = df["refArea"].str.split("/", n = 4).str[4] 
df["governorate"] =  df["refArea"].str[-1] == "e"
governorate = df["governorate"] ==True
gover_df = df[governorate]

average_education = pd.DataFrame({
    "Latitude":[34.545895, 34.208272, 33.8333, 33.8333, 33.3667, 34.4639449, 33.2721],
    "Longitude":[36.16667, 36.2625889, 35.9000, 35.5333, 35.4667, 35.9466045, 35.2033],
    "Elementary Education (%)": gover_df.groupby("refArea")["Elementary Education (%)"].mean(),
    "Intermediate Education (%)": gover_df.groupby("refArea")["Intermediate Education (%)"].mean(),
    "Secondary Education (%)": gover_df.groupby("refArea")["Secondary Education (%)"].mean(),
    "Higher Education (%)": gover_df.groupby("refArea")["Higher Education (%)"].mean(),
    "University Education (%)": gover_df.groupby("refArea")["University Education (%)"].mean()
})

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
    
    histogram =go.Figure(data=[
    go.Bar(name="Elementary Education (%)", x=(selected_gov,"Lebanon"), y= (average_elementaryedu[selected_gov],average_elementary) ),
    go.Bar(name="Intermediate Education (%)", x=(selected_gov,"Lebanon"), y= (average_intermediateedu[selected_gov],average_intermediate) ),
    go.Bar(name="Secondary Education (%)", x=(selected_gov,"Lebanon"), y= (average_secondaryedu[selected_gov],average_secondary)  ),
    go.Bar(name="Higher Education (%)", x=(selected_gov,"Lebanon"), y= (average_higheredu[selected_gov],average_higher) ),
    go.Bar(name="University Education (%)", x=(selected_gov,"Lebanon"), y= (average_universityedu[selected_gov],average_university) )
    ])
    histogram.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', barmode='group', title="Average Level of Maximum Education for each Governorate (in %)")
    st.plotly_chart(histogram, use_container_width=True)
    
