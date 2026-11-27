"""Exercise the boundary between editor output and the existing static builder."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml

from build import ROOT, build
from support import create_fixture


class DecapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        create_fixture(self.root)
        shutil.copytree(ROOT / 'admin', self.root / 'admin')
        self.config = yaml.safe_load((self.root / 'admin/config.yml').read_text())

    def test_editor_survives_rebuild_and_cannot_be_output_directory(self):
        build(self.root)
        for name in ('index.html', 'setup.js', 'config.yml'):
            self.assertEqual((self.root / 'admin' / name).read_bytes(),
                             (self.root / 'dist/admin' / name).read_bytes())
        (self.root / 'admin/config.yml').write_text(
            (self.root / 'admin/config.yml').read_text().replace(
                'YOUR_TURBO_SITE_ID', '11111111-2222-4333-8444-555555555555'))
        build(self.root)
        self.assertIn('11111111-2222-4333-8444-555555555555',
                      (self.root / 'dist/admin/config.yml').read_text())
        with self.assertRaises(ValueError):
            build(self.root, self.root / 'admin')
        self.assertTrue((self.root / 'admin/index.html').is_file())

    def test_every_section_has_compatible_editor_fields(self):
        sections = json.loads((self.root / 'site.json').read_text())['sections']
        collections = {item['name']: item for item in self.config['collections']}
        self.assertEqual(set(collections), {section['slug'] for section in sections})
        for section in sections:
            collection = collections[section['slug']]
            self.assertEqual(collection['folder'], 'content/posts/' + section['slug'])
            fields = {field['name']: field for field in collection['fields']}
            self.assertEqual(set(fields), {'title', 'date', 'summary', 'draft', 'body'})
            self.assertIs(fields['draft']['default'], True)
            self.assertEqual(fields['date']['format'], 'YYYY-MM-DD')

    def test_cms_draft_then_published_post_with_download(self):
        collection = next(item for item in self.config['collections']
                          if item['name'] == 'emergency-lighting')
        post = self.root / collection['folder'] / '2026-11-27-editor-check.md'
        post.parent.mkdir(parents=True)
        media = self.root / self.config['media_folder']
        media.mkdir(parents=True)
        (media / 'slides.pdf').write_bytes(b'%PDF-1.4\n%%EOF\n')
        meta = {'title': 'Editor check', 'date': '2026-11-27', 'summary': '', 'draft': True}
        body = '\n## Notes\n\n[Slides](' + self.config['public_folder'] + '/slides.pdf)\n'
        def save():
            post.write_text('---\n' + yaml.safe_dump(meta) + '---\n' + body)
        save()
        self.assertEqual(build(self.root), 0)
        target = self.root / 'dist/posts/emergency-lighting/2026-11-27-editor-check.html'
        self.assertFalse(target.exists())
        meta['draft'] = False
        save()
        self.assertEqual(build(self.root), 1)
        self.assertIn('href="../../assets/uploads/slides.pdf"', target.read_text())
        self.assertIn('Editor check', (self.root / 'dist/emergency-lighting.html').read_text())
        self.assertIn('Editor check', (self.root / 'dist/archive.html').read_text())
        self.assertIn('Editor check', (self.root / 'dist/index.html').read_text())
        (media / 'slides.pdf').unlink()
        with self.assertRaisesRegex(ValueError, 'missing local target'):
            build(self.root)
        self.assertTrue(target.is_file())


if __name__ == '__main__':
    unittest.main()
