#!/usr/bin/env python3
"""Build a newsletter issue page from the Substack API.

Usage:
  python3 build-newsletter-issue.py            # build newest issue if not already built
  python3 build-newsletter-issue.py <slug>     # build a specific issue by Substack slug

Pulls the post from the Substack API, cleans Substack widgets out of the
HTML, downloads images locally, builds the issue page from
/newsletter/template/index.html, updates the archive and sitemap, and
commits. Does NOT push: publishing needs Doug's approval.
"""
import json, os, re, sys, html as htmlmod
import urllib.request
from html.parser import HTMLParser
from datetime import datetime

SITE = '/home/hatch/workspace/site-rebuild'
TOOLS = os.path.join(SITE, '_tools')
WATERMARK = os.path.join(TOOLS, 'last_issue.json')
API = 'https://storiesandstrategies.substack.com'

KEEP_TAGS = {'p', 'a', 'em', 'strong', 'b', 'i', 'ul', 'ol', 'li',
             'blockquote', 'hr', 'br', 'h2', 'h3', 'figure', 'figcaption', 'img'}

VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
             'link', 'meta', 'param', 'source', 'track', 'wbr'}

class Cleaner(HTMLParser):
    def __init__(self, img_handler):
        super().__init__(convert_charrefs=False)
        self.out = []
        self.skip_depth = 0          # inside subscription widget
        self.img_handler = img_handler
        self.in_figure = False
        self.fig_img = None
        self.fig_caption = []

    def _open(self, tag, attrs):
        """Shared start-tag logic. Returns True if tag was consumed."""
        attrs = dict(attrs)
        cls = attrs.get('class', '')
        if tag == 'div' and 'subscription-widget' in cls:
            self.skip_depth += 1
            return True
        if tag == 'span' and 'mention-wrap' in cls:
            return True  # drop span, keep inner text
        if tag == 'h4':
            tag = 'h2'
        if tag == 'figure':
            self.in_figure = True
            self.fig_img = None
            self.fig_caption = []
            return True
        if tag == 'img' and self.in_figure:
            self.fig_img = {'src': attrs.get('src', ''), 'alt': attrs.get('alt', '')}
            return True
        if tag == 'figcaption' and self.in_figure:
            self.out.append('<figcaption>')
            return True
        if tag not in KEEP_TAGS:
            return True  # drop tag, keep inner text
        if tag == 'a':
            href = attrs.get('href', '')
            self.out.append('<a href="%s">' % htmlmod.escape(href, quote=True))
        elif tag == 'img':
            # stray img outside figure: route through handler
            new = self.img_handler(attrs.get('src', ''), attrs.get('alt', ''))
            self.out.append(new)
        else:
            self.out.append('<%s>' % tag)
        return True

    def handle_starttag(self, tag, attrs):
        if self.skip_depth:
            if tag not in VOID_TAGS:
                self.skip_depth += 1
            return
        self._open(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        if self.skip_depth:
            return
        self._open(tag, attrs)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == 'figure' and self.in_figure:
            self.in_figure = False
            if self.fig_img:
                new = self.img_handler(self.fig_img['src'], self.fig_img['alt'])
                self.out.append('<figure class="featured-img">%s' % new)
                if self.fig_caption:
                    self.out.append('<figcaption>%s</figcaption>' % ''.join(self.fig_caption))
                self.out.append('</figure>')
                self.fig_caption = []
            return
        if tag == 'figcaption' and self.in_figure:
            return  # closed in figure handler
        if tag == 'h4':
            tag = 'h2'
        if tag in KEEP_TAGS:
            self.out.append('</%s>' % tag)

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.in_figure and self.fig_img is None:
            return
        self.out.append(data)

    def handle_entityref(self, name):
        if not self.skip_depth:
            self.out.append('&%s;' % name)

    def handle_charref(self, name):
        if not self.skip_depth:
            self.out.append('&#%s;' % name)

    def result(self):
        body = ''.join(self.out)
        # drop empty paragraphs
        body = re.sub(r'<p>\s*</p>', '', body)
        # uniform subheaders: plain <h2>text</h2>, no nested bold/italic/link tags
        body = re.sub(r'<h2[^>]*>(.*?)</h2>',
                      lambda m: '<h2>' + re.sub(r'<[^>]+>', '', m.group(1)).strip() + '</h2>',
                      body, flags=re.S)
        return body


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    os.makedirs(TOOLS, exist_ok=True)
    watermark = {}
    if os.path.exists(WATERMARK):
        watermark = json.load(open(WATERMARK))

    if len(sys.argv) > 1:
        slug = sys.argv[1]
        post = json.loads(fetch('%s/api/v1/posts/%s' % (API, slug)).decode())
    else:
        archive = json.loads(fetch('%s/api/v1/archive?sort=new&limit=1' % API).decode())
        post = archive[0]
        slug = post['slug']

    if watermark.get('slug') == slug:
        print('already built:', slug)
        return

    title = post['title']
    post_date = post['post_date'][:10]
    pretty = datetime.strptime(post_date, '%Y-%m-%d').strftime('%B %-d, %Y')
    canonical = post.get('canonical_url', '')
    cover = post.get('cover_image') or ''

    img_dir = os.path.join(SITE, 'images', 'newsletter', slug)
    os.makedirs(img_dir, exist_ok=True)
    counter = [0]

    def img_handler(src, alt):
        if not src:
            return ''
        counter[0] += 1
        ext = '.png'
        m = re.search(r'\.(png|jpe?g|webp|gif)(\?|$)', src, re.I)
        if m:
            ext = '.' + m.group(1).lower().replace('jpeg', 'jpg')
        fname = 'img%d%s' % (counter[0], ext)
        try:
            data = fetch(src)
            open(os.path.join(img_dir, fname), 'wb').write(data)
        except Exception as e:
            print('image download failed:', src, e)
            return ''
        return '<img src="/images/newsletter/%s/%s" alt="%s" loading="lazy">' % (
            slug, fname, htmlmod.escape(alt or title, quote=True))

    # cover image
    cover_local = ''
    if cover:
        try:
            data = fetch(cover)
            cover_local = 'images/newsletter/%s/cover.png' % slug
            open(os.path.join(SITE, cover_local), 'wb').write(data)
        except Exception as e:
            print('cover download failed:', e)

    cleaner = Cleaner(img_handler)
    cleaner.feed(post.get('body_html') or '')
    body = cleaner.result()

    # meta description: subtitle or first paragraph
    desc = (post.get('subtitle') or '').strip()
    if not desc:
        m = re.search(r'<p>(.*?)</p>', body, re.S)
        if m:
            desc = re.sub(r'<[^>]+>', '', m.group(1)).strip()[:160]

    template = open(os.path.join(SITE, 'newsletter', 'template', 'index.html'), encoding='utf-8').read()
    url = 'https://storiesandstrategies.ca/newsletter/%s/' % slug
    full_title = '%s | Stories and Strategies' % title
    img_url = 'https://storiesandstrategies.ca/' + cover_local if cover_local else ''

    page = template
    page = page.replace('<meta name="robots" content="noindex">\n', '')
    page = page.replace('[Sample] Issue title | Stories and Strategies', htmlmod.escape(full_title))
    page = page.replace('[Sample] One or two sentences describing what this issue covers.', htmlmod.escape(desc))
    page = page.replace('https://storiesandstrategies.ca/newsletter/template/', url)
    page = page.replace('https://storiesandstrategies.ca/images/newsletter/template/cover.png', img_url)
    page = page.replace(
        '<div class="episode-meta"><time datetime="2026-10-07">October 7, 2026</time> · The Newsletter for Branded Podcasts</div>',
        '<div class="episode-meta"><time datetime="%s">%s</time> · The Newsletter for Branded Podcasts</div>' % (post_date, pretty))
    page = page.replace('<h1>[Sample] Issue title goes here</h1>', '<h1>%s</h1>' % htmlmod.escape(title))
    if cover_local:
        page = page.replace(
            '<img src="/images/newsletter/template/cover.png" alt="Sample newsletter cover: [Issue title]" width="1264" height="710">',
            '<img src="/%s" alt="%s" width="1264" height="710">' % (cover_local, htmlmod.escape(title, quote=True)))
    else:
        page = re.sub(r'<figure class="featured-img">.*?</figure>\n', '', page, flags=re.S)
    old_body = '''      <div class="article-body">
        <p><b>[Sample]</b> Newsletter issue text goes here, pulled from the Substack API and cleaned of Substack widgets.</p>
        <p><b>[Sample]</b> Subheadings become h2 elements, images are hosted locally, links are preserved.</p>
      </div>'''
    assert old_body in page, 'template body block changed!'
    page = page.replace(old_body, '      <div class="article-body">\n        %s\n      </div>' % body)
    # strip template comments
    page = re.sub(r'<!--\n  NEWSLETTER ISSUE TEMPLATE.*?\n-->\n', '', page, flags=re.S)
    page = page.replace('      <!-- Issue publish date. Pulled from Substack with each issue. -->\n', '')
    page = page.replace('''      <!-- FEATURED IMAGE SLOT: replace the src below with the issue's
           cover image (saved under /images/newsletter/<issue-slug>/)
           and update the alt text. -->
''', '')

    dest_dir = os.path.join(SITE, 'newsletter', slug)
    os.makedirs(dest_dir, exist_ok=True)
    open(os.path.join(dest_dir, 'index.html'), 'w', encoding='utf-8').write(page)
    print('page built:', slug)

    # archive entry (newest first)
    ap = os.path.join(SITE, 'newsletter', 'index.html')
    ah = open(ap, encoding='utf-8').read()
    entry = '''      <article class="episode-entry">
        <div>
          <h3><a href="/newsletter/%s/">%s</a></h3>
          <div class="date"><time datetime="%s">%s</time></div>
          <p>%s</p>
        </div>
      </article>
''' % (slug, htmlmod.escape(title), post_date, pretty, htmlmod.escape(desc))
    # remove the "first issue" note if present
    ah = re.sub(r'      <div class="archive-note">.*?</div>\n', '', ah, flags=re.S)
    # insert before the entry-pattern comment
    # insert the new entry directly before the pattern comment (entries must
    # stay OUTSIDE html comments or browsers hide them)
    marker = '      <!--\n        ISSUE ENTRY PATTERN'
    assert marker in ah, 'archive marker missing'
    ah = ah.replace(marker, entry + marker, 1)
    # latest-issue section on the archive page (so visitors see content, not a gate)
    latest_re = re.compile(r'    <!-- LATEST ISSUE START.*?<!-- LATEST ISSUE END -->\n', re.S)
    # pull the freshly built article content back out of the issue page
    ip = open(os.path.join(dest_dir, 'index.html'), encoding='utf-8').read()
    im = re.search(r'<div class="episode-meta">(.*?)</div>\s*<h1>(.*?)</h1>\s*(<figure class="featured-img">.*?</figure>)?\s*<div class="article-body">\n(.*?)\n      </div>', ip, re.S)
    if im and latest_re.search(ah):
        meta_inner, ititle, ifig, ibody = im.group(1), im.group(2), im.group(3) or '', im.group(4)
        # only swap the "latest issue" slot when this build is actually newer
        cur = latest_re.search(ah).group(0)
        cur_d = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})">', cur)
        new_d = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})">', meta_inner)
        if new_d and (not cur_d or new_d.group(1) >= cur_d.group(1)):
            latest = '''    <!-- LATEST ISSUE START: refreshed automatically by _tools/build-newsletter-issue.py
         whenever a new issue is built. Do not edit by hand. -->
    <section aria-label="Latest issue">
      <div class="wrap">
        <div class="eyebrow">This week&apos;s issue</div>
        <div class="episode-meta">%s</div>
        <h2>%s</h2>
        %s
        <div class="article-body">
%s
        </div>
        <p style="margin-top: 32px;"><a href="/newsletter/%s/">Permalink to this issue</a> &middot; <a href="https://storiesandstrategies.substack.com/" target="_blank" rel="noopener">Get it by email every Wednesday</a></p>
      </div>
    </section>
    <!-- LATEST ISSUE END -->
''' % (meta_inner, ititle, ifig, ibody, slug)
            ah = latest_re.sub(latest, ah)
            print('latest-issue section refreshed')
        else:
            print('latest-issue section left alone (not newer)')
    open(ap, 'w', encoding='utf-8').write(ah)
    print('archive updated')

    # sitemap
    sp = os.path.join(SITE, 'sitemap.xml')
    sx = open(sp, encoding='utf-8').read()
    new_url = '''  <url>
    <loc>%s</loc>
    <lastmod>%s</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>''' % (url, post_date)
    sx = sx.replace('</urlset>', new_url)
    open(sp, 'w', encoding='utf-8').write(sx)
    print('sitemap updated')

    json.dump({'slug': slug, 'built_at': datetime.now().isoformat()},
              open(WATERMARK, 'w'))
    os.system('cd %s && git add -A && git commit -q -m "Add newsletter issue: %s"' % (SITE, slug))
    print('committed (not pushed)')

if __name__ == '__main__':
    main()
