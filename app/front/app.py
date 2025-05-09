import streamlit as st
from recommend import gemini_recommendation, custom_model_recommendation, display_movie
from config import GENRE_OPTIONS
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

logger.info("- Front Launching...")

# Set wide layout for the Streamlit app
st.set_page_config(layout="wide")

# Set the title of the Streamlit app
st.title("🎬 Movie Recommendation System")

# Allow the user to choose the recommendation mode
mode = st.radio("Choose recommendation mode:", ["Our Model", "Gemini AI"])

# === GEMINI MODE ===
if mode == "Gemini AI":
    # Input field for the user to describe the type of movie they are looking for
    query = st.text_area("Describe the kind of movie you're looking for:")

    # Dropdown to select the number of recommendations
    num_recs = st.selectbox("How many recommendations do you want?", [1, 2, 3, 4, 5], index=2)

    # Button to trigger the Gemini recommendation process
    if st.button("Ask Gemini"):
        if not query.strip():
            # Show a warning if the input query is empty
            st.warning("Prompt is empty.")
        else:
            try:
                # Fetch movie suggestions using the Gemini AI model
                suggestions = gemini_recommendation(query, num_recs)
                st.markdown("### Gemini Suggestions:")
                st.markdown(suggestions)
            except Exception as e:
                # Display an error message if the Gemini API call fails
                st.error(f"Gemini API Error: {e}")

# === CUSTOM MODEL MODE
elif mode == "Our Model":
    # Option to filter recommendations by genre
    use_filter = st.radio("Do you want to filter by genre?", ["No", "Yes"]) == "Yes"
    selected_genres = []
    if use_filter:
        # Allow the user to select genres for filtering
        selected_genres = st.multiselect("Select genres:", GENRE_OPTIONS)
        # Allow the user to choose the filtering mode (strict or relaxed)
        filtering_mode = st.radio("Choose filtering mode:", ["Strict", "Relaxed"]).lower()
    else:
        # Default filtering mode when no genre filter is applied
        filtering_mode = "strict"
        st.markdown("Search across all genres for your movie preferences.")

    # Dropdown to select the number of recommendations
    num_recs = st.selectbox("How many recommendations do you want?", [1, 2, 3, 4, 5], index=2)

    # Input field for the user to describe the type of movie they are looking for
    query = st.text_input("Describe the kind of movie you're looking for:")

    # Button to trigger the custom model recommendation process
    if st.button("Get Recommendations"):
        if not query.strip():
            # Show a warning if the input query is empty
            st.warning("Please enter a movie description.")
        else:
            try:
                # Fetch movie recommendations using the custom backend model
                data = custom_model_recommendation(query, num_recs, use_filter, selected_genres, filtering_mode)
                if not data["results"]:
                    # Display an error message if no matching movies are found
                    st.error("😔 No matching movies found.")
                else:
                    # Display each recommended movie using the display_movie function
                    for movie in data["results"]:
                        display_movie(movie)
            except Exception as e:
                # Display an error message if the API call fails
                st.error(f"Error calling API: {e}")