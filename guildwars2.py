import html.parser
import re
import requests, urllib.parse

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
                    _type ='external w/o protocol'
                else:
                    _type = 'relative'
                self._href=t_href
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
    def handle_starttag(self, tag, attrs):
        self._tag.append(tag)
        if tag == 'a':
            for key,value in attrs:
                if key == 'href':
                    self._a.append(value)
    def handle_endtag(self, tag):
        self._tag.pop()
class p_screenshots(html.parser.HTMLParser):
    _src = ''
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for key,value in attrs:
                if key == 'href':
                    if value[:2] == '//':
                        self._src = 'https:' + value
                    else:
                        self._src = value
class p_iframe(html.parser.HTMLParser):
    _src = ''
    def handle_starttag(self, tag, attrs):
        if tag == 'iframe':
            for key,value in attrs:
                if key == 'src':
                    if value[:2] == '//':
                        self._src = 'https:' + value
                    else:
                        self._src = value
def locate_origin(url):
    forum_re = re.search('http.*?:\/\/forum-..\.guildwars2.com\/forum\/', url)
    blog_re = re.search('http.*?:\/\/.{0,4}guildwars2.com\/.*?\/', url)
    if forum_re != None:
        markdown_content = forum_parse(url)
    elif blog_re != None:
        markdown_content = blog_parse(url)
    else:
        print(url)
        raise WrongOrigenException()
    return markdown_content
def forum_parse(url):
    post_dict = {}
    post_dict['id'] = forum_id(url)
    post_dict['req'] = requests.get(url)
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
    post_dict['req'] = requests.get(url)
    post_dict['article'] = content_selection(post_dict['req'].text, '<div class="article">', '<div', '</div>')
    post_dict['attribution'] = content_selection(post_dict['article'], '<p class="blog-attribution">', '<p', '</p>')
    post_dict['name'] = blog_name(post_dict['attribution'])
    post_dict['datetime'] = blog_datetime(post_dict['attribution'])
    post_dict['text'] = content_selection(post_dict['article'], '<div class="text">', '<div', '</div>')
    markdown_header = '[BLOG] [' + post_dict['name'] + ' posted on ' + post_dict['datetime'] + '](' + url + '):\n'
    markdown_content = html_to_markdown(post_dict['text'], parse_host_from_url(url))
    return markdown_header + markdown_content
def forum_id(url):
    id = re.search('#post[0123456789]*$',url)
    if id != None:
        id = id.group(0)[5:]
    else:
        req = requests.get(url)
        id = re.search("' id='post[0123456789]*'>",req.text)
        if id != None:
            id = id.group(0)
            id = id[10:len(id)-2]
    return id
def content_selection(content, start_str, nst, net):
    content_start = content.find(start_str)
    if content_start != -1:
        content = content[content_start+len(start_str):]
        level = 1
        pointer = 0
        ned = 0
        while(True):
            ned_old = ned
            nsd = content.find(nst, pointer)
            ned = content.find(net, pointer)
            if level == 0:
                break
            elif nsd > ned and ned != -1:
                pointer = ned+1
                level -= 1
            elif nsd < ned and nsd != -1:
                pointer = nsd+1
                level += 1
            elif nsd < ned and nsd == -1:
                pointer = ned+1
                level -= 1
        return content[:ned_old]
    else:
        return ''
def forum_name(content):
    posted_by_class = re.search('<p>Posted by: <a class="member.*?" href="\/members\/.*?-[0123456789]{4}">.*?<\/a><\/p>', content).group(0)
    posted_by_name = re.search('href="\/members\/[^"]*',posted_by_class).group(0)[15:]
    posted_by_name = posted_by_name.replace('-',' ',posted_by_name.count('-')-1).replace('-','.')
    return [posted_by_name,forum_anet(posted_by_class)]
def forum_anet(posted_by_class):
    posted_by_anet = re.search('class="member [^"]*',posted_by_class).group(0)
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
    for i in range(1,len(c_split)-4):
        name += c_split[i] + ' '
    return name.strip()
def blog_datetime(content):
    c_split = content.split()
    datetime = ''
    for i in range(len(c_split)-3,len(c_split)):
        datetime += c_split[i] + ' '
    return datetime.strip()
def parse_host_from_url(url):
    return re.search('\/\/.*?guildwars2.com',url).group(0)[2:]
def html_to_markdown(content, host):
    content = tag_bold(content)
    content = tag_italic(content)
    content = tag_list(content)
    content = tag_superscript(content)
    content = tag_strikethrough(content)
    content = tag_underline(content)
    content = tag_breakrow(content)
    content = tag_h1(content)
    content = tag_h2(content)
    content = tag_h3(content)
    content = tag_h4(content)
    content = tag_h5(content)
    content = tag_h6(content)
    content = tag_screenshot(content, host)
    content = tag_paragraph(content)
    content = tag_iframe(content, host)
    content = tag_href(content, host)
    content = tag_img(content, host)
    content = tag_quote(content, host)
    content = tag_spoiler(content, host)
    content = content.strip('\n')    
    content = '>' + content.replace('\n','\n>')
    content = tag_other(content)
    return content
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
                content = content.replace(re_link,'[' + parser._text + '](https://' + host + parser._href + ')')
            else:
                content = content.replace(re_link,'[' + parser._text + '](' + parser._href + ')')
    return content
def tag_quote(content, host):
    level = 0
    pointer = 0
    quote_list = []
    dict = {}
    while(True):
        nsb = content.find('<blockquote>', pointer)
        neb = content.find('</blockquote>', pointer)
        
        if nsb == -1 and neb == -1:
            break
        
        if nsb < neb and nsb != -1:
            pointer = nsb+1
            try:
                dict[level].append(nsb)
            except KeyError:
                dict[level] = [nsb]
            level += 1
        elif nsb > neb and neb != -1:
            pointer = neb+1
            level -= 1
            quote_list.append([dict[level][len(dict[level])-1],neb])
        elif nsb < neb and nsb == -1:
            pointer = neb+1
            level -= 1
            quote_list.append([dict[level][len(dict[level])-1],neb])
        else:
            print('something went wrong (nsb found, neb not found)')

    replace_list = []
    
    for start,end in quote_list:       
        message = content[start:end]
        quotey = message[message.find('<div class="quotey">')+len('<div class="quotey">'):message.rfind('</div>')+len('</div>')]
        replace_list.append([message,quotey])
    replace_list.reverse()

    for message,quotey in replace_list:
        quotey = quotey.replace('\n','\n>')
        quotey = quotey.replace('\n></div>','\n')
        oc = content
        while oc == content:
            content = content.replace(message + '</blockquote>', '>' + quotey)
            message = message.replace('\n','\n>').replace('\n></div>','\n')
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
def tag_bold(content):
    return content.replace('<strong>','**').replace('</strong>','**')
def tag_italic(content):
    return content.replace('<em>','*').replace('</em>','*')
def tag_list(content):
    return content.replace('<li>','* ').replace('</li>','\n').replace('<ul>',"").replace('</ul>','').replace('<ol>','').replace('</ol>','')
def tag_paragraph(content):
    return content.replace('<p>',"").replace('</p>','\n')
def tag_superscript(content):
    return content.replace('<sub>','^(').replace('</sub>',')').replace('<sup>',"").replace('</sup>','')
def tag_strikethrough(content):
    return content.replace('<del>','~~').replace('</del>','~~')
def tag_underline(content):
    return content.replace('<ins>','###### ').replace('</ins>','')
def tag_breakrow(content):
    return content.replace('<br/>','\n').replace('<br />','\n').replace('<br>','')
def tag_h1(content):
    return content.replace('<h1>','# ').replace('</h1>','')
def tag_h2(content):
    return content.replace('<h2>','## ').replace('</h2>','')
def tag_h3(content):
    return content.replace('<h3>','### ').replace('</h3>','')
def tag_h4(content):
    return content.replace('<h4>','#### ').replace('</h4>','')
def tag_h5(content):
    return content.replace('<h5>','##### ').replace('</h5>','')
def tag_h6(content):
    return content.replace('<h6>','###### ').replace('</h6>','')
def tag_tabs(content):
    return content.replace('\t','')
def tag_other(content):
    return (content.replace('<li class="yui3-g">'," ").replace('<div class="yui3-u-1">'," ")
                .replace('</div>'," ").replace('<div>'," ").replace('<div id="commerce-intro">'," ")
                .replace('<div class="featured">', " ").replace('<div id="commerce-items">'," ")
                .replace('<div class="copy">'," "))
