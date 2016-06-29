import html.parser
import urllib.parse
import markdown_dictionary as m


class Htmlparser(html.parser.HTMLParser):
    # History of tag,attrs to get attrs-data at handle_endtag()
    pathList = []
    # The markdown string which will get build over time
    result = ''
    # The current data from the current opened tag
    currentText = ''
    # The host including protocol of the submission, e.g.: https://forum-en.guildwars2.com
    host = ''

    # Blockquote indention level
    lvlBlockquote = 0
    # Resulting from blockquote indention level: the text modifier (suitable number of '>'s
    qm = ''

    # State for code tag
    is_code = False

    # State for a tag
    is_a = False

    """
    Return the pos item (tag-name or attributes) from the end of the pathlist
    """
    def read_pathlist(self, pos, name):
        return self.pathList[-pos][name]

    """
    Repairs relative and relative/external urls to absolute https urls
    """
    def repair_href(self, href):
        if href[:12] == '/external?l=':
            return urllib.parse.unquote_plus(href[12:])
        elif href[:2] == '//':
            return 'https:' + href
        elif href[:1] == '/':
            return self.host + href
        elif href[:str(href).find('?')].isdigit():
            return self.host + '/forums/en/overwatch/topic/' + href
        else:
            return href

    """
    Formats url and (opt.) visual/url description into markdown syntax
    """
    @staticmethod
    def mrkd_href(href, visual=''):
        if visual == '':
            return '{0}{1}{2}{3}{1}{4}'.format(m.lvs, href.strip(), m.lve, m.lhs, m.lhe)
        else:
            return '{0}{1}{2}{3}{4}{5}'.format(m.lvs, visual.strip(), m.lve, m.lhs, href.strip(), m.lhe)

    """
    Extracts userfriendly youtube url from embedded url
    """
    @staticmethod
    def excavate_youtube(url):
        return url

    """
    Appends string including (opt.) blockquote modifier, (opt.) nextline and (opt.) codespacer to final result.
    """
    def append(self, string, qm=None, is_nextline=False):
        if qm is None:
            qm = self.qm
        if self.is_code:
            string = m.code + str(string)

        if is_nextline:
            self.result += m.newline2 + qm + str(string)
        else:
            self.result += str(string)

    """
    Appends string to current data
    """
    def add(self, string):
        self.currentText += string

    """
    Returns current data to caller and clears the data afterwards
    """
    def get_current_text(self):
        t = self.currentText
        self.currentText = ''
        return t

    """
    Handles starttag of html parser
    """
    def handle_starttag(self, tag, attrs):
        if tag == 'blockquote':
            self.lvlBlockquote += 1
        if tag == 'p':
            self.append('', None, True)
        if tag == 'strong':
            self.add(m.bold)
        if tag == 'em':
            self.add(m.itallic)
        if tag == 'del':
            self.add(m.strike)
        if tag == 'h1':
            self.add(m.h1)
        if tag == 'h2':
            self.add(m.h2)
        if tag == 'h3':
            self.add(m.h3)
        if tag == 'h4':
            self.add(m.h4)
        if tag == 'h5':
            self.add(m.h5)
        if tag == 'h6' or tag == 'ins' or (tag == 'span' and attrs[0][1] == 'underline'):
            self.add(m.h6)
        if tag == 'ul':
            self.add(m.newline2)
        if tag == 'li':
            self.add(m.li)
        if tag == 'a':
            self.append(self.get_current_text())
            self.is_a = True
        if tag == 'code':
            self.is_code = True
        if attrs is not None:
            self.pathList.append({'tag': tag, 'attrs': dict(attrs)})
        else:
            self.pathList.append({'tag': tag, 'attrs': None})

    """
    Handles data of html parser
    """
    def handle_data(self, data):
        self.currentText += data

    """
    Handles endtag of html parser
    """
    def handle_endtag(self, tag):
        # Following variables are needed to distinguish between links out of blockquotes and links in blockquotes
        self.qm = ''

        if self.lvlBlockquote > 0:
            for i in range(0, self.lvlBlockquote):
                self.qm += m.quote

        if tag == 'blockquote':
            self.lvlBlockquote -= 1
            self.append(self.get_current_text(), is_nextline=True)
        if tag == 'span' and self.read_pathlist(1, 'attrs') is not None:
            for key in self.read_pathlist(1, 'attrs'):
                if str(self.read_pathlist(1, 'attrs')[key]).find('bml-quote-date') != -1:
                    self.append(self.get_current_text() + ' ',is_nextline=True)
                if str(self.read_pathlist(1, 'attrs')[key]).find('truncated') != -1:
                    self.get_current_text()
                if str(self.read_pathlist(1, 'attrs')[key]).find('underline') != -1:
                    self.append(self.get_current_text(), is_nextline=True)
        if tag == 'img':
            self.add(self.mrkd_href(self.repair_href(self.read_pathlist(1, 'attrs')['src'])))
        if tag == 'p':
            self.append(self.get_current_text(), is_nextline=True)
        if tag == 'strong':
            self.add(m.bold)
        if tag == 'em':
            self.add(m.itallic)
        if tag == 'a':
            self.append(self.mrkd_href(self.repair_href(self.read_pathlist(1, 'attrs')['href']), self.get_current_text()))
            self.is_a = False
        if tag == 'del':
            self.add(m.strike)
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ins']:
            self.append(self.get_current_text(), is_nextline=True)
        if tag == 'br':
            if not self.is_a:
                self.append(self.get_current_text(), is_nextline=True)
        if tag == 'li':
            self.append(self.get_current_text() + m.newline2)
        if tag == 'iframe':
            self.append(self.mrkd_href(self.excavate_youtube(self.repair_href(self.read_pathlist(1,'attrs')['src']))))
        if tag == 'div':
            self.append(self.get_current_text(), is_nextline=True)
        if tag == 'code':
            self.append(self.get_current_text(), is_nextline=True)
            self.is_code = False
        if len(self.pathList) > 0:
            self.pathList.pop()


def parse(source, host):
    parser = Htmlparser()
    parser.host = host
    parser.convert_charrefs = True
    parser.feed(source)
    return parser.result

if __name__ == '__main__':
    print(parse('<strong>boldtest</strong><br /><em>ittalictest</em><br /><span class="underline">underlinetest</span><br /><ul><li>listitem1</li><li>listitem2</li></ul><br />http://<br /><code>codetest <br />us.battle.net/forums/en/overwatch/<br />    code<strong>boldtest</strong></code><br /><blockquote><blockquote><span class="truncated">...</span>quote2</blockquote>quote1</blockquote>helloworld</div>', "https://us.battle.net"))