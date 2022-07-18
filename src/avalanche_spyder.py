import scrapy

class AvalancheSpider(scrapy.Spider):
    name = "avalanche"

    def start_requests(self):
        urls = [
            'https://utahavalanchecenter.org/avalanches/fatalities'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        avalanches = response.css('div.view-content tbody td a::attr(href)').getall()
        
        #
        yield from response.follow_all(avalanches, self.parse_avalanche_info)

        next_page = response.css('div.item-list li.pager-next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
    
    def parse_avalanche_info(self, response):
        # Get the field name labels
        keys = response.css('div.page-content div.field-label::text').getall()
        
        # Get the list of values for the field names
        values = response.css('div.page-content div.text_02.mb2')

        # Some fields name that will not be consider
        omit_keys = ['Comments', 'Video', 'Snow Profile Comments', 
                      'Weather Conditions and History', 'Terrain Summary', 
                      'Accident and Rescue Summary']
        
        # Create a empty dictionary
        avalanche_info = {}

        for i, key in enumerate(keys):   
            # Check and omit keys if necessary
            if key in omit_keys:
                continue
            
            if 'Date' in key:
                avalanche_info[key] = values[i].xpath('span/text()').get()
            else:
                avalanche_info[key] = values[i].xpath('text()').get()

        yield avalanche_info