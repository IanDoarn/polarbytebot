import re


def parse_forum():
    pass


class Comments:
    TRACK_EMPLYOEES = True
    SEARCH_IN_CONTENT = False
    LINK_REGEX = 'https?://playoverwatch\.com/[^ \])\s]*'  # FYI: search for playoverwatch.com and ???.battle.net/forum


class Submissions:
    TRACK_EMPLOYEES = True
    SEARCH_IN_URL = True
    SEARCH_IN_TEXT = False
    LINK_REGEX = 'https?://.*?battle\.net/[^ \])\s]*'
    TASKS = [{'regexlist':['https?://(?P<region>.{2,3}?)\.battle\.net(?P<forum>/forums)'], 'action':parse_forum}]


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
FUNNY_MESSAGES = ['Fuck the red team.',
                  'Doo-Woo.',
                  'Beeple.',
                  'Boo Boo Doo De Doo.',
                  'Bweeeeeeeeeee.',
                  'Chirr Chirr Chirr.',
                  'Dun Dun Boop Boop.',
                  'Dweet Dweet Dweet!',
                  'Zwee? ',
                  'Hard work pays off.',
                  'Leave this to an expert.',
                  'Some assembly required.',
                  'Working as intended.',
                  'I hope you learned your lesson.',
                  'Sorry, ^sorry, ^^I\'m ^^sorry, ^^^sorry...',
                  'A-Mei-Zing!',
                  'Chill out!',
                  'You are only human.',
                  'I\'ve got a bullet with your name on it.',
                  'You seem familiar. Ain\'t I killed you before?',
                  'Happens to the best of us.',
                  'I tried being reasonable. Didn\'t take to it.',
                  'You Done?',
                  'I\'ve got you on my radar.',
                  'Leave this to a professional.',
                  'You look like you\'ve seen a ghost.',
                  'I\'m not a robot. I\'m a high-functioning robot.',
                  'If it lives, I can kill it.',
                  'I\'m an army of one.',
                  'What are you lookin\' at?',
                  'Cheers, love! The cavalry\'s here!',
                  'Ever get that feeling of déjà vu?',
                  'The world could always use more heroes.',
                  'Looks like you need a time out.',
                  'I have this under control.',
                  'I do what I must.',
                  'Ooh, shiny.',
                  'Have a nice day!',
                  'Here comes a new challenger!',
                  'Polarbytebot: 1, Bad Guys: 0',
                  'Is this easy mode?',
                  'No hacks required.',
                  'Precision German engineering.',
                  'Are you afraid to fight me?',
                  'Catch Phrase!',
                  'I\'m the ultimate crushing machine.',
                  'This old dog still knows a few tricks.',
                  'Let me show you how it\'s done.',
                  'Got something to say?',
                  'No, I do not want a banana.',
                  'Did someone say peanut butter?',
                  'I\'m not a monkey, I\'m a robot!',
                  'Justice delivered.',
                  'You know nothing.',
                  'I could do this all day.',
                  'Can\'t Stop, Won\'t Stop!',
                  'I\'ll send you my consultation fee.',
                  'I\'m not a miracle worker. Well, not always.',
                  'Everything by design.',
                  'I will put you in your place.',
                  'Welcome to my reality.',
                  'Why do you struggle?',
                  'Death is whimsical today.',
                  'Do I think? Does a submarine swim?',
                  'Free your mind.',
                  'Hello, World!',
                  'I dreamt I was a butterfly.',
                  'I think, therefore I am.',
                  'Life is more than a series of ones and zeroes.',
                  'Peace and blessings be upon you all.']

if __name__ == '__main__':
    url = ''
    for task in Submissions.TASKS:
        for regex in task['regexlist']:
            if not re.match(regex, url):
                task['action'](url)