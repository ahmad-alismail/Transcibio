import streamlit as st
import os
from dotenv import load_dotenv
import time # To measure execution time
import tempfile # To handle uploaded files

# Import functions from other modules
from processing import (
    load_diarization_pipeline,
    load_transcription_model,
    perform_diarization,
    transcribe_audio,
    align_transcription_with_diarization,
    SUPPORTED_WHISPER_MODELS,
    DEFAULT_WHISPER_MODEL,
    DEFAULT_PYANNOTE_PIPELINE
)
from utils import (
    format_aligned_transcript,
    save_uploaded_file
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Transcibio",
    page_icon="🗣️",
    layout="wide"
)

# --- Load Environment Variables ---
load_dotenv()
# Try getting token from Streamlit secrets first, then .env
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))

# --- App Title ---
st.title("Transcibio")
st.markdown("Upload an audio file, and this app will transcribe it using Whisper "
            "and identify different speakers using Pyannote.")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")

# Whisper Model Selection
selected_whisper_model = st.sidebar.selectbox(
    "Choose Whisper Model Size:",
    options=SUPPORTED_WHISPER_MODELS,
    index=SUPPORTED_WHISPER_MODELS.index(DEFAULT_WHISPER_MODEL), # Default selection
    help="Smaller models are faster but less accurate. Larger models are slower but more accurate."
)

# Hugging Face Token Info
st.sidebar.markdown("---")
if HF_TOKEN:
    st.sidebar.success("✅ Hugging Face Token found.")
    # Optionally display part of the token for confirmation, but be careful
    # st.sidebar.text(f"Token: {HF_TOKEN[:4]}...{HF_TOKEN[-4:]}")
else:
    st.sidebar.error("❌ Hugging Face Token not found.")
    st.sidebar.markdown(
        "Please add your Hugging Face Token (with read access) as `HF_TOKEN` "
        "to your Streamlit Secrets or a local `.env` file."
        "[Get Token Here](https://huggingface.co/settings/tokens)"
    )
    st.sidebar.warning("Diarization will fail without a valid token.")


# Optional: Number of Speakers
st.sidebar.markdown("---")
num_speakers = st.sidebar.number_input(
    "Number of Speakers (Optional)",
    min_value=0,
    value=0, # 0 means 'auto-detect' for our logic
    help="Set to 0 or leave empty to let Pyannote detect the number of speakers automatically. "
         "Specify a number (e.g., 2) if you know it beforehand."
)
num_speakers_param = num_speakers if num_speakers > 0 else None # Convert 0 to None for pyannote

# --- Main Area ---
st.markdown("---")
uploaded_file = st.file_uploader(
    "Upload Audio File",
    type=["wav", "mp3", "m4a", "ogg", "flac"],
    help="Supports WAV, MP3, M4A, OGG, FLAC formats."
)

if uploaded_file is not None:
    st.audio(uploaded_file, format=uploaded_file.type)

    if st.button("✨ Transcribe and Diarize Audio", type="primary", disabled=(not HF_TOKEN)):

        start_time = time.time()
        temp_audio_path = None # Initialize path variable

        try:
            # 1. Save uploaded file temporarily
            with st.spinner("Saving uploaded file..."):
                temp_audio_path = save_uploaded_file(uploaded_file)
                if not temp_audio_path:
                    st.error("Could not save uploaded file for processing.")
                    st.stop() # Stop execution if file saving failed
                st.info(f"Audio saved temporarily to: {os.path.basename(temp_audio_path)}")

            # 2. Load Models (cached)
            # Models are loaded via @st.cache_resource in processing.py
            diarization_pipeline = load_diarization_pipeline(auth_token=HF_TOKEN)
            transcription_model = load_transcription_model(selected_whisper_model)

            if not diarization_pipeline or not transcription_model:
                 st.error("Failed to load necessary models. Check logs and token.")
                 st.stop()

            # 3. Perform Diarization (cached based on path + params)
            speaker_segments = perform_diarization(
                diarization_pipeline,
                temp_audio_path,
                num_speakers=num_speakers_param
            )

            # 4. Perform Transcription (cached based on path + params)
            transcription_result = transcribe_audio(
                transcription_model,
                temp_audio_path
            )

            # 5. Align Results
            with st.spinner("Aligning transcription with speakers..."):
                aligned_data = align_transcription_with_diarization(
                    transcription_result,
                    speaker_segments
                )

            # 6. Format and Display Output
            st.subheader("Speaker-Aligned Transcript:")
            if aligned_data:
                 formatted_lines = format_aligned_transcript(aligned_data)
                 st.markdown("\n\n".join(formatted_lines)) # Display with markdown for potential bolding
                 # Alternative: Text area for easy copying
                 st.text_area("Full Transcript (copy-paste friendly)", "\n".join(formatted_lines).replace("**",""), height=300)
            else:
                 st.warning("No aligned transcript data to display.")


            end_time = time.time()
            processing_time = end_time - start_time
            st.success(f"🎉 Processing complete in {processing_time:.2f} seconds!")

        except Exception as e:
            st.error(f"An unexpected error occurred during processing: {e}")
            # You might want more specific error handling depending on the exception

        finally:
            # 7. Clean up temporary file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                    print(f"Removed temporary file: {temp_audio_path}")
                except Exception as e_clean:
                    st.warning(f"Could not remove temporary file {temp_audio_path}: {e_clean}")

    elif not HF_TOKEN:
         st.warning("Please provide a Hugging Face Token in the sidebar to enable processing.")


# --- Footer Info ---
st.markdown("---")
st.markdown("App built using [Streamlit](https://streamlit.io), [Whisper](https://github.com/openai/whisper), and [Pyannote.audio](https://github.com/pyannote/pyannote-audio).")