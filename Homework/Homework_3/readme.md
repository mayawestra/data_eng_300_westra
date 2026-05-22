# Homework 3 — NYC Taxi Analytics with PySpark, EC2, and S3

## Overview
This project analyzes NYC TLC Yellow and Green Taxi trip records for January 2026 using PySpark on AWS EC2. It covers data ingestion from S3, schema standardization, data cleaning, analytical queries, and a Random Forest fare prediction model.

## Requirements

### EC2 Setup
- **AMI:** Amazon Linux 2023
- **Region:** us-east-1

### Software
- sudo dnf install -y java-17-amazon-corretto-devel python3 python3-pip git
- python3 -m venv ~/pyspark-venv
- source ~/pyspark-venv/bin/activate
- pip install pyspark jupyter pandas pyarrow matplotlib

## How to Run

### 1. SSH into your EC2 instance
- ssh -i your-key.pem ec2-user@your-ec2-public-dns

### 2. Start Jupyter Notebook
- source ~/pyspark-venv/bin/activate
- jupyter notebook --no-browser --port=8888 --ip=0.0.0.0

### 3. Open a tunnel from your local machine
- ssh -i your-key.pem -L 8888:localhost:8888 ec2-user@your-ec2-public-dns
- go to `http://localhost:8888` in your browser and enter the token.

### 4. Configure AWS credentials
At the start of each session, refresh credentials from AWS Academy:
- !aws configure set aws_access_key_id YOUR_KEY
- !aws configure set aws_secret_access_key YOUR_SECRET
- !aws configure set aws_session_token YOUR_TOKEN
- !aws configure set region us-east-1

### 5. Open and run the notebook
- Upload `HW3_NYC_Taxi_Analytics.ipynb` to Jupyter and run all cells top to bottom 

### 6. Update your S3 bucket name
- In Part 7, replace `de300-hw3-westra` with your own S3 bucket name before running the write cells.


## S3 Output Paths
Results are written to:
```
s3://de300-hw3-westra/nyc-taxi-assignment/trips_by_type.csv
s3://de300-hw3-westra/nyc-taxi-assignment/avg_fare_by_type.csv
s3://de300-hw3-westra/nyc-taxi-assignment/pickups_by_hour.csv
s3://de300-hw3-westra/nyc-taxi-assignment/predicted_vs_actual.png
```

## AI Usage
Claude (Anthropic) was used to assist with debugging PySpark setup, fixing AWS credential errors, and structuring the notebook. 

