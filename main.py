import os
import time
import random
import schedule

from os.path import exists

import praw
import markovify



def bad_words(comment):
    with open('./lists/avoid_words.txt', 'r') as f:
        avoid_words = f.read().splitlines()

    f.close()

    for word in avoid_words:
        if word in comment.body:
            return True
    return False


def find_random_subs():
    with open('lists/subreddits.txt', 'r') as f:
        subreddits = f.read().splitlines()
    f.close()

    return random.choice(subreddits)


def scrape_comments_from_sub(name):
    subreddit = r.subreddit(name)

    print(subreddit.display_name)

    # for submission in subreddit.hot(limit=10):

    path_to_file = './data/' + name + '.txt'
    if not exists(path_to_file):
        f = open(path_to_file, 'x')
        # f.write(subreddit.display_name)

    # Iterate through the top submissions
    for submission in subreddit.hot(limit=10):
        submission.comments.replace_more(limit=0)
        # all_comments = praw.helpers.flatten_tree(submission.comments)

        all_comments = submission.comments.list()

        if len(all_comments) > 0:
            print(len(all_comments))

            # Iterate through all the comments
            for comment in all_comments:

                if bad_words(comment):
                    print("bad comment")
                    continue

                with open(path_to_file, 'a') as f:
                    f.write(comment.body)
                # f = open(path_to_file, 'a')
                # f.write(comment.body)
        else:
            print('no comments')
            continue

    f.close()


def learn_from_sub(name):
    path_to_file = './data/' + name + '.txt'
    with open(path_to_file, 'r') as f:
        text = f.read()
    # f = open(path_to_file, 'r')
    # text = f.read()
    text_model = markovify.Text(text)

    f.close()

    return text_model


# comment on reddit post
def comment_on_post(name, text_model):
    subreddit = r.subreddit(name)

    val = random.choice([1, 2])
    if val == 1:
        # Comment on post
        for submission in subreddit.hot(limit=10):
            submission.reply(text_model.make_sentence())
            break
    elif val == 2:
        # Comment on comment (if any)
        for submission in subreddit.hot(limit=10):
            submission.comments.replace_more(limit=0)
            all_comments = submission.comments.list()
            if len(all_comments) > 0:
                for comment in all_comments:
                    if comment.author != r.user.me():
                        comment.reply(text_model.make_sentence())
                        break

                break


# comments with low scores mean they are not 'human' enough so we delete them
def delete_bad_comments():
    for comment in r.user.me().comments.new(limit=10):
        if comment.score < 1:
            comment.delete()


if __name__ == '__main__':

    secret = os.environ['secret']
    client = os.environ['client']
    user_agent = os.environ['user_agent']
    username = os.environ['username']
    password = os.environ['password']

    r = praw.Reddit(
        client_id=client,
        client_secret=secret,
        user_agent=user_agent,
        username=username,
        password=password,
    )

    # Source: https://stackoverflow.com/a/25251804/9206643
    # Schedule a job to run every minute
    # starttime = time.time()
    # while True:
    #     print("tick")
    #     time.sleep(60.0 - ((time.time() - starttime) % 60.0))
    #
    #     val = random.randrange([0, 100])
    #     if val == 1:
    #         learn_from_sub('python')
    #     elif val == 2:
    #

    name = find_random_subs()

    scrape_comments_from_sub(name)

    text_model = learn_from_sub(name)

    for i in range(100):
        comment_on_post(name, text_model)
        time.sleep(10)

    comment_on_post(name, text_model)

    delete_bad_comments()
