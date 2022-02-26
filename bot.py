import os
import sys

import time
import random

import requests
import schedule
import math

from dotenv import load_dotenv
from os.path import exists

import praw
import markovify
from colorama import Fore, Back, Style
from textblob import TextBlob


class Bot:
    def __init__(self, username, password, client, secret, user_agent):
        self.username = username
        self.password = password
        self.client = client
        self.secret = secret
        self.user_agent = user_agent

        self.r = praw.Reddit(
            client_id=self.client,
            client_secret=self.secret,
            username=self.username,
            password=self.password,
            user_agent=self.user_agent
        )

        with open('./lists/avoid_words.txt', 'r') as f:
            self.bad_words = f.read().splitlines()
        f.close()



    def _get_random_subreddit(self):
        '''Get a random subreddit'''

        with open('lists/subreddits.txt', 'r') as f:
            subreddits = f.read().splitlines()
        f.close()

        return random.choice(subreddits)


    def _avoid_bad_words(self, comment):
        '''Avoid bad words'''

        for word in self.bad_words:
            if word in comment.body:
                return True
        return False


    def _scrape_comments_from_subreddit(self, name):
        '''Scrape comments from a subreddit'''
        print(Fore.GREEN + 'scraping comments from subreddit: ')

        subreddit = self.r.subreddit(name)
        print(Fore.CYAN + subreddit.display_name)


        path_to_file = './data/' + name + '.txt'
        if not exists(path_to_file):
            f = open(path_to_file, 'x')

        # Iterate through the hot submissions
        for submission in subreddit.hot(limit=10):
            submission.comments.replace_more(limit=0)

            all_comments = submission.comments.list()

            if len(all_comments) > 0:
                # print(len(all_comments))

                # Iterate through all the comments
                for comment in all_comments:

                    if self._avoid_bad_words(comment):
                        # print("bad comment")
                        continue

                    with open(path_to_file, 'a') as f:
                        f.write(comment.body)
            else:
                # print(Fore.WHITE + 'no comments')
                continue

        f.close()

    def scrape_comments_from_subreddits(self):
        '''Scrape comments from all subreddits'''
        # print('scraping comments from subreddits...')

        size = 0
        for path, dirs, files in os.walk('./data'):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)

        print("Folder size: " + str(size))
        print("Folder size in MB: " + str(size / 1000000))
        data_size = math.ceil(size / 1000000)

        if data_size > 250:
            print(Fore.RED + "Scraped enough data, moving on...")
            return

        with open('lists/subreddits.txt', 'r') as f:
            subreddits = f.read().splitlines()
        f.close()

        for subreddit in subreddits:
            self._scrape_comments_from_subreddit(subreddit)



    def _learn_from_subreddit(self, name):
        '''Learn from a subreddit'''
        print(Fore.GREEN + 'learning from subreddit: ' + name)

        path_to_file = './data/' + name + '.txt'
        with open(path_to_file, 'r') as f:
            text = f.read()
            
        text_model = markovify.Text(text)
        f.close()
        
        return text_model
    
    
    def comment_on_post(self, text_model, name):
        '''Comment on a post'''
        print(Fore.GREEN + 'commenting on post...')

        subreddit = self.r.subreddit(name)
        
        val = random.choice([1, 2])

        # convert list generator to a list then shuffle it
        submissions = list(subreddit.hot(limit=30))
        random.shuffle(submissions)


        if val == 1:
            # Comment on post
            for submission in submissions:
                submission.reply(text_model.make_short_sentence(100))
                break
        elif val == 2:
            # Comment on comment (if any)
            for submission in submissions:
                submission.comments.replace_more(limit=0)
                all_comments = submission.comments.list()
                if len(all_comments) > 0:
                    for comment in all_comments:
                        if comment.author != self.r.user.me():
                            comment.reply(text_model.make_short_sentence(100))
                            break

                break

    def _delete_bad_comments(self):
        '''Deleting comments with low scores'''
        print(Fore.RED + 'deleting bad comments...')

        for comment in self.r.user.me().comments.new(limit=100):
            if comment.score < 1:
                comment.delete()


    def _detect_shadow_banned(self):
        '''Detecting if I'm shadow banned'''
        print(Fore.RED + 'detecting if Im shadow banned...')

        response = requests.get(f"https://www.reddit.com/user/{self.username}/about.json",
                                headers={'User-agent': self.username}).json()
        if "error" in response:
            if response["error"] == 404:
                print(Fore.RED + "You're shadow banned!")
                sys.exit()
            else:
                print("189 ", response)
        else:
            print(Fore.GREEN + "You're not shadow banned!")


    def _generate_relevant_comment(self, text_model, parent):
        # TODO: implement this method
        '''Generate a relevant comment'''
        print(Fore.GREEN + 'generating relevant comment...')


        blob = TextBlob(parent)
        print(blob.noun_phrases)

        # taken from https://stackoverflow.com/questions/33587667/extracting-all-nouns-from-a-text-file-using-nltk
        # print("173 ", [n for n,t in blob.tags if t == 'NN'])

        while True:
            comment = text_model.make_short_sentence(100)

            for word in blob.noun_phrases:
                if word.lower() in comment.split(' '):
                    return comment


    def run(self, comment_count):
        '''Run the bot'''
        print(Fore.BLUE + 'running...')

        self._detect_shadow_banned()

        # scrape comments from all subreddits
        self.scrape_comments_from_subreddits()

        name = self._get_random_subreddit()
        text_model = self._learn_from_subreddit(name)

        for i in range(comment_count):
            self.comment_on_post(text_model, name)
            time.sleep(10)

        self._delete_bad_comments()



    def probability_based_run(self):
        '''Run the bot and do actions based on probabilities'''
        print(Fore.BLUE + 'running...')

        self._detect_shadow_banned()

        while True:
            random.seed(None)
            val = random.random()
            print(Fore.BLUE + "dice roll: ", val)

            if (val < 0.02):
                self.scrape_comments_from_subreddits()
            elif (val > 0.02 and val < 0.04):
                name = self._get_random_subreddit()
                text_model = self._learn_from_subreddit(name)
                self.comment_on_post(text_model, name)
            elif (val > 0.04 and val < 0.06):
                self._detect_shadow_banned()

            self._delete_bad_comments()

            print(Fore.BLUE + 'sleeping...')
            time.sleep(60)





if __name__ == '__main__':
    load_dotenv()

    secret = os.environ['secret']
    client_id = os.environ['client_id']
    user_agent = os.environ['user_agent']
    username = os.environ['username']
    password = os.environ['password']

    obj1 = Bot(username, password, client_id, secret, user_agent)

    # #1
    # schedule.every(2).minutes.do(obj1.run, comment_count=1)
    # while True:
    #     # Checks whether a scheduled task
    #     # is pending to run or not
    #     schedule.run_pending()
    #     time.sleep(1)

    # #2
    # obj1.run(1)

    # #3
    obj1.probability_based_run()

