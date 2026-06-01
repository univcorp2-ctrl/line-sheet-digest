# Setup

日本語の詳細手順は `docs/SETUP_LINE_ja.md` を参照してください。

## Required external setup

1. Create a LINE Official Account.
2. Enable Messaging API in LINE Official Account Manager.
3. Get Channel secret and Channel access token from LINE Developers Console.
4. Deploy the Cloudflare Worker or another HTTPS webhook server.
5. Set the webhook URL in LINE Developers Console and verify it.
6. Add secrets to GitHub Actions / Cloudflare / GAS.

## Local checks

```bash
python scripts/validate_env.py --mode local
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
cd cloudflare-worker && npm test
```

## Production send

```bash
LINE_DRY_RUN=false python scripts/line_oa.py --execute push-text --to <recipient> --text "hello"
```
