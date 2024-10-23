import os
import re
import sys
import numpy as np
import pandas as pd

# All values come from the model trained on the data from survey.
FEATURE_MEAN = np.array([0.07916667, 28.79916667, 1.49, 1.77666667, 0.36583333, 12.9, 15.22916667, 7.9025])
FEATURE_STD = np.array([0.14822945, 8.57692831, 0.75379042, 0.57920531, 0.14323905, 14.38345009, 21.13728952, 2.04951934])

MODEL_COEFFICIENTS = np.array([-0.32295017, -0.02162178, -0.14302383,  0.16994715,  0.53624519, -0.87802927, 0.94317421, -0.08688262])
MODEL_INTERCEPT = -0.27823503

def extract_features(code):
    # https://go101.org/article/keywords-and-identifiers.html
    go_keywords = [
        'break', 'default', 'func', 'interface', 'select', 'case', 'defer', 'go',
        'map', 'struct', 'chan', 'else', 'goto', 'package', 'switch', 'const',
        'fallthrough', 'if', 'range', 'type', 'continue', 'for', 'import',
        'return', 'var',
    ]

    # Patterns for numbers, identifiers, comments etc.
    number_pattern = re.compile(r'\b\d+(\.\d+)?\b')
    identifier_pattern = re.compile(r'\b[_a-zA-Z][_a-zA-Z0-9\.]*\b')
    comment_pattern = re.compile(r'//.*|/\*.*?\*/', re.DOTALL)
    operator_pattern = re.compile(r'(\+\+|--|==|!=|<=|>=|<<|>>|&&|\|\||[\+\-\*/%&\|\^~<>]=?)')
    whitespace_pattern = re.compile(r'\s+')

    total_line_length = 0
    max_line_length = 0

    total_identifiers = 0
    max_identifiers = 0

    total_identifier_length = 0
    max_identifier_length = 0

    total_indentation = 0
    max_indentation = 0

    total_keywords = 0
    max_keywords = 0

    total_numbers = 0
    max_numbers = 0

    total_comments = 0
    total_comments_len = 0
    total_strings = 0
    total_strings_len = 0
    total_periods = 0
    total_commas = 0
    total_spaces = 0
    total_parentheses = 0
    total_arithmetic_ops = 0
    total_comparison_ops = 0
    total_assignments = 0
    total_blank_lines = 0

    total_lines = 0

    in_block_comment = False

    for line in code.splitlines():
        total_lines += 1
        stripped_line = line.strip('\n')

        # Check for blank lines
        if not stripped_line.strip():
            total_blank_lines += 1
            continue

        # Handle block comments
        comment_start = stripped_line.find('//')
        if comment_start != -1:
            total_comments += 1
            total_comments_len = len(line[comment_start+2:].strip())
            continue
           

        # Remove strings and character literals to avoid counting operators inside them
        stripped_line = re.sub(r'"(\\.|[^"\\])*"', '', stripped_line)
        stripped_line = re.sub(r"'(\\.|[^'\\])*'", '', stripped_line)

        # Line length
        line_length = len(stripped_line)
        total_line_length += line_length
        max_line_length = max(max_line_length, line_length)

        # Indentation
        indentation = len(line) - len(line.lstrip('\t'))
        total_indentation += indentation
        max_indentation = max(max_indentation, indentation)

        # Identifiers
        identifiers = identifier_pattern.findall(stripped_line)
        identifiers = [id for id in identifiers if id not in go_keywords and not number_pattern.match(id)]
        num_identifiers = len(identifiers)
        total_identifiers += num_identifiers
        max_identifiers = max(max_identifiers, num_identifiers)

        # Identifier lengths
        identifier_lengths = [len(id) for id in identifiers]
        if identifier_lengths:
            max_id_length_in_line = max(identifier_lengths)
            max_identifier_length = max(max_identifier_length, max_id_length_in_line)
            total_identifier_length += sum(identifier_lengths)

        # Keywords
        keywords_in_line = [word for word in identifiers if word in go_keywords]
        num_keywords = len([word for word in identifier_pattern.findall(stripped_line) if word in go_keywords])
        total_keywords += num_keywords
        max_keywords = max(max_keywords, num_keywords)

        # Numbers
        numbers_in_line = number_pattern.findall(stripped_line)
        num_numbers = len(numbers_in_line)
        total_numbers += num_numbers
        max_numbers = max(max_numbers, num_numbers)

        # Strings
        strings = re.findall(r'"(.*?)"', line)
        if strings:
            total_strings += len(strings)
            total_strings_len += sum(len(s) for s in strings)

        # Periods, commas, spaces, parentheses
        total_periods += stripped_line.count('.')
        total_commas += stripped_line.count(',')
        total_spaces += stripped_line.count(' ')
        total_parentheses += stripped_line.count('(') + stripped_line.count(')') + stripped_line.count('{') + stripped_line.count('}')

    # Compute averages
    avg_line_length = total_line_length / total_lines if total_lines else 0
    avg_identifiers = total_identifiers / total_lines if total_lines else 0
    avg_identifier_length = total_identifier_length / total_identifiers if total_identifiers else 0
    avg_indentation = total_indentation / total_lines if total_lines else 0
    avg_keywords = total_keywords / total_lines if total_lines else 0
    avg_numbers = total_numbers / total_lines if total_lines else 0
    avg_comments = total_comments / total_lines if total_lines else 0
    avg_comment_len = total_comments_len / total_comments if total_comments else 0
    avg_strings = total_strings / total_lines if total_lines else 0
    avg_strings_len = total_strings_len / total_strings if total_strings else 0
    avg_periods_and_commas = (total_periods+total_commas) / total_lines if total_lines else 0
    avg_commas = total_commas / total_lines if total_lines else 0
    avg_spaces = total_spaces / total_lines if total_lines else 0
    avg_parentheses = total_parentheses / total_lines if total_lines else 0
    avg_blank_lines = total_blank_lines / total_lines if total_lines else 0

    # Output only the ones used in the model
    features = {
        'avg_strings': avg_strings,
        'avg_line_length': avg_line_length,
        'avg_commas_periods': avg_periods_and_commas,
        'avg_num_identifiers': avg_identifiers,
        'avg_keywords': avg_keywords,
        'avg_strings_len': avg_strings_len,
        'avg_comment_len': avg_comment_len,
        'avg_identifier_len': avg_identifier_length,
    }

    return features

def normalize_features(features):
    feature_array = np.array([features[feat] for feat in features])
    normalized_features = (feature_array - FEATURE_MEAN) / FEATURE_STD
    return normalized_features

def calculate_readability_score(normalized_features):
    score = np.dot(normalized_features, MODEL_COEFFICIENTS) + MODEL_INTERCEPT
    return score

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def main():
    if len(sys.argv) != 2:
        print("Usage: python rate_snippet.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist.")
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as file:
        code = file.read()

    features = extract_features(code)
    normalized_features = normalize_features(features)

    score = np.dot(normalized_features, MODEL_COEFFICIENTS) + MODEL_INTERCEPT
    # Convert the score to [0, 1] using the sigmoid function
    normalized_score = sigmoid(score)

    print(f"Readability score: {normalized_score:.2f}")

if __name__ == "__main__":
    main()