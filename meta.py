"""class with meta information of the chapter or story"""
# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder

import json
from datetime import datetime


class Meta:
    """class with meta information of the chapter or story"""
    def __init__(self, debug):
        self.debug = debug
        self.title = ""
        self.author = ""
        self.published_time = ""
        self.modified_time = ""
        self.description = ""
        self.tag = ""
        self.author = ""
        self.pov = ""
        self.category = ""
        self.speech = ""
        self.published_time = ""
        self.published_time_short = ""
        self.modified_time = ""
        self.modified_time_short = ""
        self.likes = ""
        self.views = ""


    def scrape_meta_properties(self, soup):
        """scrape all properties"""
        self.title = self.scrape_meta_property(soup, "og:title")
        self.published_time = self.scrape_meta_property(soup, "article:published_time").strip()
        self.modified_time = self.scrape_meta_property(soup, "article:modified_time")
        self.description = self.scrape_meta_property(soup, "og:description")
        if not self.published_time == '':
            self.published_time_short = datetime.fromisoformat(self.published_time).date().isoformat()
        else:
            self.published_time_short = ""

        if not self.modified_time == '':
            self.modified_time_short = datetime.fromisoformat(self.modified_time).date().isoformat()
        else:
            self.modified_time_short = ""

        self.scrape_pairs_columns(soup)

        if self.debug:
            print(f"content title: {self.title}")
            print(f"content published_time: {self.published_time}")
            print(f"content modified_time: {self.modified_time}")
            print(f"content description: {self.description}")
            print(f"content description: {self.description}")


    def scrape_meta_property(self, soup, property_name):
        """scape the property name in the class meta"""
        tag = soup.find("meta", property=f"{property_name}")

        if tag:
            content = tag["content"]
        else:
            content = ""
        return content


    def scrape_pairs_columns(self, soup):
        """scape the pov and category content"""
        pair = soup.find("div", class_="pairs-columns info")

        if pair:
            dt = pair.find("dt", string="POV")
            if dt:
                dd = dt.find_next_sibling("dd")
                if dd:
                    self.pov = dd.get_text(strip=True)

            dt = pair.find("dt", string="Category")
            if dt:
                dd = dt.find_next_sibling("dd")
                if dd:
                    self.category = dd.get_text(strip=True)


    def scrape_json(self, soap):
        """scrape json information if exists"""
        script = soap.find("script", type="application/ld+json")

        if script:
            # load json content
            try:
                data = json.loads(script.string, strict=False)

                if "inLanguage" in data and "name" in data["inLanguage"]:
                    self.speech = data["inLanguage"]["name"]
                else:
                    self.speech = ""

                if "keywords" in data:
                    self.tag = data["keywords"]
                else:
                    self.tag = ""

                stats = {
                    stat["interactionType"].split("/")[-1]: int(stat["userInteractionCount"])
                    for stat in data["interactionStatistic"]
                }
                self.likes = stats["LikeAction"]
                self.views = stats["WatchAction"]

                if self.debug:
                    print(f"tag: {self.tag}")
                    print(f"speech: {self.speech}")
                    print(f"likes: {self.likes}")
                    print(f"views: {self.views}")
            except Exception as e:
                print("Typ:", type(e))
                print("Typ-Name:", type(e).__name__)
                print(f"Error: '{e}")
                print(script.string)
