# DATA_ENG_300_HW2_Westra_Maya

## Overview
This project implements a BERT-based movie recommendation pipeline using the MovieLens 1M dataset and AWS S3.

The workflow includes:
- checking and storing the dataset in S3,
- generating BERT embeddings,
- creating recommendations for cold and top users,
- generating recommendations using the full dataset,
- and creating personalized recommendations using a custom user profile.

## Files
- DATA_ENG_300_HW2_Westra_Maya.ipynb
  Main notebook with code, outputs, and explanations.

- DATA_ENG_300_HW2_Westra_Maya.html
  Exported notebook with outputs visible and code hidden.

- README.md
  Project documentation and execution instructions.

## Technologies Used
- Python
- AWS S3
- boto3
- pandas
- NumPy
- SentenceTransformers
- scikit-learn

## How to run Assignment
1. Open Jupyter Notebook or JupyterLab.

2. Install required packages if necessary: (pip install boto3 pandas numpy sentence-transformers scikit-learn) 

3. Configure AWS credentials:

aws configure

Provide:
- AWS Access Key ID
- AWS Secret Access Key
- region: us-east-1
- output format: json

4. Run the notebook cells sequentially from top to bottom.

## Expected Outputs 
If the notebook runs successfully, the following outputs should be generated:

- verification that the MovieLens dataset exists in S3,
- movie embeddings for pre-1980 movies,
- recommendation tables for cold users and top users,
- full dataset recommendation outputs,
- personalized movie recommendations,
- intermediate and final CSV/NumPy outputs uploaded to S3.

## Recommendation Method
Movie embeddings are generated using the `all-MiniLM-L6-v2` SentenceTransformer model. Recommendations are generated using cosine similarity between averaged user embeddings and movie embeddings.

## AI Usage
ChatGPT was used to assist with debugging AWS/S3 configuration issues, notebook organization, markdown drafting, and workflow explanations. All code was reviewed, tested, and executed by the author.
