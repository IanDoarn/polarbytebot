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
    # The base url of the submission, e.g.: forum-en.guildwars2.com
    base_url = ''

    # <blockquote> stuff
    lvlBlockquote = 0
    qm = ''

    # <ul> stuff
    lvlUl = 0
    um = ''

    # <ol> stuff
    lvlOl = 0
    om = ''

    def read_pathlist(self, pos, name):
        return self.pathList[-pos][name]

    def repair_href(self, href):
        if href[:12] == '/external?l=':
            return urllib.parse.unquote_plus(href[12:])
        elif href[:2] == '//':
            return 'https:' + href
        else:
            return self.base_url + href

    @staticmethod
    def mrkd_href(href, visual=''):
        if visual == '':
            return '{0}{1}{2}{3}{1}{4}'.format(m.lvs, href.strip(), m.lve, m.lhs, m.lhe)
        else:
            return '{0}{1}{2}{3}{4}{5}'.format(m.lvs, visual.strip(), m.lve, m.lhs, href.strip(), m.lhe)

    def append(self, string, qm=None, is_nextline=False):
        if qm is None:
            qm = self.qm

        if is_nextline:
            self.result += m.newline2 + qm + str(string)
        else:
            self.result += str(string)

    def get_current_text(self):
        t = self.currentText
        self.currentText = ''
        return t

    def handle_starttag(self, tag, attrs):
        if tag == 'blockquote':
            self.lvlBlockquote += 1
        if tag == 'p':
            self.append('', None, True)
        if tag == 'strong':
            self.append(self.get_current_text() + m.bold)
        if tag == 'em':
            self.append(self.get_current_text() + m.itallic)
        if tag == 'del':
            self.append(self.get_current_text() + m.strike)
        if tag == 'h1':
            self.append(self.get_current_text() + m.h1)
        if tag == 'h2':
            self.append(self.get_current_text() + m.h2)
        if tag == 'h3':
            self.append(self.get_current_text() + m.h3)
        if tag == 'h4':
            self.append(self.get_current_text() + m.h4)
        if tag == 'h5' or tag == 'ins':
            self.append(self.get_current_text() + m.h5)
        if tag == 'h6':
            self.append(self.get_current_text() + m.h6)
        if attrs is not None:
            self.pathList.append({'tag': tag, 'attrs': dict(attrs)})
        else:
            self.pathList.append({'tag': tag, 'attrs': None})

    def handle_data(self, data):
        self.currentText += data

    def handle_endtag(self, tag):
        self.qm = ''
        qtitle = ''
        qnewline = False
        qmcite = ''
        if tag == 'blockquote':
            self.lvlBlockquote -= 1
        if tag == 'ul':
            self.lvlUl-= 1
        if self.lvlBlockquote > 0:
            for i in range(0, self.lvlBlockquote):
                self.qm += m.quote
            if tag == 'a' and self.read_pathlist(2, 'tag') == 'cite':
                qnewline = True
                qmcite = self.qm
                qtitle = self.read_pathlist(2, 'attrs')['title']
        if self.lvlUl > 0:
            for i in range(0, self.lvlUl):
                self.um += m.tab
        if self.lvlOl > 0:
            for i in range(0, self.lvlOl):
                self.om += m.tab
        if tag == 'img':
            self.currentText += self.mrkd_href(self.repair_href(self.read_pathlist(1, 'attrs')['src']))
        if tag == 'p':
            self.append(self.get_current_text() + m.newline2)
        if tag == 'strong':
            self.append(self.get_current_text() + m.bold)
        if tag == 'em':
            self.append(self.get_current_text() + m.itallic)
        if tag == 'a':
            self.append(self.mrkd_href(self.repair_href(self.read_pathlist(1, 'attrs')['href']),
                                       self.get_current_text() + qtitle), qmcite, qnewline)
        if tag == 'del':
            self.append(self.get_current_text() + m.strike)
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ins']:
            self.append(self.get_current_text() + m.newline2)
        if tag == 'br':
            self.append(self.get_current_text() + m.newline1)


def parse(input):
    parser = Htmlparser()
    parser.base_url = 'https://forum-en.guildwars2.com'
    parser.convert_charrefs = True
    with open('tests/quote2') as text:
        parser.feed(text.read())
    print(parser.result)


if __name__ == '__main__':
    parse('')
