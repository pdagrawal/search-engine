import os
import time
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt

# This method is responsible to call all the methods in the required sequence
def main(input_dir, output_dir):
    file_count = 0
    words_in_files = {}
    file_values = []
    time_values = []
    start = time.process_time_ns()
    stopwords = load_stop_words()
    inverted_index = {}
    # number of words present in a document after preprocessing
    words_count_in_docs = {}
    for filename in sorted(os.listdir(input_dir)):
        file_count += 1
        tokens = extract_tokens(input_dir + '/' + filename, stopwords)
        words_count_in_docs[filename] = len(tokens)
        words_in_files[filename] = tokens
        update_inverted_index(inverted_index, filename, tokens)
        if file_count%50 == 0:
            file_values.append(file_count)
            time_values.append(time.process_time_ns()/1000000)
            end = time.process_time_ns()
            print(f'Parsed Files {file_count} and Time taken {(end - start)/1000000}')
            start = time.process_time_ns()
    inverted_index = remove_rare_words(inverted_index)
    postings_list = create_postings_list(inverted_index, words_count_in_docs)
    print(len(postings_list))
    create_wts_files(words_in_files, postings_list, output_dir)
    # plot_graph(file_values, time_values)


def load_stop_words():
    with open('stoplist.txt') as f:
        stopwords = f.read().splitlines()
    stopwords = [re.sub(r'[0-9]+|\W+|_', '', word) for word in stopwords]
    stopwords = [word.lower() for word in stopwords if len(word) > 1]
    return stopwords

# This method takes path of HTML file and return list of tokens
def extract_tokens(file_path, stopwords):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as fp:
        soup = BeautifulSoup(fp, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    words = text.split()
    words = [re.sub(r'[0-9]+|\W+|_', '', word) for word in words]
    words = [word.lower() for word in words if len(word) > 1 and (word not in stopwords)]
    return words

def update_inverted_index(inverted_index, filename, tokens):
    for token in tokens:
        if token in inverted_index:
            if filename in inverted_index[token]:
                inverted_index[token][filename] += 1
            else:
                inverted_index[token][filename] = 1
        else:
            inverted_index[token] = {filename: 1}
    return inverted_index

# This method takes inverted_index and words_counts and generate postings_list
def create_postings_list(inverted_index, words_count_in_docs):
    postings_list = inverted_index
    # number of documents a word w occures in
    document_frequencies = { key:len(val) for key, val in inverted_index.items() }
    for word, counts in inverted_index.items():
        for doc, word_count in counts.items():
            # calculating term weight using tf and idf
            tf = word_count/words_count_in_docs[doc]
            idf = 503/document_frequencies[word]
            postings_list[word][doc] = tf * idf
    return postings_list

# This method takes output_dir and creates 2 frequency files
def create_wts_files(words_in_files, postings_list, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("The new directory is created!")
    for filename, words in words_in_files.items():
        filepath = output_dir + '/' + filename.split('.')[0]+'.wts'
        with open(filepath, 'w') as f:
            for word in list(set(words)):
                if word in postings_list:
                    f.write(word + ' ' + str(postings_list[word][filename]) + '\n')

# Remove the words which occurs only once in the entire corpus
def remove_rare_words(inverted_index):
    return { key:val for key, val in inverted_index.items() if len(val) > 1 or list(val.values())[0] > 1 }

# This methods plots grapth between no of files and time taken in processing them
def plot_graph(x_values, y_values):
    plt.plot(x_values, y_values)
    plt.title('Time vs Number of Documents Processed')
    plt.xlabel('Documents Processed Count')
    plt.ylabel('Time taken (in milliseconds)')
    plt.show()

def tokenize_words(input_dir, output_dir):
    main(input_dir, output_dir)


'''
deprecated
'''
# Create separate file of words for each input file
def create_token_files(output_dir, filename, words):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("The new directory is created!")
    filepath = output_dir + '/' + filename.split('.')[0]+'.txt'
    with open(filepath, 'w') as f:
        for word in words:
            f.write(word)
            f.write('\n')