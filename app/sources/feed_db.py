from datetime import datetime
from typing import List

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from app.utils import get_env
from app.models import Event


def get_db_engine():
    DATABASE_URI = get_env('DB_URI')
    return create_engine(DATABASE_URI)


def fetch_new_entries(timestamp: str) -> List[Event]:
    """
    Fetch new entries from the database.

    Args:
        current_timestamp (str): timestamp in format 'YYYY-MM-DD'

    Returns:
        List[Event]:
    """
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    dl_feed_news = Table('dl_feed_news', metadata, autoload_with=engine)
    dl_feed_tweets = Table('dl_feed_tweets', metadata, autoload_with=engine)

    events: List[Event] = []
    delta_datetime = datetime.strptime(timestamp, '%Y-%m-%d')

    with session.begin():
        # Fetch new news entries
        news_query = dl_feed_news.select().where(
            dl_feed_news.c.pub_date <= delta_datetime
        ).order_by(dl_feed_news.c.pub_date.desc()).limit(20)
        news_results = session.execute(news_query).fetchall()
        events.extend([Event(type='news', data=dict(news._mapping)) for news in news_results])

        # Fetch new tweets
        tweets_query = dl_feed_tweets.select().where(
            dl_feed_tweets.c.tweet_created_at <= delta_datetime
        ).order_by(dl_feed_tweets.c.tweet_created_at.desc()).limit(20)
        tweets_results = session.execute(tweets_query).fetchall()
        events.extend([Event(type='tweet', data=dict(tweet._mapping)) for tweet in tweets_results])

    return events
