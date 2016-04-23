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

    lvlBlockquote = 0
    qm = ''

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
            return '{0}{1}{2}{3}{1}{4}'.format(m.lvs, href, m.lve, m.lhs, m.lhe)
        else:
            return '{0}{1}{2}{3}{4}{5}'.format(m.lvs, visual, m.lve, m.lhs, href, m.lhe)

    def append(self, string, qm=None, is_nextline=False):
        if qm is None:
            qm = self.qm
        if is_nextline:
            self.result += '\n\n' + qm + str(string)
        else:
            self.result += str(string)

    def handle_starttag(self, tag, attrs):
        if tag == 'blockquote':
            self.lvlBlockquote += 1
        if tag == 'p':
            self.append('', None, True)
        if tag == 'strong':
            self.append(self.currentText + m.bold)
        if tag == 'em':
            self.append(self.currentText + m.itallic)
        if attrs is not None:
            self.pathList.append({'tag': tag, 'attrs': dict(attrs)})
        else:
            self.pathList.append({'tag': tag, 'attrs': None})

    def handle_data(self, data):
        self.currentText = data

    def handle_endtag(self, tag):
        self.qm = ''
        qtitle = ''
        qnewline = False
        qmcite = ''
        if tag == 'blockquote':
            self.lvlBlockquote -= 1
        if self.lvlBlockquote > 0:
            for i in range(0, self.lvlBlockquote):
                self.qm += m.quote
            if tag == 'a' and self.read_pathlist(2, 'tag') == 'cite':
                qnewline = True
                qmcite = self.qm
                qtitle = self.read_pathlist(2, 'attrs')['title']
        if tag == 'img':
            self.currentText += self.mrkd_href(self.repair_href(self.read_pathlist(1, 'attrs')['src']))
        if tag == 'p':
            self.append(self.currentText + m.newline)
        if tag == 'strong':
            self.append(self.currentText + m.bold)
        if tag == 'em':
            self.append(self.currentText + m.itallic)
        if tag == 'a':
            self.append(self.mrkd_href(self.repair_href(self.read_pathlist(1, 'attrs')['href']),
                                       self.currentText + qtitle), qmcite, qnewline)
        self.currentText = ''


def parse(input):
    parser = Htmlparser()
    parser.base_url = 'https://forum-en.guildwars2.com'
    parser.convert_charrefs = True
    with open('tests/quote2') as text:
        parser.feed(text.read())
    print(parser.result)


if __name__ == '__main__':
    parse('')
