import scrapy
import lxml.html as html


LINKS_PACKS = '//div[@id="card_list_1"]/table//tr[1]/td[1]/div/div/div/input/@value'
CARDS_NAMES = '//div[@class="list_style"]/ul/li/dl/dt/span[2]/strong/text()'
CARDS_ATRIBUTES = '//div[@class="list_style"]/ul/li/dl/dd[1]/span[1]/span//text()'
CARDS_LVLS = '//div[@class="list_style"]/ul/li/dl/dd[1]/span[2]/span[contains(text(),"Level") or contains(text(), "Rank") or contains(text(), "Link")]/text()'
CARDS_TYPES = '//div[@class="list_style"]/ul/li/dl/dd[1]/span[3]//text()'
CARDS_ATK = '//div[@class="list_style"]/ul/li/dl/dd[1]/span[4]//text()'
CARDS_DEF = '//div[@class="list_style"]/ul/li/dl/dd[1]/span[5]//text()'
CARDS_DESCRIPTION = '//div[@class="list_style"]/ul/li/dl/dd[2 or 3]/text()[1]'


class yugiohScraper(scrapy.Spider):
    name = 'yugioh'
    start_urls = [
        'https://www.db.yugioh-card.com/yugiohdb/card_list.action'
    ]
    custom_settings = {
        'FEEDS': {
            'cards.json': {
                'format': 'json',
                'encoding': 'utf-8',
                'indent': 4,
                'overwrte': True
            }
        },
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }

    def parse_links(self, response):
        response_str = str(response.body, encoding='utf-8').replace('<br>', '; ').replace(
            '\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '')
        response_2 = html.fromstring(response_str)

        descrs = response_2.xpath(CARDS_DESCRIPTION)
        names = response_2.xpath(CARDS_NAMES)
        atributes = response_2.xpath(CARDS_ATRIBUTES)
        lvls = response_2.xpath(CARDS_LVLS)
        types = response_2.xpath(CARDS_TYPES)
        atks = response_2.xpath(CARDS_ATK)
        defs = response_2.xpath(CARDS_DEF)

        cont = 0
        for atr, typee, descr in zip(atributes, types, descrs):
            for i, typee in enumerate(types):
                if typee == '\xa0':
                    types.pop(i)
            if atr == 'SPELL' or atr == 'TRAP':
                lvls.insert(cont, 'n/a')
                types.insert(cont, 'n/a')
                atks.insert(cont, 'n/a')
                defs.insert(cont, 'n/a')
            if 'Effect' not in typee:
                descr = 'n/a'
            cont += 1

        if len(atks) != len(names):
            for i in range(len(names)-len(atks)):
                atks.append('n/a')
                defs.append('n/a')
                lvls.append('n/a')
                types.append('n/a')

        for i, name in enumerate(names):
            yield {
                'name': names[i],
                'atribute': atributes[i],
                'lvl': lvls[i],
                'type': types[i],
                'atk': atks[i],
                'def': defs[i],
                'description': descrs[i]
            }

    def parse(self, response):
        links = response.xpath(LINKS_PACKS).getall()
        for link in links:
            yield response.follow(link, callback=self.parse_links)
