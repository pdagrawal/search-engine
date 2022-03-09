import os
import time
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt

# This method is responsible to call all the methods in the required sequence
def main(input_dir, output_dir):
    file_count = 0
    file_values = []
    time_values = []
    start = time.process_time_ns()
    stopwords = load_stop_words()
    for filename in os.scandir(input_dir):
        if filename.is_file():
            file_count += 1
            tokens = extract_tokens(filename.path, stopwords)
            create_token_files(output_dir, filename.name, tokens)
        if file_count%50 == 0:
            file_values.append(file_count)
            time_values.append(time.process_time_ns()/1000000)
            end = time.process_time_ns()
            print(f'Parsed Files {file_count} and Time taken {(end - start)/1000000}')
            start = time.process_time_ns()
    create_frequency_files(output_dir)
    plot_graph(file_values, time_values)


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

'''
This method takes output_dir, filename and tokens and write them into a text
file separate by newline
'''
def create_token_files(output_dir, filename, words):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("The new directory is created!")
    filepath = output_dir + '/' + filename.split('.')[0]+'.txt'
    with open(filepath, 'w') as f:
        for word in words:
            f.write(word)
            f.write('\n')

# This method takes output_dir and creates 2 frequency files
def create_frequency_files(output_dir):
    frequency_book = {}
    for filename in os.scandir(output_dir):
        if filename.is_file():
            with open(filename.path) as f:
                tokens = f.read().splitlines()
                for token in tokens:
                    if token in frequency_book:
                        frequency_book[token] += 1
                    else:
                        frequency_book[token] = 1
    processed_frequency_book = { key:val for key, val in frequency_book.items() if val != 1 }
    with open('frequencies_sorted_by_token.txt', 'w') as f:
        for word in sorted(processed_frequency_book.keys()):
            f.write(word + ' ' + str(processed_frequency_book[word]) + '\n')

    with open('frequencies_sorted_by_frequency.txt', 'w') as f:
        for word, frequency in sorted(processed_frequency_book.items(), key=lambda x: x[1], reverse=True):
            f.write(word + ' ' + str(frequency) + '\n')

# This methods plots grapth between no of files and time taken in processing them
def plot_graph(x_values, y_values):
    plt.plot(x_values, y_values)
    plt.xlabel('Documents Processed Count')
    plt.ylabel('Time taken (in milliseconds)')
    plt.title('Time vs Number of Documents Processed')
    plt.show()


def tokenize_words(input_dir, output_dir):
    # start = time.process_time_ns()
    # print('All the times are in milliseconds')
    main(input_dir, output_dir)
    # end = time.process_time_ns()
    # print("Total elapsed time:", (end - start)/1000000)
