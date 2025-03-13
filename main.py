import streamlit as st
from few_shot import FewShotPosts
from post_generator import generate_post
import json
import os

# Constants
length_options = ["Short", "Medium", "Long"]
language_options = ["English", "French", "Spanish", "German", "Hindi"]
tone_options = ["Professional", "Casual", "Inspirational", "Informative", "Human-like", "Conversational", "Storytelling", "Rhetorical-questions"]

# File path for user preferences
USER_PREFERENCES_FILE = "user_preferences.json"

def save_user_preferences(tone, keywords, writing_sample):
    """
    Save user preferences to a JSON file.
    """
    preferences = {
        "tone": tone,
        "keywords": keywords,
        "writing_sample": writing_sample
    }
    with open(USER_PREFERENCES_FILE, "w") as f:
        json.dump(preferences, f)

def load_user_preferences():
    """
    Load user preferences from a JSON file.
    If the file doesn't exist, return default values.
    """
    if os.path.exists(USER_PREFERENCES_FILE):
        with open(USER_PREFERENCES_FILE, "r") as f:
            return json.load(f)
    return {
        "tone": "Professional", #Detault tone
        "keywords": "",
        "writing_sample": ""
    }


def get_tone_index(tone, tone_options):
    """
    Get the index of the tone in the tone_options list.
    If the tone is invalid or None, return 0 (default to "Professional").
    """
    try:
        return tone_options.index(tone)
    except ValueError:
        return 0  # Default to "Professional"


def main():
    st.title("LinkedIn Post Generator")

    # Initialize session state variables
    if "generated_post" not in st.session_state:
        st.session_state.generated_post = None
    if "edited_post" not in st.session_state:
        st.session_state.edited_post = None

    # Load user preferences
    user_preferences = load_user_preferences()

    # User Customization Section
    st.sidebar.header("Customize Your Post")

    # Tone Selection (default to saved preference)
    selected_tone = st.sidebar.selectbox(
        "Select Tone", options=tone_options,
        index=get_tone_index(user_preferences.get("tone"), tone_options)
        )
    
    # Keywords Input "digital marketing," "recipe book," or "how to socialize a German Shepherd"
    user_keywords = st.sidebar.text_input(
        "Enter Keywords (comma-separated)",
        value=user_preferences.get("keywords", "")
    )
    
    # Writing Sample Upload (default to saved preference)
    user_sample = st.sidebar.text_area(
        "Paste a Writing Sample (optional)",
        value=user_preferences.get("writing_sample", ""), 
        height=150
    )

    # Main Post Generation Section
    col1, col2, col3, = st.columns(3)
    fs = FewShotPosts()

    with col1:
        selected_tag = st.selectbox("Title", options=fs.get_tags() )

    with col2:
        selected_length = st.selectbox("Length", options=length_options)

    with col3:
        selected_language = st.selectbox("Language", options=language_options)

    if st.button("Generate"):
        # Save user preferences
        save_user_preferences(selected_tone, user_keywords, user_sample)
        # Generate the post
        post = generate_post(selected_length, selected_language, selected_tag, selected_tone, user_keywords, user_sample)
        # Store the generated post in session state
        st.session_state.generated_post = post
        st.session_state.edited_post = post  # Initialize edited_post with the generated post
        
        
    # Display the generated post if it exists in session state
    if st.session_state.generated_post:
        st.subheader("Generated Post")
        st.write(st.session_state.generated_post)
        
        # Allow editing
        st.session_state.edited_post = st.text_area(
            "Edit Your Post",
            value=st.session_state.edited_post,
            height=300
        )
        
        # Save Edited Post button (always visible if generated_post exists)
        if st.button("Save Edited Post"):
            try:
                with open("generated_post.txt", "w", encoding="utf-8") as f:
                    f.write(st.session_state.edited_post)
                st.success("Post saved successfully!")
            except Exception as e:
                st.error(f"An error occurred while saving the post: {e}")



if __name__ == "__main__":
    main()