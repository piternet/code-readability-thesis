import os
import sys
import csv
import re

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

def load_readability_ratings(ratings_file):
    ratings_dict = {}  # filename -> list of ratings
    with open(ratings_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            if len(row) != 2:
                continue  # Skip invalid rows
            filename, rating = row
            try:
                rating = float(rating)
            except ValueError:
                continue  # Skip rows with invalid rating
            if filename in ratings_dict:
                ratings_dict[filename].append(rating)
            else:
                ratings_dict[filename] = [rating]
    average_ratings = {}
    for filename, ratings in ratings_dict.items():
        average_ratings[filename] = sum(ratings) / len(ratings)
    return average_ratings

def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_features.py <directory_path> <ratings_file_path>")
        sys.exit(1)
    
    directory = sys.argv[1]
    ratings_file = sys.argv[2]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)
    
    if not os.path.isfile(ratings_file):
        print(f"Error: {ratings_file} is not a valid file.")
        sys.exit(1)
    
    fieldnames = [
        'snippet_filename', 'readability_rating', 'total_lines', 'avg_line_length', 'max_line_length',
        'avg_num_identifiers', 'max_num_identifiers', 'avg_identifier_len', 'max_identifier_len',
        'avg_indentation', 'max_indentation', 'avg_keywords', 'avg_numbers', 'avg_comments',
        'avg_comment_len', 'avg_strings', 'avg_strings_len', 'avg_commas_periods', 'avg_spaces',
        'avg_parenthesis', 'avg_blank_lines'
    ]
    
    average_ratings = load_readability_ratings(ratings_file)
    
    data = []
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            features = extract_features(code)

            readability_rating = average_ratings.get(filename, None)
            if readability_rating is None:
                print(f"Warning: No readability rating for {filename}", file=sys.stderr)
                continue  # Skip files without rating
            # Combine filename, readability_rating, and features into one dictionary
            row = {
                'snippet_filename': filename,
                'readability_rating': readability_rating
            }
            row.update(features)
            data.append(row)
    
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        # Format float values to two decimal points
        formatted_row = {}
        for key, value in row.items():
            if isinstance(value, float):
                formatted_row[key] = f"{value:.2f}"
            else:
                formatted_row[key] = value
        writer.writerow(formatted_row)

if __name__ == "__main__":
    main()