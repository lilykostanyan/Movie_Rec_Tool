import pandas as pd
import ast
from typing import List, Any, Union
from config import OUTPUT_FILE, CLEANED_OUTPUT_FILE
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.logger import logger

def clean_romance_synopsis(input_csv: str = None, output_csv: str = None) -> None:
    """
    Cleans a CSV file containing romance movie synopses by removing rows with missing data
    and processing the summaries column. The cleaned data is saved to an Excel file.

    Args:
        input_csv (str): Path to the input CSV file containing the full movie data.
                         Default is "imdb_data/romance_newbatch.csv".
        output_csv (str): Path to the output CSV file where the cleaned data will be saved.
                            Default is "imdb_data/romance_full_cleaned.csv".

    Returns:
        None
    """

    if input_csv is None:
        input_csv = f"imdb_data/{OUTPUT_FILE}"
    if output_csv is None:
        output_csv = f"imdb_data/{CLEANED_OUTPUT_FILE}"

    # Load the input CSV file into a pandas DataFrame.
    df: pd.DataFrame = pd.read_csv(input_csv)

    # Filter out rows where all synopsis fields are missing or invalid.
    original_len: int = len(df)
    condition = (
        (df['short_synopsis'] == 'No short sum found') &
        (df['long_synopsis'] == 'Synopsis not found') &
        (df['summaries'].astype(str) == "['No summaries found']")
    )
    df_cleaned: pd.DataFrame = df[~condition].copy()
    removed_count: int = original_len - len(df_cleaned)

    def clean_summary_list(summary_list: Union[List[str], Any]) -> Union[List[str], Any]:
        """
        Cleans a list of summary strings by removing unwanted characters and truncating text.

        Args:
            summary_list (list or any): A list of summary strings to clean. If not a list, it is returned as-is.

        Returns:
            list or any: The cleaned list of summaries, or the original input if not a list.
        """
        if isinstance(summary_list, list):
            cleaned: List[str] = []
            for s in summary_list:
                if isinstance(s, str):
                    # Remove unwanted characters or truncate text based on specific patterns.
                    if '_x0014_' in s:
                        s = s.split('_x0014_')[0].strip()
                    if '—' in s:
                        s = s.rsplit('—', 1)[0].strip()
                cleaned.append(s)
            return cleaned
        return summary_list

    # Parse string representations of lists into actual Python lists and clean them.
    df_cleaned['summaries'] = df_cleaned['summaries'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df_cleaned['summaries'] = df_cleaned['summaries'].apply(clean_summary_list)

    def remove_backslashes(text: Any) -> Any:
        """
        Removes backslashes from a string.

        Args:
            text (str or any): The input text to process. If not a string, it is returned as-is.

        Returns:
            str or any: The processed string with backslashes removed, or the original input if not a string.
        """
        if isinstance(text, str):
            return text.replace("\\", "")
        return text

    # Remove backslashes from the summaries column.
    df_cleaned['summaries'] = df_cleaned['summaries'].apply(remove_backslashes)

    # Save the cleaned DataFrame to an CSV file.
    df_cleaned.to_csv(output_csv, index=False)
    logger.info(f"- Cleaned synopsis saved to: {output_csv}")
    logger.info(f"- Rows removed: {removed_count}")