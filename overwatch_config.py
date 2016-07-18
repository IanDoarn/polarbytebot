class Comments:
    TRACK_EMPLYOEES = True
    SEARCH_IN_CONTENT = False
    LINK_REGEX = 'https?://playoverwatch\.com/[^ \])\s]*'  # FYI: search for playoverwatch.com and ???.battle.net/forum


class Submissions:
    TRACK_EMPLOYEES = True
    SEARCH_IN_URL = True
    SEARCH_IN_TEXT = False
    LINK_REGEX = 'https?://.*?battle\.net/[^ \])\s]*'


SIGNATURE = '\n' \
            '\n' \
            '---\n' \
            '^(Beep boop. {message})\n' \
            '\n' \
            '^(I am robot. My task in this subreddit is to transcribe the content of submitted forumposts from ' \
            'battle.net. I also link responses of Blizzard employees to /r/Blizzwatch. Please message /u/Xyooz if you ' \
            'have any questions, suggestions or concerns.) ' \
            '[^Source ^Code](https://github.com/networkjanitor/polarbytebot)'

SEARCH_FLAIR_CSS_CLASS = 'blizz'
TRACKING_SUBREDDIT = 'Blizzwatch'

# haha
FUNNY_MESSAGES = ['',
                  '']
