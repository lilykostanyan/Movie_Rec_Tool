import re
import json
import pandas as pd
import shutil
from sentence_transformers import SentenceTransformer
from typing import List, Union
from config import MOVIE_SYNOPSIS_FILE, JSONS_FOLDER
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

def run_chunk_and_embed_pipeline(
    input_excel: str = None,
    output_dir: str = None
) -> None:
    """
    Processes an Excel file containing movie data, chunks text fields, embeds the chunks using a
    SentenceTransformer model, and saves the results as JSON files.

    Args:
        input_excel (str): Path to the input Excel file containing movie data.
                           Default is "imdb_data/romance_synopsis_cleaned.xlsx".
        output_dir (str): Directory where the chunked JSON files will be saved.
                          Default is "chunked_jsons/romance_chunks_json".

    Returns:
        None
    """
    if input_excel is None:
        input_excel = f"imdb_data/{MOVIE_SYNOPSIS_FILE}"
    if output_dir is None:
        output_dir = JSONS_FOLDER

    # Load the SentenceTransformer model for embedding text.
    model: SentenceTransformer = SentenceTransformer('bert-base-nli-mean-tokens')
    os.makedirs(output_dir, exist_ok=True)

    # Read the input Excel file into a pandas DataFrame.
    df: pd.DataFrame = pd.read_excel(input_excel, engine='openpyxl')

    def smart_split_sentences(text: str) -> List[str]:
        """
        Splits a text into sentences while preserving abbreviations.

        Args:
            text (str): The input text to split.

        Returns:
            list: A list of sentences.
        """
        abbreviations = {
            "Dr.": "DR_ABBR", "Mr.": "MR_ABBR", "Mrs.": "MRS_ABBR", "Ms.": "MS_ABBR",
            "Jr.": "JR_ABBR", "Sr.": "SR_ABBR", "St.": "ST_ABBR", "Prof.": "PROF_ABBR",
            "Inc.": "INC_ABBR", "Ltd.": "LTD_ABBR", "vs.": "VS_ABBR",
            "e.g.": "EG_ABBR", "i.e.": "IE_ABBR"
        }
        for abbr, token in abbreviations.items():
            text = text.replace(abbr, token)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        restored = []
        for sentence in sentences:
            for abbr, token in abbreviations.items():
                sentence = sentence.replace(token, abbr)
            restored.append(sentence.strip())
        return restored

    def chunk_text(text: str, min_chunk_size: int = 100, max_chunk_size: int = 275, target_chunk_size: int = 240) -> List[str]:
        """
        Splits a text into chunks of specified sizes.

        Args:
            text (str): The input text to chunk.
            min_chunk_size (int): Minimum size of a chunk in words. Default is 100.
            max_chunk_size (int): Maximum size of a chunk in words. Default is 275.
            target_chunk_size (int): Target size of a chunk in words. Default is 240.

        Returns:
            list: A list of text chunks.
        """
        words = text.split()
        if len(words) <= target_chunk_size:
            return [text.strip()]
        sentences = smart_split_sentences(text)
        chunks = []
        current_chunk = []
        current_length = 0
        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length > max_chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk).strip())
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        if current_chunk:
            if chunks and len(" ".join(current_chunk).split()) < min_chunk_size:
                chunks[-1] += " " + " ".join(current_chunk)
            else:
                chunks.append(" ".join(current_chunk).strip())
        return chunks

    def smart_split_summaries(text: str) -> List[str]:
        """
        Splits a summary text into individual summaries.

        Args:
            text (str): The input summary text.

        Returns:
            list: A list of cleaned summary strings.
        """
        text = text.strip()
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        split_candidates = re.split(r"""(?<!\\)['"]\s*,\s*['"]""", text)
        cleaned = []
        for chunk in split_candidates:
            chunk = chunk.strip().strip('"').strip("'").strip()
            if chunk and chunk.lower() != "no summaries found":
                cleaned.append(chunk)
        return cleaned

    # Initialize lists to store documents and text for embedding.
    all_documents: List[dict] = []
    texts_to_embed: List[str] = []

    # Iterate over each row in the DataFrame.
    for index, row in df.iterrows():
        movie_id: str = row["tconst"]
        try:
            genres: List[str] = eval(row["genres"]) if pd.notna(row["genres"]) and isinstance(row["genres"], str) else []
        except:
            genres = []
        short_synopsis: str = row["short_synopsis"] if pd.notna(row["short_synopsis"]) else ""
        long_synopsis: str = row["long_synopsis"] if pd.notna(row["long_synopsis"]) else ""
        summaries: Union[str, List[str]] = row["summaries"]

        # Process short synopsis if available.
        if short_synopsis.strip() and short_synopsis.strip() != "No short sum found":
            doc = {
                "movie_id": movie_id,
                "genres": genres,
                "type": "short",
                "chunk_id": f"{movie_id}-sh-1",
                "text": short_synopsis.strip()
            }
            all_documents.append(doc)
            texts_to_embed.append(doc["text"])

        # Process summaries if available.
        if pd.notna(summaries):
            if isinstance(summaries, str):
                summaries = smart_split_summaries(summaries)
            elif isinstance(summaries, list):
                summaries = [s for s in summaries if isinstance(s, str)]
            else:
                summaries = []
        else:
            summaries = []

        for j, summary in enumerate(summaries):
            if summary.strip():
                chunks = chunk_text(summary)
                for i, chunk in enumerate(chunks):
                    doc = {
                        "movie_id": movie_id,
                        "genres": genres,
                        "type": "summary",
                        "chunk_id": f"{movie_id}-summary-{j + 1}-{i + 1}",
                        "text": chunk
                    }
                    all_documents.append(doc)
                    texts_to_embed.append(chunk)

        # Process long synopsis if available.
        if long_synopsis.strip() and long_synopsis.strip() != "Synopsis not found":
            long_chunks = chunk_text(long_synopsis)
            for i, chunk in enumerate(long_chunks):
                doc = {
                    "movie_id": movie_id,
                    "genres": genres,
                    "type": "long",
                    "chunk_id": f"{movie_id}-lon-{i + 1}",
                    "text": chunk
                }
                all_documents.append(doc)
                texts_to_embed.append(chunk)

        # Embed the text chunks using the SentenceTransformer model.
        logger.info(f"- Embedding {len(texts_to_embed)} chunks on GPU...")
        vectors = model.encode(texts_to_embed, batch_size=32, show_progress_bar=True)

        # Add the embedding vectors to the corresponding documents.
        for i, vector in enumerate(vectors):
            all_documents[i]["vector"] = vector.tolist()

        # Save each document as a JSON file in the output directory.
        for doc in all_documents:
            filename = f"{doc['chunk_id']}.json"
            path = os.path.join(output_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=4)

        logger.info(f"- {len(all_documents)} documents saved to: {output_dir}")

        # Create a ZIP archive of the output directory.
        shutil.make_archive(output_dir, 'zip', output_dir)
        logger.info(f"- Archive created: {output_dir}.zip")