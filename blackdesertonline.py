import re
import requests


def process_comment(comments):
    submitArray = []
    for cm in comments:
        if(False): #disabled search in comments
            if re.search('http.*?://.*?blackdesertonline.com/', cm.body) is not None:
                all_links = re.findall('http.*?://.*?blackdesertonline.com/[^ \])\s]*', cm.body)
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
        if(False):  # disabled search in selftext
            if re.search('http.*?://.*?blackdesertonline.com/', sm.selftext) != None:
                all_links = re.findall('http.*?://.*?blackdesertonline.com/[^ \])\s]*', sm.selftext)
                for link in all_links:
                    if link != '':
                        submit = {}
                        submit['thing_id'] = sm.name
                        submit['submitted'] = False
                        submit['origin'], submit['content'] = locate_origin(link)
                        submit['type'] = 'comment'
                        submitArray.append(submit)
        if(True):   # enabled search in url
            if re.search('http.*?://.*?blackdesertonline.com/', sm.url) != None:
                all_links = re.findall('http.*?://.*?blackdesertonline.com/[^ \])]*', sm.url)
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
    try:
        forum_re = re.search('https?://forum\.blackdesertonline.com/index.php\?', url)
        blog_re = re.search('https?://blackdesertonline.com/', url)
        if forum_re is not None:
            return ('forum', forum_parse(url))
        elif blog_re is not None:
            return ('blog', blog_parse(url))
        else:
            return ('unknown', '')
    except Exception as e:
        errormsg = 'error::blackdesertonline::locate_origin:{0} :on: {1}'.format(e, url)
        print(errormsg)
        with open('BDOurlerror', 'a') as f:
            f.write(errormsg)
        return ('error: {0}'.format(url), '')


def forum_parse(url):
    pass


def blog_parse(url):
    pass


def forum_id(url):
    urlInformation = re.search('https?:\/\/forum\.blackdesertonline.com\/index.php\?(?P<topic>\/topic)(?P<topicid>\/[^-]*)(?P<topictitle>-[^\/#]*)((?P<identifier1>\/[^\/#\s]*)|)((?P<identifier2>(#|\/)[^\/#\s]*)|)', url)
    identifier1 = urlInformation.group('identifier1')
    identifier2 = urlInformation.group('identifier2')
    # http://forum.blackdesertonline.com/index.php?/topic/topicid-topictitle/
    if (identifier1 == '/' or identifier1 is None) and identifier2 is None:
        return forum_getFirstId(url)
    # http://forum.blackdesertonline.com/index.php?/topic/topicid-topictitle#comment-1234567
    # http://forum.blackdesertonline.com/index.php?/topic/topicid-topictitle/#comment-1234567
    elif (identifier1 is None or identifier1 == '/') and identifier2[:9] == '#comment-':
        return identifier2[9:]
    else:
        return forum_getFirstId(url)


def forum_getFirstId(url):
    req = requests_get(url)
    id = re.search("<a id='comment-[0123456789]*'></a>", req.text)
    if id is not None:
        id = id.group(0)
        id = id[15:len(id) - 6]
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