import json
import os
import praw
import time


REBUTTAL_THRESHOLD = 1000
SUBMISSON_LIMIT = 1000
DETECTION_MISSES = 3


def reply_to_rebuttal():
    return 'Nice rebuttal! [More information](https://github.com/Boomerkuwanger/rebuttal_bot/blob/master/README.md)'


def scalar_function(x):
    if x < 100:
        return 500
    elif x < REBUTTAL_THRESHOLD:
        return x * (32.27/(x ** .397))
    else:
        return x * (4/(x ** .1))


def format_comment(comment):
    return f' Comment ({comment.id}): Score: {comment.score}\n   Permalink: {comment.permalink}\n   Body: {comment.body}\n',


def print_rebuttal(comment, reply):
    print(
        '!!!!! REBUTTAL !!!!!\n',
        format_comment(comment),
        format_comment(reply)
    )


def print_rebuttal_tree(rebuttal_tree):
    for submission, comments in rebuttal_tree.items():
        if any(comments.values()):
            print('-' * 40, '\n', f"Title: {submission.title}")
        for comment, replies in comments.items():
            for reply in replies:
                print_rebuttal(comment, reply)
 

def make_permalink_tree(rebuttal_tree):
    permalink_tree = {}
    for submission, comments in rebuttal_tree.items():
        if not any(comments.values()):
            continue
        comment_tree = {}
        for comment, replies in comments.items():
            if not any(replies):
                continue
            comment_tree[comment.id] = [reply.id for reply in replies]
        permalink_tree[submission.permalink] = comment_tree
    return permalink_tree


def detect_rebuttal(comment):
    rebuttals = []
    replies = comment.replies
    for reply in replies:
        if reply.score >= scalar_function(comment.score):
            print_rebuttal(comment, reply)
            rebuttals.append(reply)
            reply.reply(reply_to_rebuttal())
        else:
            break
    return rebuttals


def process_submissions(submissions):
    rebuttal_tree = {}
    for i, submission in enumerate(submissions):
        submission.comment_sort = 'top'
        start = time.time()
        detection_misses = 0
        print('-' * 40, '\n', f"{i}:: ID: {submission.id} Title: {submission.title}")
        comments = submission.comments
        more_comments_start = time.time()
        comments.replace_more(limit=0)
        more_comments_end = time.time()
        rebuttal_tree[submission] = {}
        for comment in comments:
            # print(f'Comment Score: {comment.score}')
            # if comment.score_hidden or comment.score < REBUTTAL_THRESHOLD:
            #     detection_misses += 1
            # if detection_misses > DETECTION_MISSES:
            #     break
            results = detect_rebuttal(comment)
            rebuttal_tree[submission][comment] = results
        end = time.time()
        print(f'Elapsed: {end - start} -- More Comments: {more_comments_end - more_comments_start}')
    return rebuttal_tree


def main():
    reddit = praw.Reddit('rebuttal-bot')
    r_all = reddit.subreddit('all')
    # process_submissions(r_all.hot(limit=10))
    tree = process_submissions(r_all.top(time_filter='day', limit=SUBMISSON_LIMIT))
    # print_rebuttal_tree(tree)
    submissions = [submission.permalink for submission in tree.keys()]
    permalink_tree = make_permalink_tree(tree)
    run_time = time.strftime("%Y%m%d-%H%M%S")
    if permalink_tree:
        with open(f'rebuttals/rebuttal_{run_time}.json', 'w+') as f:
            f.write(json.dumps(permalink_tree))
    with open(f'submissions/submission_{run_time}.json', 'w+') as f:
        f.write(json.dumps(submissions))


if __name__ == '__main__':
    main()
