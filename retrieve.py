import sys
import os
import time
from indexing import load_stop_words
from prettytable import PrettyTable


# This method is responsible to call all the methods in the required sequence
def main(query_words, query_wts = None):
    query_words = [word.lower() for word in query_words.split(',') if len(word) > 1 and (word not in load_stop_words())]
    postings_list = get_postings_for_query(query_words)
    query_weights = calculate_query_weights(query_words, query_wts)
    documents = {key: 0 for key in sorted(os.listdir('files/'))}
    numerator_values = calculate_numerators(query_words, postings_list, query_weights, documents)
    query_denominator = square_root_of_sum_of_squares(query_weights.values())
    similarity_scores = calculate_similarity(query_words, postings_list, numerator_values,
                                            query_denominator, documents)
    search_result = PrettyTable()
    search_result.field_names = ["Rank", "Document ID", "Similarity Score"]
    for index, name in enumerate(list(similarity_scores.keys())[:10]):
        if similarity_scores[name] != 0:
            search_result.add_row([index + 1, name, similarity_scores[name]])
    print(search_result)
    if list(similarity_scores.values())[0] == 0:
        print('No matching document found')


# Read dictionary and posting files to get postings list
def get_postings_for_query(query_words):
    postings_list = {}
    with open('output_files/dictionary_file.txt', 'r') as f:
        dictionaries = f.read().splitlines()
    with open('output_files/posting_file.txt', 'r') as f:
        postings = f.read().splitlines()
    for word in query_words:
        if word in postings_list:
            continue
        else:
            postings_list[word] = {}
        if word in dictionaries:
            word_index = dictionaries.index(word)
            starting_index = int(dictionaries[word_index+2])
            for i in range(0,int(dictionaries[word_index+1])):
                posting = postings[starting_index-1+i]
                postings_list[word][posting.split(',')[0]] = float(posting.split(',')[1])
    return postings_list

# Calculate query weights using their frequency in query
def calculate_query_weights(words, weights):
    query_wts = {}
    if weights is None:
        for word in list(set(words)):
            query_wts[word] = words.count(word)/len(words)
    else:
        for word in list(set(words)):
            query_wts[word] = float(weights.split(',')[list(set(words)).index(word)])
    return query_wts

# Calculate numerators for each document
def calculate_numerators(query_words, postings_list, query_weights, numerators):
    for term in query_words:
        for doc in numerators.keys():
            if term in postings_list and doc in postings_list[term]:
                numerators[doc] += postings_list[term][doc] * query_weights[term]
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
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main(sys.argv[1])
    end = time.process_time_ns()
    print(f"Total elapsed time: {(end - start)/1000000} ms")