# Connect the included Decap editor

This package includes the editor files and the build integration. It does not create a GitHub repository, a Turbo account, or a working login on your behalf. The public website still builds normally before you finish connecting the editor. Opening `/admin/` shows setup instructions until a valid Turbo Site ID is supplied.

## 1. Upload the website to GitHub

Extract the complete website ZIP. Upload its CONTENTS at your repository's top level, preserving `admin/`, `assets/`, `content/`, `templates/`, `tests/`, and `.github/workflows/pages.yml`. Use branch `main`.

In repository Settings → Pages → Build and deployment, choose GitHub Actions. Run **Deploy to GitHub Pages** from the Actions tab. Wait for a successful deployment.

If you already uploaded the previous website ZIP, the smaller Decap update ZIP contains the new and modified files only. Extract it and merge its contents into the repository, preserving the relative paths and replacing the included `build.py` and `README.md`. It does not include or overwrite your posts, site.json, resume, homepage, or semiconductor lessons. Keep your existing files that are absent from the update ZIP. The new `build.py` is necessary: uploading only `admin/` would not deploy the editor with the old build.

## 2. Connect Decap Turbo

1. Open https://turbo.decapcms.org/ and create an account/organization. Choose the Free plan for one site and one editor.
2. Open **Git connection**, install the Turbo GitHub App, and select only your website repository.
3. Create a site in Turbo using these settings:

| Setting | Value |
| --- | --- |
| Git provider | GitHub |
| Repository | Your actual `OWNER/REPOSITORY` |
| Branch | `main` |
| Config path | `admin/config.yml` |
| Admin interface URL | Your GitHub Pages URL followed by `/admin/` |

For a personal site the admin URL looks like `https://YOUR-USERNAME.github.io/admin/`. For a project repository it looks like `https://YOUR-USERNAME.github.io/REPOSITORY/admin/`. Use the actual address shown in GitHub's Pages settings; keep the repository segment for project sites.

4. Copy the **Site ID** (a UUID) from the Turbo site's Overview tab.
5. Edit `admin/config.yml` in GitHub. Replace only `YOUR_TURBO_SITE_ID` with that ID:

```yaml
backend:
  name: turbo-github
  turbo_site_id: YOUR_TURBO_SITE_ID
  branch: main
```

The ID comes from Turbo, not from the site hosted in ChatGPT. It is a public identifier, not a password. Never put API tokens, passwords, or OAuth secrets in this file. The repository is selected in the Turbo dashboard; this backend does not use a `repo` setting in the YAML.

6. Commit the change to `main`, wait for deployment, then open your site's `/admin/` page. Choose **Login with Turbo**.

## 3. Write a post

1. Choose a section and select **New Post**.
2. Enter a title, date, short description and article body.
3. Keep **Keep off the public website** enabled while drafting.
4. When ready, switch it OFF and use Decap's save/publish action.
5. Wait for the GitHub Actions deployment to succeed, then check the public article.

This installation uses Decap's simple workflow: saving writes to `main`. Your builder separately checks the `draft` field. A CMS action labelled Publish does not override the hidden-post switch. Public repositories expose committed draft source files even when the generated website omits them. Future dates affect sorting, not scheduled publishing.

The `_template.md` files are retained for manual writing. If Decap displays entries named **Your post title**, leave them alone and use **New Post**. The builder never publishes filenames beginning with `_`.

The 20 blog collections are configured. Resume and the homepage remain in their existing source files; this package does not add dedicated editing forms for them. Semiconductor blog posts use `content/posts/chips/`. Ordered semiconductor lessons remain a separate course system in `content/courses/semiconductors/`, configured as before. No semiconductor articles or lessons have been added.

## Images, PDFs and slides

Use the Media area to upload files. New CMS uploads are stored in `assets/uploads/` and copied into the published site. Insert an image using the editor's image control. For a PDF or slide deck, insert a normal hyperlink to the uploaded path, for example:

```markdown
[Download the slides](assets/uploads/my-slides.pdf)
![Describe the image](assets/uploads/my-photo.jpg)
```

Those names are examples, not included files. Use the exact filename of your own upload. Keep local links relative as shown; the builder resolves them for nested articles and GitHub project URLs. Add alt text for images and start body headings at level 2 (`##`).

Keep existing images and files in their current folders; you do not need to move them. The editor preview pane is disabled until a preview matching the site's templates is implemented. This does not disable the writing editor.

## Adding a section later

Add it to `site.json` as before. Then copy a collection block in `admin/config.yml`, changing `name`, `label`, and `folder` to match the new section. Keep `fields: *id001` if copying a later collection: that YAML alias shares the first collection's field definitions. Update the first collection's fields to change the common form for every section.

## Checks and troubleshooting

- **Setup instructions still appear:** replace the placeholder with the Turbo UUID, commit the source `admin/config.yml`, and wait for a successful deployment. Editing only `dist/admin/config.yml` is temporary; the next build replaces it.
- **Login is refused:** check your Turbo site's allowed admin URL and GitHub repository connection, and that your Turbo account has access to this site.
- **A saved post does not appear:** turn off the hidden-post switch; check the Actions tab for a failed build. Do not edit `_template.md` as a real post.
- **Build reports a missing local file:** correct the link or upload the referenced file before publishing.
- **The workflow does not appear:** restore `.github/workflows/pages.yml` and use the `main` branch.
- **Decap cannot be downloaded:** the editor loads a pinned Decap 3.17.0 script from jsDelivr; check the network/content blocker. The site itself does not depend on that script.

Run the checks locally, if desired:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python build.py
```

The build copies `admin/` into `dist/admin/`. The setup shell contains a real heading, so the existing HTML validator remains enabled without a special exemption. `admin/` is protected from being used as a generated output directory.

Login, GitHub writes and live publication must be tested after connecting your accounts. The packaged tests check CMS-shaped content, draft visibility, links, configuration and build integration; they do not authenticate to your accounts.

Official references, checked 27 November 2026:

- https://decapcms.org/docs/turbo-getting-started/
- https://decapcms.org/docs/turbo-connecting-a-site/
- https://decapcms.org/docs/configuration-options/
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
