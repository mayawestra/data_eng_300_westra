# Lab 8 Submission 
## Maya Westra 

## What is the partition key of plays_by_user?

The partition key is `user_id`. This means all listening events for the same user are stored together on the same Cassandra node. 

## What are the clustering columns of plays_by_user?

The clustering columns are `played_at` and `song_id`. For each user, rws are physically sorted by `played_at` descending (most recent first), then by `song_id` to ensure uniqueness when two songs are played at the exact same timestamp.

## Why did we create both plays_by_user and plays_by_song instead of using one table?

Cassandra requires queries to filter by the partition key. If we only had `plays_by_user`, we could efficiently look up plays for a given user, but we could not efficiently look up all users who played a given song — that would require scanning every partition in the table. By creating a second table with `song_id` as the partition key, we can answer both queries efficiently. 

## What happens if you try to query plays_by_user by song_id only?

I got ``` InvalidRequest: Error from server: code=2200 [Invalid query] message="PRIMARY KEY column "song_id" cannot be restricted as preceding column "played_at" is not restricted' ```  Since `song_id` is a clustering column (not the partition key), Cassandra cannot route the query to a specific node. 

## Why is data duplication common in Cassandra?

Because Cassandra doesn't support joins, the same data often needs to be stored in multiple tables to answer different queries efficiently. This is the opposite of relational databases where you use joins when querying. 

## Include a screenshot or copied output of: - SELECT * FROM plays_by_user WHERE user_id = 'u1'; - SELECT * FROM plays_by_song WHERE song_id = 's1';

```
cqlsh:music_app> SELECT * FROM plays_by_user WHERE user_id = 'u1';

 user_id | played_at                       | song_id | artist        | device | title
---------+---------------------------------+---------+---------------+--------+-----------------
      u1 | 2026-05-01 10:10:00.000000+0000 |      s3 | Billie Eilish | laptop |         bad guy
      u1 | 2026-05-01 10:05:00.000000+0000 |      s2 |    The Weeknd | iphone | Blinding Lights
      u1 | 2026-05-01 10:00:00.000000+0000 |      s1 |  Taylor Swift | iphone |       Anti-Hero

(3 rows)

cqlsh:music_app> SELECT * FROM plays_by_song WHERE song_id = 's1';

 song_id | played_at                       | user_id | artist       | device  | title
---------+---------------------------------+---------+--------------+---------+-----------
      s1 | 2026-05-01 12:00:00.000000+0000 |      u3 | Taylor Swift |  laptop | Anti-Hero
      s1 | 2026-05-01 11:00:00.000000+0000 |      u2 | Taylor Swift | android | Anti-Hero
      s1 | 2026-05-01 10:00:00.000000+0000 |      u1 | Taylor Swift |  iphone | Anti-Hero

(3 rows)
```

## Submit the two exported CSV files: - plays_by_user.csv - plays_by_song.csv
