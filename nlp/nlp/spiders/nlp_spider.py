from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from nlp.items import LyricsItem
from scrapy.http import Request

class Lyrics(CrawlSpider):
    name = 'lyrics'
    allowed_domains = ['absolutelyrics.com']
    start_urls = ['http://artists.letssingit.com/artists/popular/1']

    rules = (
        Rule(SgmlLinkExtractor(allow=('lyrics/artistlist/.', )), callback='parse_letter'),
    )

    def parse_letter(self, response):
        hxs = HtmlXPathSelector(response)
        pages = hxs.select("//div[@id='pagelist']//a/@href").extract()
        for page in pages:
            yield Request("http://www.absolutelyrics.com" + page, callback=self.parse_letter)
        artists = hxs.select("//div[@class='artistlist']/ul/li/a/@href").extract()
        for artist in artists:
            yield Request("http://www.absolutelyrics.com" + artist, callback=self.parse_artist)
    
    def parse_artist(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@id='artist_albumlist']//a/@href").extract()
        for l in links:
            yield Request("http://www.absolutelyrics.com" + l, callback=self.parse_lyrics)
    
    def parse_lyrics(self, response):
        hxs = HtmlXPathSelector(response)
        item = LyricsItem()
        item["artist"] = hxs.select("//div[@id='content']//h2/text()").extract()[0].split(" - ")
        item["lyrics"] = hxs.select("//p[@id='view_lyrics']/text()").extract()
        return item
