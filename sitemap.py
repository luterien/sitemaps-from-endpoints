#!/usr/bin/env python
import urllib.parse
import requests
import json


class Client:

    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, url):
        try:
            resp = requests.get(url)
            print(url)
            return json.loads(resp.content)
        except:
            raise

class URLHandler:

    def __init__(self, base_url):
        self.base_url = base_url

    def from_path(self, path):
        return self.base_url + path


class BaseSitemap:

    def __init__(self):
        self.client = Client(self.BASE_URL)
        self.url_handler = URLHandler(self.BASE_URL)

    def get_urls(self):
        raise NotImplementedError

    def get_url_data(self):
        raise NotImplementedError

    def get_items(self):
        items = []
        for url in self.get_urls():
            things = self.client.get(url)
            urls = self.get_url_data(things)
            if urls:
                items.extend(urls)
        return items


class JobSitemap(BaseSitemap):

    BASE_URL = "http://localhost:4000/api"

    def get_urls(self):
        return [self.url_handler.from_path("/jobs")]

    def get_url_data(self, resp):
        return [self.serialize(k) for k in resp]

    def serialize(self, item):
        return {
            "url": self.url_handler.from_path("/jobsz/%s" % item["slug"]),
            "date": None
        }


class XMLFileMaker:

    def __init__(self, destination):
        self.destination = destination

    def create(self, items):
        nodes = [self.make_node(k) for k in items]
        file_content = self.make_file("\n".join(nodes))
        return self.write("sitemap.xml", file_content)

    def write(self, filename, contents):
        with open(filename, 'w') as f:
            f.write(contents)
            return filename

    def make_node(self, item):
        template= """<url>\n<loc>%s/</loc>\n<lastmod>%s</lastmod>\n<changefreq>daily</changefreq>\n<priority>0.8</priority>\n</url>"""
        today = "2019-01-03"
        return template % (item.get('url'), item.get('date') or today)

    def make_file(self, content):
        base = """<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>"""
        return base % content


class SitemapGenerator:

    def __init__(self, sources, target_location):
        self.source_classes = sources
        self.xml_file_maker = XMLFileMaker("/tmp")

    def create(self, many=False):
        for source_class in self.source_classes:
            items = (source_class)().get_items()
            filename = self.xml_file_maker.create(items)
            return filename


sitemap_sources = [JobSitemap,]
sitemap_generator = SitemapGenerator(
    sources=sitemap_sources,
    target_location="/tmp"
)
filename = sitemap_generator.create()
