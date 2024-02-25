# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from w3lib.html import remove_tags
from scrapy.exceptions import DropItem
from slugify import slugify

class AssasinsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Remove HTML tags from the notes
        notes = adapter.get("notes")
        if notes:
            # If there's a title, remove HTML tags from it
            if 'titre' in notes:
                notes['titre'] = remove_tags(notes['titre'])
            
            # If there's content, remove HTML tags from it
            if 'contenu' in notes:
                notes['contenu'] = remove_tags(notes['contenu'])

            # Update the item with cleaned notes
            adapter['notes'] = notes

        # Slugify the name to get the url
        value = adapter.get("name")
        if value is not None:
            value = slugify(value, lowercase=False, decimal=False, allow_unicode=True, separator="_")
            adapter["url"] = "https://assassinscreed.fandom.com/fr/wiki/" + value

        return item
