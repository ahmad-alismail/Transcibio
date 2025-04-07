import streamlit as st
import tempfile
import os
from typing import List, Dict, IO

def format_aligned_transcript(aligned_data: List[Dict]) -> List[str]:
    """Formats the aligned transcript data into readable strings."""
    if not aligned_data:
        return ["No transcription data found or alignment failed."]

    output_lines = []
    current_speaker = None
    current_segment_start = None
    current_text = ""
    last_end_time = 0.0

    for i, word_data in enumerate(aligned_data):
        speaker = word_data.get('speaker', "UNKNOWN")
        word = word_data.get('word', "")
        start_time = word_data.get('start', None)
        end_time = word_data.get('end', None)

        # Initialize on first word or if start_time is None
        if current_speaker is None or start_time is None:
            current_speaker = speaker
            current_segment_start = start_time if start_time is not None else last_end_time
            current_text = "" # Reset text

        # If speaker changes, or if start_time is missing (treat as new segment)
        if speaker != current_speaker or start_time is None:
            if current_text.strip(): # Print previous segment if it had text
                 segment_start_str = f"{current_segment_start:.2f}s" if current_segment_start is not None else "??"
                 segment_end_str = f"{last_end_time:.2f}s" if last_end_time is not None else "??"
                 output_lines.append(f"[{segment_start_str} - {segment_end_str}] **{current_speaker}:** {current_text.strip()}")

            # Start new segment
            current_speaker = speaker
            current_segment_start = start_time if start_time is not None else last_end_time
            current_text = word
        else:
            # Append word to current segment's text
            current_text += word

        # Update last known end time
        if end_time is not None:
            last_end_time = end_time

        # Print the very last segment after the loop finishes
        if i == len(aligned_data) - 1 and current_text.strip():
            segment_start_str = f"{current_segment_start:.2f}s" if current_segment_start is not None else "??"
            segment_end_str = f"{last_end_time:.2f}s" if last_end_time is not None else "??"
            output_lines.append(f"[{segment_start_str} - {segment_end_str}] **{current_speaker}:** {current_text.strip()}")

    return output_lines


def save_uploaded_file(uploaded_file: IO[bytes]) -> str:
    """Saves uploaded file to a temporary path and returns the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return None