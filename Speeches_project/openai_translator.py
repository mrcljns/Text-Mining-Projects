import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
from openai import OpenAI

def openai_translation(text):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a skilled and experienced translator, specializing in translating texts from turkish to english without losing the meaning of the original language."},
            {"role": "user", "content": f"Translate the following text from turkish to english: {text}"}
            ]
            )
    return completion.choices[0].message.content

# Function for translating the text
def get_translation(text):
    # In case of error, return nan
    try:
        # Translate by paragraph
        pars = text.split("\n")
        translated_text = [openai_translation(par) for par in pars]
        return "\n".join(translated_text)
    except:
        return np.nan
    
parser = argparse.ArgumentParser()
parser.add_argument("year", help="translate only speeches from the given year", type=int)
parser.add_argument("limit", help="translate only n-number of speeches until the limit", type=int)
args = parser.parse_args()

client = OpenAI()

# See the progress bar
tqdm.pandas()

# Load speeches
speech_df = pd.read_csv("Erdogan_speeches.csv")

if args.year:
    speech_df.Date = pd.to_datetime(speech_df.Date, format="%d.%m.%Y")
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