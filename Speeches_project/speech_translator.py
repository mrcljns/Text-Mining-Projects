import numpy as np
import pandas as pd
from tqdm import tqdm
# To see the progress
tqdm.pandas()
# Library for obtaining translation
import translators as ts

# Function for translating the text
def get_translation(text):
    # In case of error, return nan
    try:
        # Translate by paragraph
        pars = text.split("\n")
        translated_text = [ts.translate_text(query_text=par, from_language="tr", to_language="en", translator="google") for par in pars]
        return "\n".join(translated_text)
    except:
        return np.nan

# Load speeches
speeches_df = pd.read_csv("Erdogan_speeches.csv")

# Translate title
speeches_df["Translated_title"] = speeches_df["Title"].progress_map(lambda x: get_translation(x))

# Translate transcript of speech
speeches_df["Translated_text"] = speeches_df["Text"].progress_map(lambda x: get_translation(x))

speeches_df = speeches_df.drop(["Title", "Text"], axis=1)

# Reorder the columns
speeches_df = speeches_df[["Translated_title", "Date", "Translated_text"]]

# Write results to file
speeches_df.to_csv("Erdogan_translated_speeches.csv", index=False)