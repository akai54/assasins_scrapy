import scrapy
from assasins.items import AssasinsItem

class AssasinsSpiderSpider(scrapy.Spider):
    name = "assasins_spider"
    allowed_domains = ["assassinscreed.fandom.com", "proxy.scrapeops.io"]
    start_urls = ["https://assassinscreed.fandom.com/fr/wiki/Culte_de_Kosmos"]

    def get_valid_member_url(self, path):
        if "www" not in path and "play" not in path and "Local_Sitemap" not in path and "Chronologie_des_jeux" not in path and "/fr/wiki/" in path:
            return "https://assassinscreed.fandom.com" + path
            
        else:
            return None
    
    def parse(self, response):
        members = response.css("ul li a")

        for member in members:
            next_member = member.css("a::attr(href)").get()
            if next_member is not None:
                next_member_url = self.get_valid_member_url(next_member)
                if next_member_url is not None:
                    print(next_member_url)
                    yield response.follow(next_member_url, callback=self.parse_member_page)
        

    def parse_member_page(self, response):
        assasin_item = AssasinsItem()

        assasin_item["name"] = response.css("span.mw-page-title-main::text").get()
        assasin_item["quote"] = response.css("div.quote dl dd i::text").get()    

        assasin_item["birth_death_info"] = self.parse_birth_death_info(response)

        assasin_item["notes"] = self.parse_notes(response)

        yield assasin_item
    
    def parse_notes(self, response):
        notes = response.xpath("//table[@border=2]//tbody//tr")
        if notes is not None:
            for note in notes:
                titre = note.css("b").get()
                contenu = note.css("p").get()

                return {"titre": titre, "contenu": contenu}


    def parse_birth_death_info(self, response):
        parsed_info = {
            'birth_date': None,
            'birth_place': None,
            'death_date': None,
            'death_place': None,
        }
        
        # Using XPath to find the birth and death information
        birth_info = response.xpath("//h3[contains(., 'Naissance')]/following-sibling::div[1]")
        death_info = response.xpath("//h3[contains(., 'Décès')]/following-sibling::div[1]")
        
        # Parse birth information if available
        if birth_info:
            birth_text = birth_info.xpath(".//text()").extract()
            # Assuming the first line is always the date and the second (if exists) is the place
            if len(birth_text) >= 1:
                parsed_info['birth_date'] = birth_text[0].strip()
            if len(birth_text) >= 2:
                parsed_info['birth_place'] = birth_text[1].strip()
        
        # Parse death information if available
        if death_info:
            death_text = death_info.xpath(".//text()").extract()
            # Assuming the first line is always the date and the second (if exists) is the place
            if len(death_text) >= 1:
                parsed_info['death_date'] = death_text[0].strip()
            if len(death_text) >= 2:
                parsed_info['death_place'] = death_text[1].strip()
        
        return parsed_info