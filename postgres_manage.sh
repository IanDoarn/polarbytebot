sudo useradd postgres_reddit
sudo -iu postgres psql -c "CREATE USER postgres_reddit WITH PASSWORD 'password';"
sudo -iu postgres psql -c "CREATE DATABASE reddit_polarbytebot_db OWNER postgres_reddit;"
sudo -iu postgres_reddit psql -d reddit_polarbytebot_db -c "CREATE TABLE bot_comments (
    id BIGSERIAL PRIMARY KEY,
    thing_id VARCHAR(15) NOT NULL,
    content VARCHAR(10000) NOT NULL,
    submitted BOOLEAN NOT NULL,
    submitted_id VARCHAR(15));"
sudo -iu postgres_reddit psql -d reddit_polarbytebot_db -c "CREATE TABLE bot_submissions (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    content VARCHAR(15000),
    type VARCHAR(10) NOT NULL,
    subreddit VARCHAR(50) NOT NULL,
    submitted BOOLEAN NOT NULL);"
sudo -iu postgres_reddit psql -d reddit_polarbytebot_db -c "CREATE TABLE subreddit (
    website VARCHAR(10) PRIMARY KEY,
    last_submission BIGINT,
    last_comment BIGINT);"
sudo -iu postgres_reddit psql -d reddit_polarbytebot_db -c "CREATE TABLE anet_member (
    username VARCHAR(50) PRIMARY KEY);"
