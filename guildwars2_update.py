import praw, re
from models import session, anet_member, cfg_file

FLAIR_IMAGE_URL='%%arenanet-half6%%'

css = praw.Reddit(cfg_file['reddit']['user_agent']).get_subreddit('Guildwars2')\
        .get_stylesheet()['stylesheet']
int_flairimg = css.find(FLAIR_IMAGE_URL)
int_start_anet_section = css.rfind('ArenaNet Staff', 0, int_flairimg)

t_str_names = re.findall('.author\[href\$="\/[^"]*"\]:before',\
                    css[int_start_anet_section:int_flairimg])
session.query(anet_member).delete()

for line in t_str_names:
    if line != '':
        row = anet_member()
        row.username = line.replace('"]:before','')\
                            .replace('.author[href$="/','')
        session.add(row)
session.commit()
