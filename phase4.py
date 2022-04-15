import sys
import os
import time
from bs4 import BeautifulSoup
import re

# This method is responsible to call all the methods in the required sequence
def main(input_dir, query_words, query_wts = None):
    query_words = query_words.split(',')
    query_weights = calculate_query_weights(query_words, query_wts)
    stopwords = load_stop_words()
    inverted_index = {}
    # number of words in a document after preprocessing
    words_count_in_docs = {}
    for filename in sorted(os.listdir(input_dir)):
        tokens = extract_tokens(input_dir + '/' + filename, stopwords)
        words_count_in_docs[filename] = len(tokens)
        update_inverted_index(inverted_index, filename, tokens)
    inverted_index = remove_rare_words(inverted_index)
    postings_list = create_postings_list(inverted_index, words_count_in_docs)
    documents = dict.fromkeys(words_count_in_docs, 0)
    numerator_values = calculate_numerators(query_words, postings_list, query_weights, documents)
    query_denominator = square_root_of_sum_of_squares(query_weights.values())
    similarity_scores = calculate_similarity(query_words, postings_list, numerator_values,
                                            query_denominator, documents)
    if list(similarity_scores.values())[0] == 0:
        print('No matching doc found')
        return
    for index, name in enumerate(list(similarity_scores.keys())[:10]):
        if similarity_scores[name] != 0:
            print(f'Rank: {index + 1} => {name} with score {similarity_scores[name]}')


# This method loads stopwords from the txt file and returns a list of them
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

# Updating the hash of inverted index to keep track of word count
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

# Remove the words which occurs only once in the entire corpus
def remove_rare_words(inverted_index):
    return { key:val for key, val in inverted_index.items() if len(val) > 1 or list(val.values())[0] > 1 }

# Calculate query weights using their frequency in query
def calculate_query_weights(words, weights):
    query_wts = {}
    if weights is None:
        for word in list(set(words)):
            query_wts[word] = words.count(word)/len(words)
    else:
        for word in list(set(words)):
            query_wts[word] = weights.split(',')[list(set(words)).index(word)]
    return query_wts

# Calculate numerators for each document
def calculate_numerators(query_words, postings_list, query_weights, numerators):
    for term in query_words:
        for doc in numerators.keys():
            if term in postings_list and doc in postings_list[term]:
                numerators[doc] += postings_list[term][doc] * float(query_weights[term])
    return numerators

def square_root_of_sum_of_squares(numbers):
    total = 0.0
    for number in numbers:
        total += float(number)**2
    return total**0.5

# This method calculates the similarity between query and document
def calculate_similarity(query_words, postings_list, numerator_values, query_denominator, similarity_dict):
    for doc, numerator in numerator_values.items():
        weights = []
        for term in query_words:
            if term in postings_list and doc in postings_list[term]:
                weights.append(postings_list[term][doc])
        doc_denominator = square_root_of_sum_of_squares(weights)
        denominator = query_denominator * doc_denominator
        similarity_dict[doc] = (numerator / denominator) if denominator != 0 else 0
    return dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True))


if __name__ == "__main__":
    start = time.process_time_ns()
    print('All the times are in milliseconds')
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2])
    end = time.process_time_ns()
    print("Total elapsed time:", (end - start)/1000000)
