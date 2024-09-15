import random
import nltk
from nltk.corpus import words

# Download the word list if you haven't already
nltk.download('words')

# Fetch the list of words
word_list = words.words()

# Function to generate the unique ID
def generate_unique_id(num_words=4):
    # Randomly select words and join them with dashes
    selected_words = random.sample(word_list, num_words)
    return '-'.join(selected_words)
