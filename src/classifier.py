import pickle
import string
from functools import lru_cache

# Text preprocessing function
# convert to lower case
# remove stop words
# remove uneeded white space
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = " ".join(text.split())  # Remove extra whitespace
    return text

# Load the model via a function and cache it
@lru_cache(maxsize=1)  # Cache the loaded model in memory (maxsize=1 ensures only 1 cached item)
def load_model(model_path="text_classifier_pipeline.pkl"):
    # Load the pickled pipeline only once
    with open(model_path, "rb") as file:
        loaded_model = pickle.load(file)
    return loaded_model

def classify_file_ml(text):
    # Load the cached model
    loaded_model = load_model()
    
    # Preprocess the input text
    preprocessed_text = clean_text(text)
    
    # Predict the file type using the model
    return loaded_model.predict([preprocessed_text])[0]
