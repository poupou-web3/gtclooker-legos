import tweepy
import config
import os

TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
TWITTER_API_KEY_SECRET = os.environ["TWITTER_API_KEY_SECRET"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

auth = tweepy.OAuth1UserHandler(
  TWITTER_API_KEY, 
  TWITTER_API_KEY_SECRET, 
  TWITTER_ACCESS_TOKEN, 
  TWITTER_ACCESS_TOKEN_SECRET
)

api = tweepy.API(auth)

def get_followers_count(screen_name):
    try:
        screen_name = screen_name.split("/")[-1]
        user = api.get_user(screen_name=screen_name)
        return user.followers_count
    except Exception as e:
        return None