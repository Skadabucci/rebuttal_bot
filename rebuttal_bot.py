import json
import os
import praw
import time
import traceback

SUBMISSON_LIMIT = 1000
DETECTION_MISSES = 3


def reply_to_comment(comment):
    text = 'Nice rebuttal! [More information](https://github.com/Boomerkuwanger/rebuttal_bot/blob/master/README.md)'
    comment.reply(text)


def reply_to_rebuttals(rebuttal_tree):
    print('-' * 12, 'Replying to rebuttals', '-' * 12)
    for submission, comments in rebuttal_tree.items():            
        for comment, replies in comments.items():
            for reply in replies:
                replied = False
                while not replied:
                    try:
                        reply_to_comment(reply)
                        print(f'Replied to rebuttal from comment: https://reddit.com{comment.permalink}')
                        replied = True
                        time.sleep(60 * 5)
                    except praw.exceptions.APIException as e:
                        if 'RATELIMIT' in str(e):
                            time.sleep(60 * 1)
                        else:
                            traceback.print_exc()
                            print(f'Failed to reply to https://reddit.com{comment.permalink}')
                            break


def scalar_function(x):
    if x < 100:
        return 500
    elif x < 1000:
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
        else:
            break
    return rebuttals


def process_submissions(submissions):
    rebuttal_tree = {}
    for i, submission in enumerate(submissions):
        print('-' * 40, '\n', f'{i}:: ID: {submission.id} Title: {submission.title}')
        submission.comment_sort = 'top'
        rebuttal_tree[submission] = {}
        start = time.time()
        comments = submission.comments

        comments.replace_more(limit=0)
        for comment in comments:
            results = detect_rebuttal(comment)
            rebuttal_tree[submission][comment] = results

        print('-' * 12, f'Elapsed: {time.time() - start}', '-' * 12)
    return rebuttal_tree


def main():
    reddit = praw.Reddit('rebuttal-bot')
    r_all = reddit.subreddit('all')
    tree = process_submissions(r_all.top(time_filter='day', limit=SUBMISSON_LIMIT))
    submissions = [submission.permalink for submission in tree.keys()]
    permalink_tree = make_permalink_tree(tree)
    run_time = time.strftime("%Y%m%d-%H%M%S")

    with open(f'rebuttals/rebuttal_{run_time}.json', 'w+') as f:
        f.write(json.dumps(permalink_tree))

    with open(f'submissions/submission_{run_time}.json', 'w+') as f:
        f.write(json.dumps(submissions))

    reply_to_rebuttals(tree)

if __name__ == '__main__':
    main()
