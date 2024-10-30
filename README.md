# Automated evaluation of code’s readability

This repository contains the snippets, survey results, scripts *Automated evaluation of code’s readability* Master's thesis project. The content here can be used to train the model on one's own dataset or use pre-trained model on the data from conducted survey to assess readability of given code snippet in Go.

## Repository contents

- `data/`: Contains survey data and CSV files with aggregated survey data and extracted features used for model training.
- `snippets/`: Example Go code snippets used in the survey and then for model training.
- `src/`: Source code for feature extraction and model training.

## Prerequisites

Before running the program, make sure you have the following installed:

- Python 3.x
- Go programming language (see [Go official website](https://go.dev/doc/install) for installation instructions)
- Required Python libraries (installable via `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/piternet/code-readability-master-thesis.git
   cd code-readability-master-thesis
   ```
2. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

You have two options to use the system: either train a new model on your custom code snippets or use the existing pre-trained model to evaluate Go code snippets. 

You can also adjust the code to work with any programming language, not just Go - for that you need to implement a custom parser, outputting CSV file with code features in a format following the one specified in `src/features.csv`.

### Option 1: Use pre-trained model

1. **Prepare code snippet**:
   Get your Go code snippet in one file available at `/path/your_snippet.go`.

2. **Rate the code snippet**:
   Run the following command to evaluate the quality of the Go code snippet using the pre-trained model:
   ```bash
   python src/rate_snippet.py /path/your_snippet.go
   ```

3. **Output**:
   The program will output a quality rating based on the trained model, providing insights into the quality of the code.


### Option 2: Train on your own data

1. **Prepare snippets**: 
   Get all Go code snippets available in one directory, e.g. `/path/snippets/`.

2. **Prepare training data**: 
   Get your training data available at `/path/training_data.csv`. The file should be a CSV containing a list of single ratings for all snippets within `/path/snippets/`, with two columns: `filename` and `readability_rating`.
   
   Example file:

    ```
   filename   readability_rating
   1.go     4
   1.go     5
   2.go     7
   2.go     4
   3.go     5
   ```

3. **Extract features**:
   Run the feature extraction script:
   ```bash
   python src/extract_features.py /path/snippets/ > data/extracted_features.csv
   ```

5. **Train the model**:
   Use the following command to train the model on your data:
   ```bash
   python src/train_model.py /path/training_data.csv data/extracted_features.csv
   ```
