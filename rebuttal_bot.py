import os
import praw
import time

REBUTTAL_THRESHOLD = 1000
DETECTION_MISSES = 3
reddit = praw.Reddit('rebuttal-bot')


def print_rebuttal(comment, reply):
    print(
        '!!!!! REBUTTAL !!!!!\n',
        f' Comment: {comment.body} --- Score: {comment.score}\n',
        f' Reply: {reply.body} --- Score: {reply.score}\n',
        f' {comment.fullname} --- {reply.fullname}'
    )


def print_rebuttal_tree(rebuttal_tree):
    for submission, comments in rebuttal_tree.items():
        if any(comments.values()):
            print('-' * 40, '\n', f"Title: {submission.title}")
        for comment, replies in comments.items():
            for reply in replies:
                print_rebuttal(comment, reply)
                

def detect_rebuttal(comment):
    rebuttals = []
    replies = comment.replies
    for reply in replies:
        if reply.score > comment.score + REBUTTAL_THRESHOLD:
            print_rebuttal(comment, reply)
            rebuttals.append(reply)
        else:
            break
    return rebuttals

def process_submissions(submissions):
    rebuttal_tree = {}
    for i, submission in enumerate(submissions):
        start = time.time()
        detection_misses = 0
        print('-' * 40, '\n', f"{i}: Title: {submission.title}")
        comments = submission.comments
        more_comments_start = time.time()
        comments.replace_more(limit=500)
        more_comments_end = time.time()
        rebuttal_tree[submission] = {}
        for comment in comments:
            # print(f'Comment Type: {type(comment)}')
            # print(f'Comment Score: {comment.score}')
            if comment.score_hidden or comment.score < REBUTTAL_THRESHOLD:
                detection_misses += 1
            if detection_misses > DETECTION_MISSES:
                break
            results = detect_rebuttal(comment)
            rebuttal_tree[submission][comment] = results
        end = time.time()
        print(f'Elapsed: {end - start} -- More Comments: {more_comments_end - more_comments_start}')
    return rebuttal_tree



def main(reddit=reddit):
    r_all = reddit.subreddit('all')
    # process_submissions(r_all.hot(limit=10))
    tree = process_submissions(r_all.top(time_filter='day', limit=500))
    print_rebuttal_tree(tree)

if __name__ == '__main__':
    main()
