import shutil
import tempfile
import unittest
from pathlib import Path
import yaml
from build import ROOT, build
from support import create_fixture


class TeachingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        create_fixture(self.root)
        self.folder = self.root / 'content/courses/semiconductors'
        self.out = self.root / 'dist'

    def add_lessons(self):
        config = {'title':'Semiconductor Notes','description':'','chapters':[
            {'title':'Chapter A','lessons':['first-lesson','second-lesson']},
            {'title':'Chapter B','lessons':['third-lesson']} ]}
        (self.folder/'course.yml').write_text(yaml.safe_dump(config))
        for slug in ('first-lesson','second-lesson','third-lesson'):
            (self.folder/f'{slug}.md').write_text(f'---\ntitle: {slug}\n---\n\nAuthor notes.\n\n<!-- practice -->\n\nAuthor exercise.\n\n<details markdown="1">\n<summary>Show Solution</summary>\n\n**Author answer.**\n\n</details>\n')
        return config

    def test_empty_course_and_removed_samples(self):
        build(self.root)
        html=(self.out/'chips.html').read_text()
        self.assertIn('Semiconductor Notes',html)
        self.assertIn('No posts yet.',html)
        self.assertNotIn('chapter-menu',html)
        self.assertNotIn('#downloads',html)
        self.assertFalse((self.out/'notes/semiconductors').exists())
        self.assertEqual(list((self.out/'assets/files/semiconductors').glob('*.pdf')),[])
        for marker in ('Charge carriers','Doping','0.714','starter-handout','Sample material'):
            self.assertNotIn(marker,html)

    def test_notes_practice_and_sequence_when_author_adds_lessons(self):
        self.add_lessons()
        build(self.root)
        first=(self.out/'notes/semiconductors/first-lesson.html').read_text()
        last=(self.out/'notes/semiconductors/third-lesson.html').read_text()
        self.assertNotIn('rel="prev"',first)
        self.assertIn('rel="next" href="../../notes/semiconductors/second-lesson.html"',first)
        self.assertNotIn('rel="next"',last)
        practice=(self.out/'notes/semiconductors/first-lesson-practice.html').read_text()
        self.assertIn('<summary>Show Solution</summary>',practice)
        self.assertIn('<strong>Author answer.</strong>',practice)
        self.assertIn('second-lesson-practice.html',practice)
        self.assertNotIn('Author exercise.',first)
        # Removing all lessons must remove old generated pages too.
        (self.folder/'course.yml').write_text('title: Semiconductor Notes\ndescription: ""\nchapters: []\n')
        build(self.root)
        self.assertFalse((self.out/'notes/semiconductors').exists())

    def test_order_and_unlisted_lessons(self):
        config=self.add_lessons()
        config['chapters'][0]['lessons'].reverse()
        (self.folder/'course.yml').write_text(yaml.safe_dump(config))
        (self.folder/'unfinished.md').write_text('Unfinished draft')
        build(self.root)
        first=(self.out/'notes/semiconductors/second-lesson.html').read_text()
        self.assertNotIn('rel="prev"',first)
        self.assertIn('rel="next" href="../../notes/semiconductors/first-lesson.html"',first)
        self.assertFalse((self.out/'notes/semiconductors/unfinished.html').exists())

    def test_author_download_is_listed_and_missing_file_preserves_build(self):
        self.add_lessons()
        attachment=self.root/'assets/files/semiconductors/author-notes.txt'
        attachment.write_text('Author attachment')
        lesson=self.folder/'first-lesson.md'
        lesson.write_text(lesson.read_text().replace('title: first-lesson','title: first-lesson\ndownloads:\n  - label: My notes\n    file: assets/files/semiconductors/author-notes.txt'))
        build(self.root)
        before=(self.out/'chips.html').read_bytes()
        self.assertIn(b'author-notes.txt',before)
        attachment.unlink()
        with self.assertRaisesRegex(ValueError,'download must exist'):
            build(self.root)
        self.assertEqual((self.out/'chips.html').read_bytes(),before)

    def test_duplicate_and_missing_lessons_fail(self):
        config=self.add_lessons()
        config['chapters'][0]['lessons'].append('second-lesson')
        (self.folder/'course.yml').write_text(yaml.safe_dump(config))
        with self.assertRaisesRegex(ValueError,'unique'):
            build(self.root)
        config['chapters'][0]['lessons'][-1]='missing-lesson'
        (self.folder/'course.yml').write_text(yaml.safe_dump(config))
        with self.assertRaisesRegex(ValueError,'Missing lesson'):
            build(self.root)

    def test_notes_only_lesson_needs_no_invented_exercises(self):
        self.add_lessons()
        first=self.folder/'first-lesson.md'
        first.write_text(first.read_text().split('<!-- practice -->')[0])
        build(self.root)
        notes=(self.out/'notes/semiconductors/first-lesson.html').read_text()
        self.assertIn('Author notes.',notes)
        self.assertNotIn('first-lesson-practice.html',notes)
        self.assertFalse((self.out/'notes/semiconductors/first-lesson-practice.html').exists())
        overview=(self.out/'chips-practice.html').read_text()
        self.assertNotIn('first-lesson-practice.html',overview)
        self.assertIn('second-lesson-practice.html',overview)
        second=(self.out/'notes/semiconductors/second-lesson-practice.html').read_text()
        self.assertNotIn('rel="prev"',second)
