import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
import openai

# Function for translating the text with Chat GPT
def openai_translation(text, target_language):
        response = openai.Completion.create(
            engine="text-davinci-002", 
            prompt=f"Translate the following text into {target_language}: {text}\n", 
            max_tokens=60, 
            n=1, 
            stop=None, 
            temperature=0.7, )
        return response.choices[0].text.strip()

# Function for applying the translator to the text by paragraph
def get_translation(text):
    # In case of error, return nan
    try:
        # Translate by paragraph
        pars = text.split("\n")
        translated_text = [openai_translation(par, "turkish") for par in pars]
        return "\n".join(translated_text)
    except:
        return np.nan
    
parser = argparse.ArgumentParser()
parser.add_argument("api_key", help="connect to openai api with this key", type=int)
parser.add_argument("year", help="translate only speeches from the given year", type=int)
parser.add_argument("limit", help="translate only n-number of speeches until the limit", type=int)
args = parser.parse_args()

if args.api_key:
    # Use provided API key
    openai.api_key = args.api_key

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

else:
    print("Cannot translate without providing an OpenAI API key.")