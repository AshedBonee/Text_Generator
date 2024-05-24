from flask import Flask, request, jsonify
import numpy as np
import pickle
from keras.utils import pad_sequences
from keras.models import load_model
import language_tool_python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

model = load_model('model.h5')

# Load fitted Tokenizer
with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

# Define the maximum sequence length used during training
max_sequence_len = 20  # This should be set to the max sequence length used during training

tool = language_tool_python.LanguageTool('en-US')  # Language tool for grammar correction

# Generate text function
def generate_text(seed_text, next_words, model, max_sequence_len):
    for _ in range(next_words):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len, padding='pre')
        predicted_probs = model.predict(token_list, verbose=0)[0]
        predicted_index = np.argmax(predicted_probs)
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted_index:
                output_word = word
                break
        seed_text += " " + output_word
        if output_word in ['.', '!', '?']:  # Check for end punctuation
            break
    return seed_text

def correct_grammar(text):
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text

def paraphrase_paragraph(paragraph):
    sentences = paragraph.split('. ')
    paraphrased_sentences = []
    for sentence in sentences:
        paraphrased_sentence = generate_text(sentence.strip(), 10, model, max_sequence_len)  # Reduce the word count for coherence
        paraphrased_sentences.append(paraphrased_sentence)
    paraphrased_paragraph = '. '.join(paraphrased_sentences)
    if not paraphrased_paragraph.endswith('.'):
        paraphrased_paragraph += '.'
    return paraphrased_paragraph

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    seed_text = data.get('seed_text', '')
    next_words = data.get('next_words', 50)
    preresult = generate_text(seed_text, next_words, model, max_sequence_len)
    corrected_text = correct_grammar(preresult)
    paraphrased_text = paraphrase_paragraph(corrected_text)
    return jsonify({'generated_text': paraphrased_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
