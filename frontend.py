import streamlit as st
import requests
import pandas as pd
import altair as alt

# Set the page configuration for a wider layout and a custom title
st.set_page_config(page_title="News Sentiment Dashboard", layout="wide")

# Sidebar for user inputs
st.sidebar.title("News Sentiment Dashboard")
company = st.sidebar.text_input("Enter Company Name", "X")

if st.sidebar.button("Generate Report"):
    with st.spinner("Fetching and processing news..."):
        payload = {"company_name": company}
        try:
            # Make sure to update the URL if your API endpoint changes
            response = requests.post("http://localhost:8000/api/process-news", json=payload)
            if response.status_code == 200:
                data = response.json()
                st.success("Report generated successfully!")
                
                # Create three tabs: Comparative Report, Articles, and Audio Report
                tab1, tab2, tab3 = st.tabs(["Comparative Report", "Articles", "Audio Report"])
                
                with tab1:
                    st.header("Comparative Sentiment Report")
                    st.text(data["comparative_report"])
                    
                    st.header("Sentiment Distribution")
                    sentiment_counts = data["sentiment_counts"]
                    # Create a DataFrame for the sentiment counts
                    df = pd.DataFrame({
                        "Sentiment": list(sentiment_counts.keys()),
                        "Count": list(sentiment_counts.values())
                    })
                    # Create an interactive Altair bar chart
                    chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X("Sentiment", sort=None),
                        y="Count",
                        color="Sentiment"
                    ).properties(width=600)
                    st.altair_chart(chart, use_container_width=True)
                
                with tab2:
                    st.header("News Articles")
                    # Display each article within an expander for a cleaner view
                    for article in data["articles"]:
                        with st.expander(article["title"]):
                            st.markdown(f"**Summary:** {article['summary']}")
                            st.markdown(f"**Publication Date:** {article['publication_date']}")
                            st.markdown(f"**Sentiment:** {article['sentiment']}")
                            st.markdown(f"[Read full article]({article['url']})")
                
                with tab3:
                    st.header("Hindi Audio Report")
                    try:
                        with open(data["tts_file"], 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format='audio/mp3')
                    except Exception as e:
                        st.error(f"Error loading audio: {e}")
            else:
                st.error("Error fetching data from the API.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
