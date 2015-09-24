import urllib.request
from models import session, anet_member

SUBREDDIT_CSS_URL='https://b.thumbs.redditmedia.com/G3o22FYu1eyCBOz3v9P60aijMXkd02e1CYNAGjCXf-s.css'
FLAIR_IMAGE_URL='//b.thumbs.redditmedia.com/Fq7hb9d2IPCARg62gk3qRHkWy95sHvNvgUt3d386hOw.png'

css = urllib.request.urlopen(SUBREDDIT_CSS_URL).read().decode('utf-8')
int_flairimg = css.find(FLAIR_IMAGE_URL)
int_start_anet_section = css.rfind('}',0,int_flairimg)

t_str_names = css[int_start_anet_section+1:int_flairimg-14].split(',')
session.query(anet_member).delete()

for part in t_str_names:
    row = anet_member()
    row.username = part.replace('"]:before,','').replace('"]:before','').replace('.author[href$="/','')
    session.add(row)
session.commit()
