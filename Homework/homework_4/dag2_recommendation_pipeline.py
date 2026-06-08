from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# ---- CONFIG ----
BUCKET = "de300-airflow-rmj"

PARTITIONS = [
    ("2000-04-25", "2000-08-03"),   # Part I   - run 1
    ("2000-08-04", "2000-10-31"),   # Part II  - run 2
    ("2000-11-01", "2000-11-26"),   # Part III - run 3
    ("2000-11-26", "2001-12-31"),   # Part IV  - run 4
]
# ----------------


def get_partition_index(execution_date):
    start = datetime(2024, 1, 1)
    diff_hours = (execution_date.replace(tzinfo=None) - start).total_seconds() / 3600
    if diff_hours < 10:
        return 0
    elif diff_hours < 20:
        return 1
    elif diff_hours < 30:
        return 2
    else:
        return 3


def load_ratings(**context):
    import boto3
    import pandas as pd

    s3 = boto3.client("s3")
    execution_date = context["logical_date"]
    partition_idx = get_partition_index(execution_date)
    start_date, end_date = PARTITIONS[partition_idx]

    print(f"Run {partition_idx + 1}/4 — Partition: {start_date} to {end_date}")

    s3.download_file(BUCKET, "data/ratings.dat", "/tmp/ratings.dat")
    ratings = pd.read_csv(
        "/tmp/ratings.dat",
        sep="::",
        engine="python",
        names=["UserID", "MovieID", "Rating", "Timestamp"],
        encoding="latin-1"
    )
    ratings["Date"] = pd.to_datetime(ratings["Timestamp"], unit="s")

    current = ratings[(ratings["Date"] >= start_date) & (ratings["Date"] <= end_date)].copy()
    print(f"Current partition: {len(current)} ratings, {current['UserID'].nunique()} users")

    try:
        s3.download_file(BUCKET, "intermediate/cumulative_ratings.csv", "/tmp/cumulative_ratings.csv")
        cumulative = pd.read_csv("/tmp/cumulative_ratings.csv")
        cumulative["Date"] = pd.to_datetime(cumulative["Date"])
        print(f"Loaded {len(cumulative)} cumulative ratings from previous runs.")
    except Exception:
        cumulative = pd.DataFrame(columns=["UserID", "MovieID", "Rating", "Timestamp", "Date"])
        print("No previous cumulative ratings, starting fresh.")

    combined = pd.concat([cumulative, current]).drop_duplicates()
    combined.to_csv("/tmp/cumulative_ratings.csv", index=False)
    s3.upload_file("/tmp/cumulative_ratings.csv", BUCKET, "intermediate/cumulative_ratings.csv")

    context["ti"].xcom_push(key="partition_idx", value=partition_idx)
    print(f"Combined ratings: {len(combined)} total")


def compute_user_embeddings(**context):
    import boto3
    import pandas as pd
    import numpy as np
    import json

    s3 = boto3.client("s3")

    s3.download_file(BUCKET, "intermediate/cumulative_ratings.csv", "/tmp/cumulative_ratings.csv")
    combined = pd.read_csv("/tmp/cumulative_ratings.csv")

    s3.download_file(BUCKET, "intermediate/movie_embeddings_all.npy", "/tmp/movie_embeddings_all.npy")
    s3.download_file(BUCKET, "intermediate/movies_all.csv", "/tmp/movies_all.csv")
    all_embeddings = np.load("/tmp/movie_embeddings_all.npy")
    movies = pd.read_csv("/tmp/movies_all.csv")

    movie_id_to_idx = {mid: i for i, mid in enumerate(movies["MovieID"])}

    all_users = combined["UserID"].unique()
    sample_size = max(1, int(len(all_users) * 0.30))
    sampled_users = np.random.choice(all_users, size=sample_size, replace=False)
    print(f"Computing embeddings for {len(sampled_users)}/{len(all_users)} users (30% sample)")

    user_embeddings = {}
    for user_id in sampled_users:
        user_ratings = combined[(combined["UserID"] == user_id) & (combined["Rating"] >= 4)]
        liked_ids = user_ratings["MovieID"].tolist()
        indices = [movie_id_to_idx[mid] for mid in liked_ids if mid in movie_id_to_idx]
        if indices:
            user_embeddings[int(user_id)] = all_embeddings[indices].mean(axis=0).tolist()

    with open("/tmp/user_embeddings.json", "w") as f:
        json.dump(user_embeddings, f)
    s3.upload_file("/tmp/user_embeddings.json", BUCKET, "intermediate/user_embeddings.json")
    print(f"Saved {len(user_embeddings)} user embeddings to S3.")


def generate_recommendations(**context):
    import boto3
    import pandas as pd
    import numpy as np
    import json
    import random
    from sklearn.metrics.pairwise import cosine_similarity

    s3 = boto3.client("s3")
    ti = context["ti"]
    partition_idx = ti.xcom_pull(key="partition_idx", task_ids="load_ratings")

    s3.download_file(BUCKET, "intermediate/cumulative_ratings.csv", "/tmp/cumulative_ratings.csv")
    s3.download_file(BUCKET, "intermediate/movie_embeddings_all.npy", "/tmp/movie_embeddings_all.npy")
    s3.download_file(BUCKET, "intermediate/movies_all.csv", "/tmp/movies_all.csv")
    s3.download_file(BUCKET, "intermediate/user_embeddings.json", "/tmp/user_embeddings.json")

    combined = pd.read_csv("/tmp/cumulative_ratings.csv")
    combined["Date"] = pd.to_datetime(combined["Date"])
    all_embeddings = np.load("/tmp/movie_embeddings_all.npy")
    movies = pd.read_csv("/tmp/movies_all.csv")
    with open("/tmp/user_embeddings.json") as f:
        user_embeddings = json.load(f)

    user_counts = combined.groupby("UserID").size()

    def recommend_cold_user(n=5):
        movie_counts = combined.groupby("MovieID").size().reset_index(name="NumRatings")
        candidates = movies.merge(movie_counts, on="MovieID", how="left")
        candidates["NumRatings"] = candidates["NumRatings"].fillna(0)
        recs = candidates.sort_values("NumRatings", ascending=False).head(n)
        return recs["Title"].tolist()

    def recommend_top_user(user_id, n=5):
        if str(user_id) not in user_embeddings:
            return []
        user_emb = np.array(user_embeddings[str(user_id)]).reshape(1, -1)
        scores = cosine_similarity(user_emb, all_embeddings)[0]
        movies_scored = movies.copy()
        movies_scored["score"] = scores
        seen_ids = set(combined[combined["UserID"] == user_id]["MovieID"])
        movies_scored = movies_scored[~movies_scored["MovieID"].isin(seen_ids)]
        recs = movies_scored.sort_values("score", ascending=False).head(n)
        return recs["Title"].tolist()

    cutoff = user_counts.quantile(0.95)
    top_user_ids = user_counts[user_counts >= cutoff].index.tolist()
    top_users_with_embeddings = [u for u in top_user_ids if str(u) in user_embeddings]
    top_user_id = random.choice(top_users_with_embeddings) if top_users_with_embeddings else top_user_ids[0]

    cold_recs = recommend_cold_user()
    top_recs = recommend_top_user(top_user_id)

    last_interaction_time = combined[combined["UserID"] == top_user_id]["Date"].max()

    recommendations = pd.DataFrame([
        {
            "User_Type": "Cold User",
            "Last_Interaction_Time": None,
            "User_Summary": "No previous interaction data available.",
            "Recommended_Movies": str(cold_recs)
        },
        {
            "User_Type": "Top User",
            "Last_Interaction_Time": str(last_interaction_time),
            "User_Summary": f"UserID {top_user_id}; total ratings = {user_counts[top_user_id]}; selected from top 5% of users by number of interactions.",
            "Recommended_Movies": str(top_recs)
        }
    ])

    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"recommendations_iter{partition_idx + 1}_{timestamp_str}.csv"
    local_path = f"/tmp/{filename}"
    recommendations.to_csv(local_path, index=False)
    s3.upload_file(local_path, BUCKET, f"recommendations/{filename}")
    print(f"Saved recommendations to s3://{BUCKET}/recommendations/{filename}")


with DAG(
    dag_id="dag2_recommendation_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=timedelta(hours=10),
    end_date=datetime(2024, 1, 3),
    catchup=True,
    max_active_runs=1,
    tags=["hw4"],
) as dag:

    t1 = PythonOperator(
        task_id="load_ratings",
        python_callable=load_ratings,
    )

    t2 = PythonOperator(
        task_id="compute_user_embeddings",
        python_callable=compute_user_embeddings,
    )

    t3 = PythonOperator(
        task_id="generate_recommendations",
        python_callable=generate_recommendations,
    )

    t1 >> t2 >> t3
