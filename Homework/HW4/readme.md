## Homework 4: Apache Airflow Recommendation Pipeline

**Overview:**  This project recreates the recommendation system developed in Homework 2 using Amazon Managed Workflows for Apache Airflow (MWAA). The goal is to generate BERT-based movie embeddings, process MovieLens ratings data over four simulated arrival periods, compute user embeddings, and generate movie recommendations for both cold users and highly active users. All intermediate and final outputs are stored in Amazon S3.

**How to Run the Code**: 
- Clone the repository and navigate to the HW_4 folder in Github:
- Upload the DAG files to the MWAA DAG folder in the project S3 bucket.
- Ensure the MovieLens 1M dataset files (movies.dat and ratings.dat) are stored in: s3://de300-airflow-rmj/data/
- Activate both DAGs in the MWAA environment and allow them to run according to their schedules.

Project Structure
- homework_4/
- dag1_bert_embeddings.py
- recommendation_pipeline.py
- readme.md
- info.txt
- report.pdf

**What the Code Does** 
1. **Movie Embedding Generation:** Downloads movies.dat from Amazon S3 and generates BERT-based movie embeddings using the SentenceTransformers model all-MiniLM-L6-v2.
Movie titles and genres are combined into a text representation and converted into embedding vectors.

    The resulting files are uploaded to S3:
  - movies_all.csv
  - movie_embeddings_all.npy

2. **Ratings Processing:** Ratings are divided into four timestamp-based partitions to simulate observations arriving over time:
  Part I: 04/25/2000 - 08/03/2000
  Part II: 08/04/2000 - 10/31/2000
  Part III: 11/01/2000 - 11/26/2000
  Part IV: 11/26/2000 and later

    Each run loads the newest partition and combines it with all previously observed ratings.
  
3. **User Embedding Generation:** A random 30% sample of available users is selected.

    For each sampled user, movie embeddings from positively rated movies (rating ≥ 4) are averaged to create a user embedding.

    User embeddings are saved as: user_embeddings.json

4. **Recommendation Generation:** Recommendations are generated for two user types:
  - Cold User: Recommendations are based on the most frequently rated movies observed so far.
  - Top User: A user is randomly selected from the top 5% of users by number of ratings.

    Recommendations are generated using cosine similarity between the user embedding and movie embeddings while excluding previously rated movies.

**Expected Outputs**
- Embedding Files
  - movies_all.csv
  - movie_embeddings_all.npy

**User Embedding File**
- user_embeddings.json

**Cumulative Ratings File**
- cumulative_ratings.csv

**Recommendation Files**
- Recommendation files are uploaded to: recommendations/

**Example outputs:**
- recommendations_iter1_YYYYMMDD_HHMMSS.csv
- recommendations_iter2_YYYYMMDD_HHMMSS.csv
- recommendations_iter3_YYYYMMDD_HHMMSS.csv
- recommendations_iter4_YYYYMMDD_HHMMSS.csv

**Each file contains:**
- User_Type
- Last_Interaction_Time
- User_Summary
- Recommended_Movies

**Key Findings:** Movie embeddings only need to be generated once and can be reused throughout the recommendation pipeline.
Incremental processing allows the recommendation system to simulate newly arriving observations while preserving previous data.
Sampling 30% of users reduces computational cost while still producing meaningful recommendation outputs.
Embedding-based recommendations provide personalized suggestions for active users while popularity-based recommendations provide recommendations for cold users.

**Notes:** Movie embeddings are generated using SentenceTransformers and stored in Amazon S3 for reuse.
Recommendation outputs use timestamped filenames to prevent overwriting outputs from previous iterations.
All intermediate datasets are stored in Amazon S3 to support reproducibility and future analysis.

**AI Usage:** ChatGPT was used for debugging MWAA deployment issues, Airflow DAG development, package installation troubleshooting, and documentation support. All code execution and results were verified by the project team.

