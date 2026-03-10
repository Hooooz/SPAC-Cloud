# OpenClaw Skills Installation (Quick)

This repo contains reusable OpenClaw skills. The two updated skills are:

- `design-inspiration-daily`
- `export-control-weekly`

## 1) Clone on another machine

```bash
git clone https://github.com/Hooooz/SPAC-Cloud.git
cd SPAC-Cloud
```

## 2) Copy skills into OpenClaw workspace

Assume your OpenClaw workspace is `~/clawd` (adjust if different):

```bash
mkdir -p ~/clawd/skills/design-inspiration-daily
mkdir -p ~/clawd/skills/export-control-weekly

cp -R deliverables/design-inspiration-daily-skill/* ~/clawd/skills/design-inspiration-daily/
cp -R deliverables/export-control-weekly-skill/* ~/clawd/skills/export-control-weekly/
```

## 3) Install runtime dependencies

```bash
python3 -m pip install --upgrade httpx pyyaml beautifulsoup4 lxml
```

## 4) Local sanity check

```bash
cd ~/clawd/skills/design-inspiration-daily
python3 src/fetch_search_results.py --keyword "拍立得周边" --max-results 10 --out data/search_results_scheduled.json
python3 src/trend.py --config config/config.yaml --input data/search_results_scheduled.json --keyword "拍立得周边" --out output/daily_scheduled

cd ~/clawd/skills/export-control-weekly
python3 src/monitor.py --config config/config.yaml --out output/weekly_scheduled
```

## 5) Recommended cron payload principle

- Force script execution path (do not let the model invent commands).
- Always use `python3`.
- If realtime retrieval has no valid data, send explicit failure reason instead of fabricated content.

