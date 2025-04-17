import whisper
import torch
from pyannote.audio import Pipeline
import pandas as pd
import os
from typing import List, Dict, Optional
import streamlit as st # Import Streamlit for caching

# --- Constants ---
SUPPORTED_WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]
DEFAULT_WHISPER_MODEL = "tiny"
DEFAULT_PYANNOTE_PIPELINE = "pyannote/speaker-diarization-3.1"

# --- Device Selection ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Processing device: {DEVICE}") # Log device choice

# --- Model Loading (Cached) ---

@st.cache_resource(show_spinner="Loading Diarization Pipeline...")
def load_diarization_pipeline(pipeline_name: str = DEFAULT_PYANNOTE_PIPELINE, auth_token: Optional[str] = None):
    """Loads the Pyannote diarization pipeline."""
    print(f"Loading Pyannote pipeline: {pipeline_name}")
    try:
        pipeline = Pipeline.from_pretrained(pipeline_name, use_auth_token=auth_token)
        pipeline.to(torch.device(DEVICE))
        print("Pyannote pipeline loaded successfully.")
        return pipeline
    except Exception as e:
        st.error(f"Error loading diarization pipeline '{pipeline_name}': {e}\n"
                 "Please ensure you have accepted user conditions on Hugging Face Hub "
                 "and provided a valid Hugging Face token (HF_TOKEN) in secrets or .env.")
        return None

@st.cache_resource(show_spinner="Loading Transcription Model...")
def load_transcription_model(model_name: str = DEFAULT_WHISPER_MODEL):
    """Loads the Whisper transcription model."""
    print(f"Loading Whisper model: {model_name}")
    try:
        model = whisper.load_model(model_name, device=DEVICE)
        print("Whisper model loaded successfully.")
        return model
    except Exception as e:
        st.error(f"Error loading Whisper model '{model_name}': {e}")
        return None

# --- Core Processing Functions ---

@st.cache_data(show_spinner="Performing Speaker Diarization...")
def perform_diarization(_pipeline: Pipeline, audio_path: str, num_speakers: Optional[int] = None):
    """Performs speaker diarization on the audio file."""
    print(f"Starting diarization for: {audio_path}")
    if not _pipeline:
        st.error("Diarization pipeline not loaded. Cannot perform diarization.")
        return []
    try:
        diarization = _pipeline(audio_path, num_speakers=num_speakers)
        speaker_segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        print(f"Diarization complete. Found {len(speaker_segments)} speaker turns.")
        if not speaker_segments:
             st.warning("No speaker segments found by pyannote. Alignment might be inaccurate.")
        return speaker_segments
    except Exception as e:
        st.error(f"Error during diarization: {e}")
        return []

@st.cache_data(show_spinner="Transcribing Audio...")
def transcribe_audio(_model: whisper.Whisper, audio_path: str):
    """Transcribes the audio file using Whisper with word timestamps."""
    print(f"Starting transcription for: {audio_path}")
    if not _model:
        st.error("Transcription model not loaded. Cannot perform transcription.")
        return None
    try:
        options = whisper.DecodingOptions(fp16 = (DEVICE == "cuda")) # fp16 only works on CUDA
        result = _model.transcribe(audio_path, word_timestamps=True, **vars(options))
        print("Transcription complete.")
        return result
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return None

# --- Alignment Function ---

def get_speaker_for_timestamp(timestamp: float, segments: List[Dict]) -> str:
    """Finds the speaker for a given timestamp based on diarization segments."""
    for segment in segments:
        if segment["start"] <= timestamp < segment["end"]:
            return segment["speaker"]
    # Basic fallback: Assign to nearest segment if no direct overlap?
    # For simplicity now, return UNKNOWN
    return "UNKNOWN_SPEAKER"

def align_transcription_with_diarization(
    transcription_result: Optional[Dict],
    speaker_segments: List[Dict]
) -> List[Dict]:
    """Aligns Whisper word timestamps with Pyannote speaker segments."""
    aligned_transcript = []
    if not transcription_result or 'segments' not in transcription_result:
        st.warning("Transcription result is missing or invalid. Cannot perform alignment.")
        return []
    if not speaker_segments:
        st.warning("No speaker segments available. Assigning all words to UNKNOWN_SPEAKER.")
        # Assign all words to UNKNOWN if no diarization
        for segment in transcription_result.get('segments', []):
            for word_info in segment.get('words', []):
                 aligned_transcript.append({
                        "start": word_info.get('start', 0),
                        "end": word_info.get('end', 0),
                        "word": word_info.get('word', ""),
                        "speaker": "UNKNOWN_SPEAKER"
                    })
        return aligned_transcript


    print("Aligning transcription with speaker segments...")
    for segment in transcription_result.get('segments', []):
        for word_info in segment.get('words', []):
            word_start = word_info.get('start', None)
            word_end = word_info.get('end', None)
            word_text = word_info.get('word', "")

            if word_start is None or word_end is None:
                speaker_label = "UNKNOWN_SPEAKER" # Cannot align without timestamp
            else:
                # Use the middle of the word time to find the speaker
                word_mid_time = word_start + (word_end - word_start) / 2
                speaker_label = get_speaker_for_timestamp(word_mid_time, speaker_segments)
            # Aligned transcript on word level
            aligned_transcript.append({
                "start": word_start,
                "end": word_end,
                "word": word_text,
                "speaker": speaker_label
            })

    print("Alignment complete.")
    return aligned_transcript