# Hoonapps

Hoonapps is a personal technical blog for backend development, AI tool notes,
open-source experiments, system design notes, and project logs.

The site keeps the existing English archive, but new publishing is Korean-first.

## Local Development

```bash
rbenv local 3.3.0
bundle install
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

Open <http://127.0.0.1:4000/>.

## Build

```bash
bundle exec jekyll build
```

## AI Notes

Collect current AI engineering candidates:

```bash
python3 tools/ai_radar.py --days 7 --limit 12 --write-data
```

Create a draft from the collected candidates:

```bash
python3 tools/ai_radar.py --days 7 --limit 12 --write-data --draft
```

The generated data is rendered at `/ai-radar/`.

## Content System

- Operating guide: `docs/CONTENT_OPERATING_SYSTEM.md`
- AI notes template: `docs/templates/ai-radar.md`
- Backend Deep Dive template: `docs/templates/backend-deep-dive.md`
- Project Log template: `docs/templates/project-log.md`

## Deployment

GitHub Pages deployment is handled by `.github/workflows/pages-deploy.yml`.
AI topic data refresh is handled by `.github/workflows/ai-radar.yml`.
