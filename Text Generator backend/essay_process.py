import os
import numpy as np
import pickle
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense
from keras.callbacks import ModelCheckpoint, EarlyStopping

# Load essays
def load_essays(directory):
    essays = []
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r') as file:
            essays.append(file.read())
    return essays

# Preprocess essays
def preprocess_texts(texts):
    texts = [text.lower() for text in texts]
    texts = [''.join(char for char in text if char.isalnum() or char.isspace()) for text in texts]  # Remove non-alphanumeric characters
    texts = [text.replace('\n', ' ') for text in texts]  # Replace new lines with spaces
    return texts

# Load and preprocess essays
essays = load_essays('essays')
processed_essays = preprocess_texts(essays)

# Tokenize essays
tokenizer = Tokenizer()
tokenizer.fit_on_texts(processed_essays)
sequences = tokenizer.texts_to_sequences(processed_essays)
vocab_size = len(tokenizer.word_index) + 1

# Save tokenizer
with open('tokenizer.pkl', 'wb') as tokenizer_file:
    pickle.dump(tokenizer, tokenizer_file)

# Create input-output pairs
def create_sequences(sequences, step=20):
    input_sequences = []
    target_sequences = []
    for seq in sequences:
        for i in range(0, len(seq) - step):
            input_sequences.append(seq[i:i + step])
            target_sequences.append(seq[i + step])
    return input_sequences, target_sequences

# Set step size and create sequences
step = 20
input_sequences, target_sequences = create_sequences(sequences, step)

# Convert to numpy arrays and pad sequences
input_sequences = pad_sequences(input_sequences)
target_sequences = np.array(target_sequences)

# Define the model
model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=50, input_length=input_sequences.shape[1]))
model.add(LSTM(100, return_sequences=False))
model.add(Dense(vocab_size, activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Model checkpoint and early stopping
checkpoint = ModelCheckpoint('model.h5', monitor='loss', verbose=1, save_best_only=True, mode='min')
early_stopping = EarlyStopping(monitor='loss', patience=5, verbose=1, mode='min')

# Train the model
model.fit(input_sequences, target_sequences, epochs=300, batch_size=64, callbacks=[checkpoint, early_stopping])