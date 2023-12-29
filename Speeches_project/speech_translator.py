import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
# Libraries for obtaining translation
import translators as ts
from deep_translator import GoogleTranslator
import time

translator = GoogleTranslator(source='tr', target='en')

# Function for translating the text
def get_translation(text):
    try:
        # Translate by paragraph
        pars = text.split("\n")
        # translated_text = [ts.translate_text(query_text=par, from_language="tr", to_language="en", translator="bing") for par in pars]
        translated_text = translator.translate_batch(pars)
        translated_text = [x for x in translated_text if x is not None]
        return "\n".join(translated_text)
    except:
        return np.nan
    
parser = argparse.ArgumentParser()
parser.add_argument("year", help="translate only speeches from the given year", type=int, nargs="?")
parser.add_argument("limit", help="translate only n-number of speeches until the limit", type=int, nargs="?")
args = parser.parse_args()

# See the progress bar
tqdm.pandas()

# Load speeches
speech_df = pd.read_csv("Erdogan_selected_speeches.csv")

if args.year:
    speech_df.Date = pd.to_datetime(speech_df.Date, format="%Y-%m-%d")
    speech_df = speech_df.loc[speech_df.Date.dt.year == args.year].reset_index(drop=True)

if args.limit:
    speech_df = speech_df.iloc[:args.limit].reset_index(drop=True)

# Translate title
speech_df["Translated_title"] = speech_df["Title"].progress_map(lambda x: get_translation(x))

# Translate transcript of speech
speech_df["Translated_text"] = speech_df["Text"].progress_map(lambda x: get_translation(x))

speech_df = speech_df.drop(["Title", "Text"], axis=1)

# Reorder the columns
speech_df = speech_df[["Translated_title", "Date", "Translated_text"]]

# Write results to file
speech_df.to_csv("Erdogan_translated_speeches.csv", index=False)