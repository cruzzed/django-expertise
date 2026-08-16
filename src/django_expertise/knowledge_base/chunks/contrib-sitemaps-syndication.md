# django.contrib.sitemaps and django.contrib.syndication

- **ID:** `contrib-sitemaps-syndication`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules, §2.1 Decision Tree
- **Tags:** `sitemaps`, `rss`, `seo`, `feeds`

## Canonical pattern (Django / HTMX / Hyperscript way)
sitemaps generates XML sitemaps from Sitemap classes (items(), lastmod(), changefreq); syndication generates RSS/Atom feeds by subclassing Feed with items(), item_title(), item_description(). Wire both into urls.py.

## Typical MVC default (what AI typically generates)
Typical MVC stacks rely on third-party sitemap/feed packages or hand-built XML views. AI installs SEO/feed third-party packages or string-builds XML by hand - both flagged in the spec's decision tree.

## Why Django differs
These are classic Django batteries with first-class hooks into the ORM and URL resolver. Hand-rolled XML generators are error-prone (escaping, dates) and duplicate what contrib already maintains.

## Example
# sitemaps.py
from django.contrib.sitemaps import Sitemap
class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    def items(self): return Product.objects.filter(discontinued=False)
    def lastmod(self, obj): return obj.updated_at

# feeds.py
from django.contrib.syndication.views import Feed
class LatestProductsFeed(Feed):
    title = "New products"
    link = "/products/"
    def items(self): return Product.objects.order_by('-created_at')[:20]
    def item_title(self, item): return item.name
