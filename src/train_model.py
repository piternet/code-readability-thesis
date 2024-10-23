import os
import re
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from scipy.stats import pearsonr
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def extract_features_from_csv(snippet_filename, df):
    row = df[df['snippet_filename'] == snippet_filename]
    if row.empty:
        print(f"No data found for snippet {snippet_filename}")
        return None

    features = {
        'avg_line_length': row['avg_line_length'].values[0],
        'max_line_length': row['max_line_length'].values[0],
        'avg_num_identifiers': row['avg_num_identifiers'].values[0],
        'max_num_identifiers': row['max_num_identifiers'].values[0],
        'avg_identifier_len': row['avg_identifier_len'].values[0],
        'max_identifier_len': row['max_identifier_len'].values[0],
        'avg_indentation': row['avg_indentation'].values[0],
        'max_indentation': row['max_indentation'].values[0],
        'avg_keywords': row['avg_keywords'].values[0],
        'avg_numbers': row['avg_numbers'].values[0],
        'avg_comments': row['avg_comments'].values[0],
        'avg_comment_len': row['avg_comment_len'].values[0],
        'avg_strings': row['avg_strings'].values[0],
        'avg_strings_len': row['avg_strings_len'].values[0],
        'avg_commas_periods': row['avg_commas_periods'].values[0],
        'avg_spaces': row['avg_spaces'].values[0],
        'avg_parenthesis': row['avg_parenthesis'].values[0],
        'avg_blank_lines': row['avg_blank_lines'].values[0],
    }
    return features

def read_code_snippets(directory):
    snippets = []
    snippet_filenames = []
    for filename in os.listdir(directory):
        if filename.endswith('.go'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                code = file.read()
                snippets.append(code)
                snippet_filenames.append(filename)
    return snippets, snippet_filenames

def main():
    if len(sys.argv) != 3:
        print("Usage: python readability_model.py <code_snippets_directory> <labels_csv_file>")
        sys.exit(1)
    
    code_dir = sys.argv[1]
    labels_file = sys.argv[2]
    
    snippets, snippet_filenames = read_code_snippets(code_dir)
    if not snippets:
        print("No valid Go code snippets found in the specified directory.")
        sys.exit(1)
    
    df = pd.read_csv(labels_file)
    
    data = []
    for code, snippet_filename in zip(snippets, snippet_filenames):
        features = extract_features_from_csv(snippet_filename, df)
        if features is None:
            continue

        label_row = df[df['snippet_filename'] == snippet_filename]
        if label_row.empty:
            print(f"No label found for snippet {snippet_filename}.")
            continue
        readability_rating = label_row['readability_rating'].values[0]
        
        data.append({'snippet_filename': snippet_filename, **features, 'readability_rating': readability_rating})
    
    if not data:
        print("No data available after processing. Exiting.")
        sys.exit(1)
    
    df_data = pd.DataFrame(data)
    
    # Split readability labels into two classes 0/1 based on median
    median_rating = df_data['readability_rating'].median()
    df_data['readability_label'] = df_data['readability_rating'].apply(lambda x: 1 if x > median_rating else 0)
    
    feature_columns = ['avg_strings', 'avg_line_length', 'avg_commas_periods',
                       'avg_num_identifiers', 'avg_keywords', 'avg_strings_len', 'avg_comment_len', 'avg_identifier_len']
    
    X = df_data[feature_columns]
    X_normalized = (X - X.mean()) / X.std()
    y = df_data['readability_label']
    
    model = LogisticRegression()
    leave_one_out = LeaveOneOut()
    y_true = []
    y_pred = []
    
    for train_index, test_index in leave_one_out.split(X_normalized):
        X_train, X_test = X_normalized.iloc[train_index], X_normalized.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        model.fit(X_train, y_train)
        y_pred_prob = model.predict_proba(X_test)[:, 1]
        y_pred_label = (y_pred_prob >= 0.5).astype(int)
        
        y_true.extend(y_test)
        y_pred.extend(y_pred_label)
    

    print("Model performance:")
    print(f"Accuracy: {accuracy_score(y_true, y_pred):.2f}")
    print(f"Precision: {precision_score(y_true, y_pred):.2f}")
    print(f"Recall: {recall_score(y_true, y_pred):.2f}")
    print(f"F-score: {f1_score(y_true, y_pred):.2f}")
    
    print("\nConfusion matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    df_data = df_data.sort_values(by='snippet_filename')
    df_data['predicted_readability_label'] = y_pred
    
    output_columns = ['snippet_filename', 'readability_label', 'predicted_readability_label'] + feature_columns
    print("\nPredicted readability scores:")
    print(df_data[output_columns])

if __name__ == "__main__":
    main()