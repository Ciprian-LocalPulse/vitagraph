# wiki/ — GitHub Wiki source pages

This folder contains the source for VitaGraph's **GitHub Wiki**
(the screenshot in the project's planning notes showed an empty wiki —
these five pages plus a sidebar are the content to publish there).

## Pages

1. **[`Home.md`](Home.md)** — landing page, quick links, project status
2. **[`Getting-Started.md`](Getting-Started.md)** — install, quick start, CLI + library usage
3. **[`Architecture.md`](Architecture.md)** — the 7-stage pipeline, diagram, module mapping
4. **[`Methodology-and-Scope.md`](Methodology-and-Scope.md)** — precise scope statement, formulas, limitations
5. **[`FAQ-and-Troubleshooting.md`](FAQ-and-Troubleshooting.md)** — common questions and errors
6. **[`_Sidebar.md`](_Sidebar.md)** *(bonus, not counted among the 5)* — persistent nav shown on every wiki page

## How to publish these to your repository's GitHub Wiki

GitHub Wikis are themselves a separate Git repository, cloned at
`<your-repo-url>.wiki.git`. To publish:

```bash
# 1. Enable the wiki: repo Settings → Features → check "Wikis"
# 2. Create the wiki's first page once via the GitHub UI (Wiki tab →
#    "Create the first page") — this initializes the wiki's git repo.
# 3. Clone the wiki repo alongside your main repo clone:
git clone https://github.com/Ciprian-LocalPulse/vitagraph.wiki.git

# 4. Copy these files in (page filenames become the page titles,
#    with hyphens rendered as spaces):
cp wiki/*.md vitagraph.wiki/

# 5. Commit and push:
cd vitagraph.wiki
git add .
git commit -m "docs: publish Home, Getting Started, Architecture, Methodology and Scope, FAQ pages"
git push
```

After pushing, the wiki will be live at:
`https://github.com/Ciprian-LocalPulse/vitagraph/wiki`

## Keeping this in sync

Because the GitHub Wiki is a separate Git repository, changes made
directly on the wiki (via the web UI) won't automatically flow back
into `wiki/` in the main repository, and vice versa. Treat `wiki/` here
as the source of truth for review/PR purposes, and periodically sync
`vitagraph.wiki/` from it (or edit only here and re-push per the steps
above) to avoid drift.
