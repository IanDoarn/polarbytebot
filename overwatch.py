import html.parser
import re
import requests
import urllib.parse
import datetime
import overwatch_html2markdown


class p_href(html.parser.HTMLParser):
    _href = ''
    _text = ''
    _type = ''

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == 'href':
                t_href = value
                if t_href[:12] == '/external?l=':
                    t_href = urllib.parse.unquote_plus(t_href[12:])
                    _type = 'external'
                elif t_href[:2] == '//':
                    t_href = 'https:' + t_href
                    _type = 'external w/o protocol'
                else:
                    _type = 'relative'
                self._href = t_href

    def handle_data(self, data):
        self._text += data

    def handle_entityref(self, name):
        self._text += '&' + name + ';'


class p_img(html.parser.HTMLParser):
    _src = ''
    _type = ''

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == 'src':
                t_src = value
                if t_src[:1] == '/':
                    self._type = 'relative'
                else:
                    self._type = 'external'
                self._src = value


class p_attachments(html.parser.HTMLParser):
    _a = []
    _tag = []

    def __init__(self):
        self._a = []

    def handle_starttag(self, tag, attrs):
        self._tag.append(tag)
        if tag == 'a':
            for key, value in attrs:
                if key == 'href':
                    self._a.append(value)

    def handle_endtag(self, tag):
        self._tag.pop()


class p_screenshots(html.parser.HTMLParser):
    _src = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for key, value in attrs:
                if key == 'href':
                    if value[:2] == '//':
                        self._src = 'https:' + value
                    else:
                        self._src = value


class p_iframe(html.parser.HTMLParser):
    _src = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'iframe':
            for key, value in attrs:
                if key == 'src':
                    if value[:2] == '//':
                        self._src = 'https:' + value
                    else:
                        self._src = value


def process_comment(comments, array_anet_names):
    submitArray = []
    for cm in comments:
        if cm.author.name in array_anet_names:
            # submission to devtracker subreddit
            submit = {}
            submit['type'] = 'link'
            title = cm.link_title
            if len(title) + len(cm.author.name) + len(' []') > 300:
                title = '{0}... [{1}]'.format(title[:300 - len(cm.author.name) - len(' []') - len('...')], cm.author.name)
            else:
                title = '{0} [{1}]'.format(title, cm.author.name)
            submit['title'] = title
            submit['subreddit'] = 'gw2devtrack'
            submit['submitted'] = False
            submit['content'] = cm.permalink + '?context=1000'
            submitArray.append(submit)
            # submission to alternative devtracker subreddit
            submit = {}
            submit['type'] = 'self'
            title = cm.link_title
            if len(title) + len(cm.author.name) + len(' []') > 300:
                title = '{0}... [{1}]'.format(title[:300 - len(cm.author.name) - len(' []') - len('...')], cm.author.name)
            else:
                title = '{0} [{1}]'.format(title, cm.author.name)
            submit['title'] = title
            submit['subreddit'] = 'gw2devtrackalt'
            submit['submitted'] = False
            submit['content'] = '{0}\n\n{1}?context=1000'.format(cm.body, cm.permalink)
            submitArray.append(submit)
            # anet-comment-pool
            submit = {}
            submit['thread_id'] = cm.link_id
            submit['type'] = 'edit'
            submit['submitted'] = False
            submit['content'] = '\n\n* [Comment by {0}]({1}?context=1000) - {2}'.format(cm.author.name, cm.permalink, datetime.datetime.fromtimestamp(cm.created_utc,datetime.timezone.utc).isoformat(' '))
            submitArray.append(submit)

        if(False): #disabled search in comments
            if re.search('http.*?:\/\/.*?guildwars2.com\/', cm.body) != None:
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


def process_submission(submissions, array_anet_names):
    submitArray = []
    for sm in submissions:
        if sm.author.name in array_anet_names:
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
            submit['subreddit'] = 'gw2devtrack'
            submit['content'] = sm.permalink + '?context=1000'
            submitArray.append(submit)
            # submission to alternative devtracker subreddit
            submit = {}
            submit['type'] = 'self'
            title = sm.title
            if len(title) + len(sm.author.name) + len(' []') > 300:
                title = '{0}... [{1}]'.format(title[:300 - len(sm.author.name) - len(' []') - len('...')], sm.author.name)
            else:
                title = '{0} [{1}]'.format(title, sm.author.name)
            submit['title'] = title
            submit['submitted'] = False
            submit['subreddit'] = 'gw2devtrackalt'
            submit['content'] = '{0}\n\n{1}?context=1000'.format(sm.selftext, sm.permalink)
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
            if re.search('http.*?:\/\/.*?guildwars2.com\/', sm.url) != None:
                all_links = re.findall('http.*?:\/\/.*?guildwars2.com\/[^ \])]*', sm.url)
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
        forum_re = re.search('http.*?:\/\/forum-..\.guildwars2.com\/forum\/', url)
        blog_re = re.search('http.*?:\/\/.{0,4}guildwars2.com\/.*?\/', url)
        if forum_re is not None:
            return ('forum', forum_parse(url))
        elif blog_re is not None:
            return ('blog', blog_parse(url))
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
    post_dict['message'] = content_selection(post_dict['req'].text, "' id='post" + post_dict['id'], '<div', '</div>')
    post_dict['datetime'] = forum_datetime(post_dict['message'])
    t_name = forum_name(post_dict['message'])
    post_dict['name'] = t_name[0]
    post_dict['isArenanet'] = t_name[1]
    post_dict['content'] = content_selection(post_dict['message'], '<div class="message-content">', '<div', '</div>')
    markdown_header = post_dict['isArenanet'] + ' [' + post_dict['name'] + ' posted on ' + post_dict['datetime'] + '](' + url + '):\n'
    markdown_content = html_to_markdown(post_dict['content'], parse_host_from_url(url))
    post_dict['attach_content'] = content_selection(post_dict['message'], '<div class="attachment-content">', '<div', '</div>')
    if post_dict['attach_content'] == '':
        return markdown_header + markdown_content
    else:
        return markdown_header + markdown_content + forum_attachments(post_dict['attach_content'])


def blog_parse(url):
    post_dict = {}
    post_dict['req'] = requests_get(url)
    post_dict['article'] = content_selection(post_dict['req'].text, '<div class="article">', '<div', '</div>')
    post_dict['attribution'] = content_selection(post_dict['article'], '<p class="blog-attribution">', '<p', '</p>')
    post_dict['name'] = blog_name(post_dict['attribution'])
    post_dict['datetime'] = blog_datetime(post_dict['attribution'])
    post_dict['text'] = content_selection(post_dict['article'], '<div class="text">', '<div', '</div>')
    markdown_header = '[BLOG] [' + post_dict['name'] + ' posted on ' + post_dict['datetime'] + '](' + url + '):\n'
    markdown_content = html_to_markdown(post_dict['text'], parse_host_from_url(url))
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
        return identifier2[5:]

    else:
        return forum_getFirstId(url)


def forum_getFirstId(url):
    req = requests_get(url)
    id = re.search("' id='post[0123456789]*'>", req.text)
    if id is not None:
        id = id.group(0)
        id = id[10:len(id) - 2]
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
    posted_by_class = re.search('<p>Posted by: <a class="member.*?" href="\/members\/.*?-[0123456789]{4}">.*?<\/a><\/p>', content).group(0)
    posted_by_name = re.search('href="\/members\/[^"]*', posted_by_class).group(0)[15:]
    posted_by_name = posted_by_name.replace('-', ' ', posted_by_name.count('-') - 1).replace('-', '.')
    return [posted_by_name, forum_anet(posted_by_class)]


def forum_anet(posted_by_class):
    posted_by_anet = re.search('class="member [^"]*', posted_by_class).group(0)
    if "arenanet" in posted_by_anet:
        return '[ARENA NET]'
    else:
        return ''


def forum_datetime(content):
    posted_datetime_class = re.search('<p><time class="changeabletime" datetime=".*?">.*?<\/time><\/p>', content).group(0)
    return re.search('datetime="[^"]*', posted_datetime_class).group(0)[10:].replace('T', ' ').replace('Z', ' UTC')


def forum_attachments(attach_content):
    parser = p_attachments()
    parser.feed(attach_content)
    markdown_attachments = '\n\n>Attachments:\n'
    for item in parser._a:
        markdown_attachments += '\n>* ' + item
    return markdown_attachments


def blog_name(content):
    c_split = content.split()
    name = ''
    for i in range(1, len(c_split) - 4):
        name += c_split[i] + ' '
    return name.strip()


def blog_datetime(content):
    c_split = content.split()
    datetime = ''
    for i in range(len(c_split) - 3, len(c_split)):
        datetime += c_split[i] + ' '
    return datetime.strip()


def parse_host_from_url(url):
    return re.search('\/\/.*?guildwars2.com', url).group(0)[2:]


def html_to_markdown(content, host):
    with open('debug/out', 'w') as f:
        f.write(content)
    parser = overwatch_html2markdown.Htmlparser()
    parser.convert_charrefs = True
    parser.host = 'https://' + host
    content = content.replace('\n', '\n>')
    parser.feed(content)
    print(parser.result)
    return parser.result


def tag_img(content, host):
    re_imgs = re.findall('<img.*?src="[^"]*"[^>]*>', content)
    for re_img in re_imgs:
        if re_img != '':
            parser = p_img()
            parser.feed(re_img)
            if parser._type == 'relative':
                content = content.replace(re_img, ' https://' + host + parser._src)
            else:
                content = content.replace(re_img, ' ' + parser._src)
    return content


def tag_href(content, host):
    re_links = re.findall('<a.*?href="[^"]*".*?>.*?<\/a>', content)
    for re_link in re_links:
        if re_link != '':
            parser = p_href()
            parser.feed(re_link)
            if parser._text == '':
                parser._text = parser._href
            if parser._type == 'relative':
                content = content.replace(re_link, '[' + parser._text + '](https://' + host + parser._href + ')')
            else:
                content = content.replace(re_link, '[' + parser._text + '](' + parser._href + ')')
    return content


def tag_quote(content, host):
    level = 0
    pointer = 0
    quote_list = []
    dict = {}
    while (True):
        nsb = content.find('<blockquote>', pointer)
        neb = content.find('</blockquote>', pointer)

        if nsb == -1 and neb == -1:
            break

        if nsb < neb and nsb != -1:
            pointer = nsb + 1
            try:
                dict[level].append(nsb)
            except KeyError:
                dict[level] = [nsb]
            level += 1
        elif nsb > neb and neb != -1:
            pointer = neb + 1
            level -= 1
            quote_list.append([dict[level][len(dict[level]) - 1], neb])
        elif nsb < neb and nsb == -1:
            pointer = neb + 1
            level -= 1
            quote_list.append([dict[level][len(dict[level]) - 1], neb])
        else:
            print('something went wrong (nsb found, neb not found)')

    replace_list = []

    for start, end in quote_list:
        message = content[start:end]
        quotey = message[
                 message.find('<div class="quotey">') + len('<div class="quotey">'):message.rfind('</div>') + len('</div>')]
        replace_list.append([message, quotey])
    replace_list.reverse()

    for message, quotey in replace_list:
        quotey = quotey.replace('\n', '\n>')
        quotey = quotey.replace('\n></div>', '\n')
        oc = content
        while oc == content:
            content = content.replace(message + '</blockquote>', '>' + quotey)
            message = message.replace('\n', '\n>').replace('\n></div>', '\n')
    return content


def tag_spoiler(content, host):
    return content


def tag_iframe(content, host):
    re_ifrs = re.findall('<iframe.*?src="[^"]*".*?>.*?<\/iframe>', content)
    for re_ifr in re_ifrs:
        if re_ifr != '':
            parser = p_iframe()
            parser.feed(re_ifr)
            content = content.replace(re_ifr, parser._src)
    return content


def tag_screenshot(content, host):
    re_sss = re.findall('<p class="screenshot">.*?<\/p>', content)
    for re_ss in re_sss:
        if re_ss != '':
            parser = p_screenshots()
            parser.feed(re_ss)
            content = content.replace(re_ss, parser._src + '\n')
    return content


def tag_object(content):
    re_objFlashs = re.findall('<object type="application\/x-shockwave-flash".*?>.*?<\/object>', content)
    for re_objFlash in re_objFlashs:
        if re_objFlash != '':
            content = content.replace(re_objFlash, '')
    return content


def tag_bold(content):
    return content.replace('<strong>', '**').replace('</strong>', '**') \
        .replace('<b>', '**').replace('</b>', '**')


def tag_italic(content):
    return content.replace('<em>', '*').replace('</em>', '*')


def tag_list(content):
    return content.replace('<li>', '* ').replace('</li>', '\n').replace('<ul>', "").replace('</ul>', '').replace('<ol>', '').replace('</ol>', '')


def tag_paragraph(content):
    return content.replace('<p>', "").replace('</p>', '\n')


def tag_superscript(content):
    return content.replace('<sub>', '^(').replace('</sub>', ')').replace('<sup>', "").replace('</sup>', '')


def tag_strikethrough(content):
    return content.replace('<del>', '~~').replace('</del>', '~~')


def tag_underline(content):
    return content.replace('<ins>', '###### ').replace('</ins>', '')


def tag_breakrow(content):
    return content.replace('<br/>', '\n').replace('<br />', '\n').replace('<br>', '')


def tag_h1(content):
    return content.replace('<h1>', '# ').replace('</h1>', '')


def tag_h2(content):
    return content.replace('<h2>', '## ').replace('</h2>', '')


def tag_h3(content):
    return content.replace('<h3>', '### ').replace('</h3>', '')


def tag_h4(content):
    return content.replace('<h4>', '#### ').replace('</h4>', '')


def tag_h5(content):
    return content.replace('<h5>', '##### ').replace('</h5>', '')


def tag_h6(content):
    return content.replace('<h6>', '###### ').replace('</h6>', '')


def tag_tabs(content):
    return content.replace('\t', '')


def tag_hr(content):
    return content.replace('<hr />', '---')


def tag_other(content):
    return content

if __name__ == '__main__':
    locate_origin('http://us.battle.net/forums/en/overwatch/topic/20745604460?page=3')
    #locate_origin('http://us.battle.net/forums/en/overwatch/topic/20745605151#post-1')