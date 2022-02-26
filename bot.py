import os

import time
import random
import schedule

from os.path import exists

import praw
import markovify
from colorama import Fore, Back, Style


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
        # TODO: implement this


    def run(self, comment_count):
        '''Run the bot'''
        print(Fore.BLUE + 'running...')

        # TODO: do actions based on probabilities

        # scrape comments from all subreddits
        obj1.scrape_comments_from_subreddits()

        name = obj1._get_random_subreddit()
        text_model = obj1._learn_from_subreddit(name)

        for i in range(comment_count):
            obj1.comment_on_post(text_model, name)
            time.sleep(10)

        obj1._delete_bad_comments()



if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    secret = os.environ['secret']
    client = os.environ['client']
    user_agent = os.environ['user_agent']
    username = os.environ['username']
    password = os.environ['password']

    obj1 = Bot(username, password, client, secret, user_agent)

    schedule.every(2).minutes.do(obj1.run, comment_count=1)
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)

    # obj1.run(1)

