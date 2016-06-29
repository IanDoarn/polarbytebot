import html.parser
import re
import requests
import urllib.parse
import datetime
import overwatch_html2markdown

def process_comment(comments):
    submitArray = []
    for cm in comments:
        if cm.author_flair_css_class == 'blizz':
            # submission to devtracker subreddit
            submit = {}
            submit['type'] = 'link'
            title = cm.link_title
            if len(title) + len(cm.author.name) + len(' []') > 300:
                title = '{0}... [{1}]'.format(title[:300 - len(cm.author.name) - len(' []') - len('...')], cm.author.name)
            else:
                title = '{0} [{1}]'.format(title, cm.author.name)
            submit['title'] = title
            submit['subreddit'] = 'blizzwatch'
            submit['submitted'] = False
            submit['content'] = cm.permalink + '?context=1000'
            submitArray.append(submit)
            # anet-comment-pool
            #submit = {}
            #submit['thread_id'] = cm.link_id
            #submit['type'] = 'edit'
            #submit['submitted'] = False
            #submit['content'] = '\n\n* [Comment by {0}]({1}?context=1000) - {2}'.format(cm.author.name, cm.permalink, datetime.datetime.fromtimestamp(cm.created_utc,datetime.timezone.utc).isoformat(' '))
            #submitArray.append(submit)

        if False: #disabled search in comments
            if re.search('http.*?:\/\/.*?guildwars2.com\/', cm.body) != None: # FYI: search for playoverwatch.com and ???.battle.net/forum
                all_links = re.findall('http.*?:\/\/.*?guildwars2.com\/[^ \])\s]*', cm.body)
                for link in all_links:
                    if link != '':
                        submit = {}
                        submit['thing_id'] = cm.name
                        submit['submitted'] = False
                        submit['origin'], submit['content'] = locate_origin(link)
                        submit['type'] = 'comment'
                        submitArray.append(submit)
    return submitArray


def process_submission(submissions):
    submitArray = []
    for sm in submissions:
        if sm.author_flair_css_class == 'blizz':
            # submission to devtracker subreddit
            submit = {}
            submit['type'] = 'link'
            title = sm.title
            if len(title) + len(sm.author.name) + len(' []') > 300:
                title = '{0}... [{1}]'.format(title[:300 - len(sm.author.name) - len(' []') - len('...')], sm.author.name)
            else:
                title = '{0} [{1}]'.format(title, sm.author.name)
            submit['title'] = title
            submit['submitted'] = False
            submit['subreddit'] = 'blizzwatch'
            submit['content'] = sm.permalink + '?context=1000'
            submitArray.append(submit)

        if(False):  # disabled search in selftext
            if re.search('http.*?:\/\/.*?guildwars2.com\/', sm.selftext) != None:
                all_links = re.findall('http.*?:\/\/.*?guildwars2.com\/[^ \])\s]*', sm.selftext)
                for link in all_links:
                    if link != '':
                        submit = {}
                        submit['thing_id'] = sm.name
                        submit['submitted'] = False
                        submit['origin'], submit['content'] = locate_origin(link)
                        submit['type'] = 'comment'
                        submitArray.append(submit)
        if(True):   # enabled search in url
            if re.search('http.*?:\/\/.*?battle.net\/', sm.url) != None:
                all_links = re.findall('http.*?:\/\/.*?battle.net\/[^ \])]*', sm.url)
                for link in all_links:
                    if link != '':
                        submit = {}
                        submit['thing_id'] = sm.name
                        submit['submitted'] = False
                        submit['origin'], submit['content'] = locate_origin(link)
                        submit['type'] = 'comment'
                        submitArray.append(submit)
    return submitArray


def locate_origin(url):
    #try:
        forum_re = re.search('https?://(?P<region>.{2,3}?)\.battle.net(?P<forum>\/forums)', url)
        if forum_re is not None:
            return ('forum', forum_parse(url))
        else:
            return ('unknown', '')
    #except Exception as e:
    #    errormsg = 'error::guildwars2::locate_origin:{0} :on: {1}'.format(e, url)
    #    print(e.args)
    #    with open('gw2urlerror', 'a') as f:
    #        f.write(errormsg)
    #    return ('error: {0}'.format(url), '')


def forum_parse(url):
    post_dict = {}
    post_dict['id'] = forum_id(url)
    post_dict['req'] = requests_get(url)
    post_dict['message'] = content_selection(post_dict['req'].text, ' id="' + post_dict['id'], '<div', '</div>')
    post_dict['datetime'] = forum_datetime(post_dict['message'])
    t_name = forum_name(post_dict['message'])
    post_dict['name'] = t_name[0]
    post_dict['isBlizzard'] = t_name[1]
    post_dict['content'] = content_selection(post_dict['message'], '<div class="TopicPost-bodyContent" data-topic-post-body-content="true"', '<div', '</div>')[1:] + '</div>'
    markdown_header = post_dict['isBlizzard'] + ' [' + post_dict['name'] + ' posted on ' + post_dict['datetime'] + '](' + url + '):\n'
    markdown_content = html_to_markdown(post_dict['content'], parse_host_from_url(url))
    return markdown_header + markdown_content


def forum_id(url):
    urlInformation = re.search('https?://(?P<region>.{2,3}?)\.battle.net(?P<forum>\/forums)(?P<language>\/[^\/]*)(?P<subforum>\/[^\/]*)(?P<title>\/[^\/#]*)((?P<identifier1>\/[^\/#\s?]*)|)((?P<identifier2>(#?|\/)[^\/#\s]*)|)((?P<identifier3>(#|\/)[^\/#\s]*)|)', url)
    identifier1 = urlInformation.group('identifier1')
    identifier2 = urlInformation.group('identifier2')
    identifier3 = urlInformation.group('identifier3')
    # http://us.battle.net/forums/en/overwatch/topic/123456789
    # http://us.battle.net/forums/en/overwatch/topic/123456789/
    if identifier1[1:].isdigit and (identifier2 == '/' or identifier2 is None) and identifier3 is None:
        return 'post-1'
    # http://us.battle.net/forums/en/overwatch/topic/20745604460#post-4
    elif identifier1[1:].isdigit and identifier2[:6] == '#post-' and identifier3 is None:
        return identifier2[1:]
    # http://us.battle.net/forums/en/overwatch/topic/20745604460?page=3
    elif identifier1[1:].isdigit and identifier2[:6] == '?page=' and identifier3 is None:
        return 'post-' + str((int(identifier2[6:])-1)*20+1)
    # http://us.battle.net/forums/en/overwatch/topic/20745604460?page=3#post-41
    elif identifier1[1:].isdigit and identifier2[:6] == '?page=' and identifier3[:6] == '#post-':
        return identifier3[1:]

    else:
        return forum_getFirstId(url)


def forum_getFirstId(url):
    req = requests_get(url)
    id = re.search(' id="post-[0123456789]*"', req.text)
    if id is not None:
        id = id.group(0)
        id = id[5:-1]
    else:
        id = '0'
    return id


def requests_get(url):
    counter = 0
    while (True):
        try:
            req = requests.get(url)
        except:
            pass
        else:
            return req
        finally:
            counter += 1
            if counter > 100:
                return


def content_selection(content, start_str, nst, net):
    content_start = content.find(start_str)
    if content_start != -1:
        content = content[content_start + len(start_str):]
        level = 1
        pointer = 0
        ned = 0
        while (True):
            ned_old = ned
            nsd = content.find(nst, pointer)
            ned = content.find(net, pointer)
            if level == 0:
                break
            elif nsd > ned != -1:
                pointer = ned + 1
                level -= 1
            elif nsd < ned and nsd != -1:
                pointer = nsd + 1
                level += 1
            elif nsd < ned and nsd == -1:
                pointer = ned + 1
                level -= 1
        return content[:ned_old]
    else:
        return ''


def forum_name(content):
    posted_by_class = re.search('<aside class="TopicPost-author">.*?</aside>', content, re.DOTALL).group(0)
    posted_by_name = re.search('<span class="Author-name">(?P<name>.*?)</span>', posted_by_class, re.DOTALL).group('name')
    #posted_by_name = posted_by_name.replace('-', ' ', posted_by_name.count('-') - 1).replace('-', '.')
    return [posted_by_name.strip(), forum_blizz(posted_by_class)]


def forum_blizz(posted_by_class):
    posted_by_blizz = re.findall('class="Author[^"]*', posted_by_class)
    for found in posted_by_blizz:
        if "blizzard" in found:
            return '[BLIZZARD]'
    return ''


def forum_datetime(content):
    #<a class="TopicPost-timestamp" .*? data-tooltip-content="06/23/2016 05:35 AM">.*?</a>
    posted_datetime_class = re.search('<a class="TopicPost-timestamp".*?data-tooltip-content=".*?">\s*.*?\s*</a>', content).group(0)
    return re.search('data-tooltip-content="[^"]*', posted_datetime_class).group(0)[len("data-tooltip-content=\""):]


def parse_host_from_url(url):
    return re.search('\/\/.*?battle.net', url).group(0)[2:]


def html_to_markdown(content, host):
    with open('debug/out', 'w') as f:
        f.write(content)
    parser = overwatch_html2markdown.Htmlparser()
    parser.convert_charrefs = True
    parser.host = 'https://' + host
    content = content.replace('\n', '\n>')
    parser.feed(content)
    return parser.result

if __name__ == '__main__':
    #locate_origin('http://us.battle.net/forums/en/overwatch/topic/20745604460?page=3#post-42')
    locate_origin('http://us.battle.net/forums/en/overwatch/topic/20745665208#post-3')