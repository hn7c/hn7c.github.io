import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit

from build import ROOT, build
from support import create_fixture
from new_post import create_post


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls=[]
        self.ids=set()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name in ('href','src'):
            if name in attrs:
                self.urls.append(attrs[name])


class BlogTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        create_fixture(self.root)
        self.out=self.root/'dist'

    def post(self,section='optics',slug='2026-11-25-test',title='Test title',date='2026-11-25',draft=False,body='A **bold** note.',summary='A summary.'):
        path=self.root/'content/posts'/section/(slug+'.md')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(f'---\ntitle: {json.dumps(title)}\ndate: {date}\nsummary: {json.dumps(summary)}\ndraft: {str(draft).lower()}\n---\n\n{body}\n')
        return path

    def test_add_edit_and_delete_post(self):
        path=self.post()
        self.assertEqual(build(self.root),1)
        target=self.out/'posts/optics/2026-11-25-test.html'
        self.assertIn('<strong>bold</strong>',target.read_text())
        self.assertIn('Test title',(self.out/'index.html').read_text())
        path.write_text(path.read_text().replace('Test title','Revised title'))
        build(self.root)
        self.assertIn('Revised title',target.read_text())
        path.unlink()
        build(self.root)
        self.assertFalse(target.exists())
        self.assertNotIn('Revised title',(self.out/'optics.html').read_text())

    def test_drafts_and_templates_never_published(self):
        self.post(draft=True,title='Secret draft',body='Unfinished secret content')
        self.assertEqual(build(self.root),0)
        html=''.join(p.read_text() for p in self.out.rglob('*.html'))
        self.assertNotIn('Secret draft',html)
        self.assertNotIn('Unfinished secret content',html)
        self.assertNotIn('Your post title',html)
        self.assertIn('No posts yet.',(self.out/'optics.html').read_text())

    def test_order_and_section_membership(self):
        self.post(slug='older',title='Older optics',date='2026-11-20')
        self.post(slug='newer',title='Newer optics',date='2026-11-25')
        self.post(section='chips',title='Chip article')
        build(self.root)
        optics=(self.out/'optics.html').read_text()
        self.assertLess(optics.index('Newer optics'),optics.index('Older optics'))
        self.assertNotIn('Chip article',optics)
        self.assertIn('Chip article',(self.out/'archive.html').read_text())

    def test_metadata_is_escaped_and_markdown_features_work(self):
        self.post(title='<script>alert(1)</script>',summary='A <b>summary</b>',body='## Heading\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n```python\nprint("hello")\n```')
        build(self.root)
        html=(self.out/'posts/optics/2026-11-25-test.html').read_text()
        self.assertNotIn('<script>alert(1)</script>',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('<table>',html)
        self.assertIn('language-python',html)

    def test_all_links_work_on_github_project_subpath(self):
        self.post(body='![Portrait](assets/portrait.svg)\n\n[Resume](/resume.html)\n\n[Work](work.html)\n\n[External](https://example.com)')
        build(self.root)
        origin='https://example.org/my-repository/'
        parsed={}
        for file in self.out.rglob('*.html'):
            parser=Links();parser.feed(file.read_text());parsed[file]=parser
        for file,parser in parsed.items():
            base=origin+file.relative_to(self.out).as_posix()
            for href in parser.urls:
                url=urlsplit(urljoin(base,href))
                if url.netloc != 'example.org':
                    continue
                self.assertTrue(url.path.startswith('/my-repository/'),(file,href))
                target=self.out/unquote(url.path.removeprefix('/my-repository/'))
                if target.is_dir(): target=target/'index.html'
                self.assertTrue(target.is_file(),(file,href,target))
                if url.fragment:
                    self.assertIn(unquote(url.fragment),parsed[target].ids,(file,href))

    def test_bad_metadata_fails_without_erasing_previous_site(self):
        build(self.root)
        before=(self.out/'index.html').read_text()
        self.post(date='not-a-date')
        with self.assertRaisesRegex(ValueError,'date must'):
            build(self.root)
        self.assertEqual(before,(self.out/'index.html').read_text())

    def test_new_post_helper_creates_draft_and_refuses_overwrite(self):
        path=create_post('mathematics','A proof: first notes','2026-11-25',self.root)
        self.assertEqual(path.name,'2026-11-25-a-proof-first-notes.md')
        self.assertIn('draft: true',path.read_text())
        with self.assertRaises(FileExistsError):
            create_post('mathematics','A proof: first notes','2026-11-25',self.root)
        self.assertEqual(build(self.root),0)

    def test_all_requested_sections_exist_in_order(self):
        build(self.root)
        expected=['resume','work','cats','forensics','chips','optics','mathematics','econ','art','recs','sartorial','rowing','cycling','intpoli','firearms','boats','cars','bristol','db-am','hongqi']
        html=(self.out/'index.html').read_text()
        offsets=[html.index(f'href="{slug}.html"') for slug in expected]
        self.assertEqual(offsets,sorted(offsets))
        for slug in expected:
            self.assertTrue((self.out/(slug+'.html')).is_file())
        self.assertTrue((self.out/'intpoli/index.html').is_file())

    def test_car_subsections_and_parent_feed(self):
        self.post(section='bristol',title='Bristol article',date='2026-11-26')
        self.post(section='db-am',title='DB AM article',date='2026-11-25')
        self.post(section='hongqi',title='Hongqi article',date='2026-11-24')
        self.post(section='cars',title='General car article',date='2026-11-23')
        self.post(section='boats',title='Boat article')
        self.post(section='firearms',title='Firearms article')
        build(self.root)
        cars=(self.out/'cars.html').read_text()
        for title in ('Bristol article','DB AM article','Hongqi article','General car article'):
            self.assertIn(title,cars)
        self.assertLess(cars.index('Bristol article'),cars.index('DB AM article'))
        self.assertNotIn('Boat article',cars)
        self.assertNotIn('Firearms article',cars)
        bristol=(self.out/'bristol.html').read_text()
        self.assertIn('Bristol article',bristol)
        self.assertNotIn('Hongqi article',bristol)
        self.assertIn('href="cars.html"',bristol)
        home=(self.out/'index.html').read_text()
        self.assertIn('<a href="cars.html">Vintage Cars</a><ul>',home)
        archive=(self.out/'archive.html').read_text()
        self.assertEqual(archive.count('Bristol article'),1)

    def test_new_sections_accept_drafts_and_published_edits(self):
        for slug in ('firearms','boats','cars','bristol','db-am','hongqi'):
            path=create_post(slug,'My first post','2026-11-26',self.root)
            self.assertIn('draft: true',path.read_text())
            path.write_text(path.read_text().replace('draft: true','draft: false'))
        self.assertEqual(build(self.root),6)
        for slug in ('firearms','boats','cars','bristol','db-am','hongqi'):
            self.assertIn('My first post',(self.out/(slug+'.html')).read_text())

    def test_name_and_institution_have_one_source(self):
        path=self.root/'site.json'
        config=json.loads(path.read_text())
        config.update(name='A & B',institution='Example Institute')
        path.write_text(json.dumps(config))
        build(self.root)
        home=(self.out/'index.html').read_text()
        self.assertIn('<h1>A &amp; B</h1>',home)
        self.assertIn('Example Institute',home)
        self.assertNotIn('{{name}}',home)
        self.assertIn('A &amp; B',(self.out/'resume.html').read_text())

    def test_semiconductor_posts_keep_course_layout(self):
        self.post(section='chips',title='My semiconductor post')
        build(self.root)
        html=(self.out/'posts/chips/2026-11-25-test.html').read_text()
        self.assertIn('class="course-page"',html)
        self.assertIn('class="course-paper"',html)
        self.assertIn('../../assets/course.css',html)
        self.assertIn('>Semiconductors</a>',html)
        self.assertNotIn('Chip Design',html)
        self.assertIn('>Semiconductors</a>',(self.out/'index.html').read_text())

    def test_public_names_and_markdown_page_intros(self):
        (self.root/'content/pages/work.md').write_text('My **work** introduction.')
        build(self.root)
        self.assertIn('My <strong>work</strong> introduction.',(self.out/'work.html').read_text())
        self.assertIn('Aston Martin — DB Series',(self.out/'db-am.html').read_text())
        self.assertIn('href="db-am.html"',(self.out/'cars.html').read_text())

    def test_missing_post_download_prevents_replacing_site(self):
        build(self.root)
        before=(self.out/'index.html').read_bytes()
        self.post(body='[Notes](assets/files/not-uploaded.pdf)')
        with self.assertRaisesRegex(ValueError,'missing local target'):
            build(self.root)
        self.assertEqual((self.out/'index.html').read_bytes(),before)

    def test_missing_anchor_and_bad_heading_fail_validation(self):
        path=self.post(body='[Missing heading](resume.html#not-there)')
        with self.assertRaisesRegex(ValueError,'missing anchor'):
            build(self.root)
        path.write_text(path.read_text().replace('[Missing heading](resume.html#not-there)','# Another top-level heading'))
        with self.assertRaisesRegex(ValueError,'one main heading'):
            build(self.root)


if __name__=='__main__':
    unittest.main()
