import re


def parse_forum():
    pass


class Comments:
    TRACK_EMPLYOEES = True
    SEARCH_IN_CONTENT = False
    SEARCH_FOR_USERNAME = True
    LINK_REGEX = ['http.*?:\/\/.*?guildwars2.com\/[^ \])\s]*']
    MENTION_REGEX = '\+/u/{botname} {1,3}{linkregex}'


class Submissions:
    TRACK_EMPLOYEES = True
    SEARCH_IN_URL = True
    SEARCH_IN_TEXT = False
    SEARCH_FOR_USERNAME = True
    LINK_REGEX = ['http.*?:\/\/.*?guildwars2.com\/[^ \])\s]*']
    MENTION_REGEX = '\+/u/{botname} {1,3}{linkregex}'
    #TASKS = [{'regexlist':['https?://(?P<region>.{2,3}?)\.battle\.net(?P<forum>/forums)'], 'action':parse_forum}]


SIGNATURE = '\n' \
            '\n' \
            '---\n' \
            '^(Beep boop. {message})\n' \
            '\n' \
            '^(I am robot. Please message /u/Xyooz if you ' \
            'have any questions, suggestions or concerns.) ' \
            '[^Source ^Code](https://github.com/networkjanitor/polarbytebot)'


#SEARCH_FLAIR_CSS_CLASS = 'blizz'
#TRACKING_SUBREDDIT = 'Blizzwatch'

# haha
FUNNY_MESSAGES = ['']

if __name__ == '__main__':
    url = ''
    exit(0)
    for task in Submissions.TASKS:
        for regex in task['regexlist']:
            if not re.match(regex, url):
                task['action'](url)