import sys
import time
from tokenize_search import tokenize_words

def calculate_weights(input_dir, output_dir):
    tokenize_words(input_dir, 'text_files_dir')

if __name__ == "__main__":
    start = time.process_time_ns()
    print('All the times are in milliseconds')
    calculate_weights(sys.argv[1], sys.argv[2])
    end = time.process_time_ns()
    print("Total elapsed time:", (end - start)/1000000)