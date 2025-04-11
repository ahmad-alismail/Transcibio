import streamlit as st
# Use the OpenAI library pointed at the local server
from openai import OpenAI, APIConnectionError, RateLimitError # Import specific errors
from typing import List, Dict, Optional
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter


# --- Constants ---
LMSTUDIO_DEFAULT_URL = "http://localhost:1234/v1"
# Model name might be ignored by LM Studio if only one model loaded, use a placeholder
# Or allow user to specify which loaded model to use via app UI later if needed
DEFAULT_LOCAL_MODEL = "gemma-3-4b-it"#"deepseek-r1-distill-qwen-7b"
DEFAULT_SUMMARY_PROMPT_TEMPLATE = "Fasse den folgenden Text zusammen. Gib ausschließlich die Zusammenfassung zurück, \
                                    ohne einleitenden oder abschließenden Kommentar:\n\n{input_text}"
DEFAULT_COMBINE_PROMPT_TEMPLATE = "Fasse die folgenden Zusammenfassungen zu einer abschließenden, \
                                    kohärenten Zusammenfassung des Originaltexts zusammen. Achte darauf, dass die endgültige Zusammenfassung \
                                    gut lesbar ist und die wichtigsten Informationen korrekt wiedergibt. \
                                    Gib ausschließlich die Zusammenfassung zurück, ohne einleitenden oder abschließenden Kommentar:\n\n{input_text}"



# --- API Call Function for Local LLM (using OpenAI library) ---

def call_local_llm_summarize(
    base_url: str,
    text_to_summarize: str,
    prompt_template: str,
    model_name: str = DEFAULT_LOCAL_MODEL
) -> Optional[str]:
    """Calls the local LLM server (like LM Studio) for summarization using the OpenAI library."""
    if not base_url:
        st.error("LM Studio API URL is missing.")
        return None

    try:
        # Point OpenAI client to the local server
        # Use a dummy API key as required by the library, LM Studio ignores it
        client = OpenAI(base_url=base_url.rstrip('/'), api_key="lm-studio")

        prompt = prompt_template.format(input_text=text_to_summarize)

        completion = client.chat.completions.create(
            model=model_name, # Model served by LM Studio
            messages=[
                
                {"role": "system", "content": "Du bist ein hilfreicher Assistent, der auf das Zusammenfassen von Inhalten spezialisiert ist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0, # Lower temperature for factual summary
            
        )
        summary = completion.choices[0].message.content.strip()
        return summary

    except APIConnectionError as e:
        st.error(f"LM Studio Connection Error: {e}. Is LM Studio running and the server started at {base_url}?")
        return None
    except RateLimitError as e:
         st.error(f"LM Studio Rate Limit Error: {e}") # Unlikely for local, but possible
         return None
    except Exception as e:
        # Catch other potential errors from the OpenAI client or LM Studio response
        st.error(f"Error during local LLM call: {e}")
        return None


# --- Main Map-Reduce Summarization Logic ---

@st.cache_data(show_spinner="Generating summary with local LLM...")
def summarize_text_map_reduce(
    full_text: str,
    chunk_size: int,
    chunk_overlap: int,
    base_url: Optional[str] = None,
    model_name: Optional[str] = None,
    combine_summaries: bool = True  # Add this parameter
) -> Optional[str]:
    """Summarizes text using Map-Reduce strategy with the configured local LLM."""

    if not base_url:
         st.error("Cannot summarize: LM Studio API URL is not configured.")
         return None

    model_to_use = model_name or DEFAULT_LOCAL_MODEL

    # 1. Split the text into chunks
    # (Keep Langchain splitting logic as before)
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
    chunks = text_splitter.split_text(full_text)


    if not chunks:
        st.warning("Text could not be split into chunks.")
        return None

    st.info(f"Text split into {len(chunks)} chunks for summarization.")

    # 2. Map: Summarize each chunk individually
    chunk_summaries = []
    progress_bar = st.progress(0, text="Summarizing chunks via local LLM...")
    for i, chunk in enumerate(chunks):
        summary = call_local_llm_summarize(
            base_url, chunk, DEFAULT_SUMMARY_PROMPT_TEMPLATE, model_to_use
        )

        if summary:
            chunk_summaries.append(summary)
        else:
            st.warning(f"Could not summarize chunk {i+1}/{len(chunks)}.")
            # Option: stop? For now, we continue and try to summarize the rest.

        # Update progress bar
        progress = (i + 1) / len(chunks)
        progress_bar.progress(progress, text=f"Summarizing chunk {i+1}/{len(chunks)}...")

    progress_bar.empty() # Remove progress bar after loop

    if not chunk_summaries:
        st.error("Failed to generate summaries for any chunk.")
        return None

    st.info(f"Generated {len(chunk_summaries)} chunk summaries.")

    # 3. Reduce: Combine chunk summaries and summarize again if needed
    combined_summaries = "\n\n".join(chunk_summaries)

    if len(chunk_summaries) == 1 or not combine_summaries:  # Check if user wants to skip combining
        if len(chunk_summaries) == 1:
            st.success("Generated final summary from single chunk.")
        else:
            st.success("Returning individual chunk summaries as requested.")
        return combined_summaries
    else:
        st.info("Combining chunk summaries into a final summary...")
        final_summary = call_local_llm_summarize(
            base_url, combined_summaries, DEFAULT_COMBINE_PROMPT_TEMPLATE, model_to_use
        )

        if final_summary:
             st.success("Generated final combined summary.")
             return final_summary
        else:
             st.error("Failed to generate the final combined summary. Returning combined chunk summaries instead.")
             return combined_summaries  # Fallback