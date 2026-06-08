from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime

BUCKET = "de300-airflow-rmj"

def generate_bert_embeddings():
    import subprocess, sys, traceback, boto3

    # Force install everything we need at runtime
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "pandas>=2.0,<3.0", "numpy<2.0", "scikit-learn",
        "sentence-transformers==2.7.0", "--quiet"
    ])

    s3 = boto3.client("s3")

    try:
        import pandas as pd
        import numpy as np
        from sentence_transformers import SentenceTransformer

        print("Downloading movies.dat...")
        s3.download_file(BUCKET, "data/movies.dat", "/tmp/movies.dat")

        movies = pd.read_csv(
            "/tmp/movies.dat", sep="::", engine="python",
            encoding="latin-1", names=["MovieID", "Title", "Genres"]
        )
        print(f"Loaded {len(movies)} movies.")

        movies["Text"] = movies["Title"].fillna("") + " Genres: " + movies["Genres"].fillna("")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(movies["Text"].tolist(), show_progress_bar=False, convert_to_numpy=True)
        print(f"Embeddings shape: {embeddings.shape}")

        movies.to_csv("/tmp/movies_all.csv", index=False)
        np.save("/tmp/movie_embeddings_all.npy", embeddings)

        s3.upload_file("/tmp/movies_all.csv", BUCKET, "intermediate/movies_all.csv")
        s3.upload_file("/tmp/movie_embeddings_all.npy", BUCKET, "intermediate/movie_embeddings_all.npy")
        print("Done!")

    except Exception as e:
        s3.put_object(Bucket=BUCKET, Key="intermediate/error_log.txt", Body=traceback.format_exc())
        raise

with DAG(
    dag_id="dag1_bert_embeddings",
    start_date=datetime(2024, 1, 1),
    schedule="@once",
    catchup=False,
    tags=["hw4"],
) as dag:
    PythonOperator(task_id="generate_bert_embeddings", python_callable=generate_bert_embeddings)
