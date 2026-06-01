from __future__ import annotations

import os
from pathlib import Path

START = "<!-- AI_README_SETUP_GUIDE_START -->"
END = "<!-- AI_README_SETUP_GUIDE_END -->"
repo = os.environ.get("GITHUB_REPOSITORY", "this repository").split("/")[-1]

svg = """<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='720' viewBox='0 0 1200 720' role='img' aria-label='README初期設定ガイド'><rect width='1200' height='720' rx='28' fill='#f6f8fa'/><text x='60' y='78' font-family='Arial,sans-serif' font-size='38' font-weight='700' fill='#0f172a'>README 画像付き初期設定ガイド</text><text x='60' y='122' font-family='Arial,sans-serif' font-size='20' fill='#475569'>このリポジトリを初めて開いた人が上から順番に設定できる導線です。</text><g font-family='Arial,sans-serif' font-size='18'><rect x='60' y='170' width='300' height='170' rx='20' fill='#dbeafe' stroke='#2563eb' stroke-width='3'/><text x='88' y='218' font-size='26' font-weight='700' fill='#1e3a8a'>1. READMEを見る</text><text x='88' y='258' fill='#1e40af'>目的・必要Secret・手順を確認</text><rect x='450' y='170' width='300' height='170' rx='20' fill='#dcfce7' stroke='#16a34a' stroke-width='3'/><text x='478' y='218' font-size='26' font-weight='700' fill='#14532d'>2. Secrets設定</text><text x='478' y='258' fill='#166534'>値は必ず ******** でマスク</text><rect x='840' y='170' width='300' height='170' rx='20' fill='#fef3c7' stroke='#d97706' stroke-width='3'/><text x='868' y='218' font-size='26' font-weight='700' fill='#78350f'>3. Actions実行</text><text x='868' y='258' fill='#92400e'>Run workflow を押す</text><rect x='255' y='430' width='300' height='170' rx='20' fill='#ede9fe' stroke='#7c3aed' stroke-width='3'/><text x='283' y='478' font-size='26' font-weight='700' fill='#4c1d95'>4. 結果確認</text><text x='283' y='518' fill='#5b21b6'>ログ・artifact・出力を確認</text><rect x='645' y='430' width='300' height='170' rx='20' fill='#fee2e2' stroke='#dc2626' stroke-width='3'/><text x='673' y='478' font-size='26' font-weight='700' fill='#7f1d1d'>5. エラー対応</text><text x='673' y='518' fill='#991b1b'>失敗ステップとSecret名を確認</text></g><path d='M365 255 H435M755 255 H825M555 515 H635' stroke='#64748b' stroke-width='8' stroke-linecap='round'/><path d='M990 350 C990 390 920 415 855 425' stroke='#64748b' stroke-width='8' fill='none' stroke-linecap='round'/><text x='60' y='675' font-family='Arial,sans-serif' font-size='18' fill='#64748b'>詳細: docs/setup-visual-guide.md / 画像再生成: docs/image-generation-prompts.md</text></svg>"""

setup = f"""# 画像付き初期設定ガイド

![README setup guide](assets/readme-setup-guide.svg)

## 1. 最初に見る場所

README冒頭の「画像付き初期設定ガイド」から、必要な設定と実行手順を確認します。

## 2. Secretsの扱い

実際の値はREADME、Issue、ログ、画像に貼りません。例は `********`、`YOUR_SECRET_HERE`、`your-folder-id` のようにマスクします。

## 3. 基本手順

1. README冒頭で必要なSecretと外部サービス設定を確認します。
2. GitHub Secrets または Cloudflare Secrets に値を登録します。
3. GitHub Actions の `Run workflow` を実行します。
4. Actionsログで成功・失敗を確認します。
5. Artifact、レポート、CSV、Excel、TXTなどの成果物を確認します。

## 4. エラー時の見る順番

1. Actions の赤い失敗ステップ
2. Secret名のスペル
3. 権限不足、API制限、対象フォルダIDやURL
4. READMEのトラブルシューティング

## 5. 対象repo

`{repo}`
"""

prompts = """# 画像生成プロンプト集

利用環境で使える最新の GPT Image / ChatGPT Images モデルで生成してください。APIで `gpt-image-2` が利用可能な環境では `gpt-image-2` を優先します。Secret値は絶対に表示しません。

## README冒頭用まとめ画像

```text
日本語UI風のGitHubリポジトリ初期設定ガイド画像。横長16:9。タイトルは「README 画像付き初期設定ガイド」。5つの番号付きパネル: 1 READMEを見る、2 Secrets設定、3 GitHub Actions実行、4 Artifact/成果物確認、5 エラー時のログ確認。赤枠、矢印、短い説明ラベルを使う。Secret値は ******** または YOUR_SECRET_HERE と表示する。
```

## GitHub Secrets設定画面

```text
GitHubのSettings → Secrets and variables → ActionsでNew repository secretを追加する初心者向け手順画像。日本語ラベル、赤枠、番号付き。Secret名は EXAMPLE_SECRET、値は ********。
```

## GitHub Actions手動実行画面

```text
GitHub Actionsタブでworkflowを選び、Run workflowを押す手順の画像。日本語UI風。赤枠と番号付き。
```

## Artifactダウンロード画面

```text
GitHub Actionsの実行結果画面でArtifacts欄から成果物をダウンロードする手順画像。日本語ラベル、赤枠、番号付き。
```
"""

Path("docs/assets").mkdir(parents=True, exist_ok=True)
Path("docs/assets/readme-setup-guide.svg").write_text(svg, encoding="utf-8")
Path("docs/setup-visual-guide.md").write_text(setup, encoding="utf-8")
Path("docs/image-generation-prompts.md").write_text(prompts, encoding="utf-8")

block = f"""{START}
## 🧭 画像付き初期設定ガイド

![README 画像付き初期設定ガイド](docs/assets/readme-setup-guide.svg)

このリポジトリ **{repo}** を初めて開いた人は、まずここだけ見れば初期設定から実行、成果物確認まで進められます。

### 最初にやること

1. 必要なSecretや外部サービス設定を確認します。
2. GitHub Actions または README の実行手順に沿って動かします。
3. 実行ログと成果物を確認します。
4. エラー時は Actions の失敗ステップと Secret名を確認します。

### 詳しい画像付きガイド

- [docs/setup-visual-guide.md](docs/setup-visual-guide.md)
- [docs/image-generation-prompts.md](docs/image-generation-prompts.md)

> SecretやAPIキーの実値は、README、Issue、ログ、画像に絶対に貼らないでください。例では `********` または `YOUR_SECRET_HERE` を使います。

{END}
"""

readme = Path("README.md")
original = readme.read_text(encoding="utf-8") if readme.exists() else f"# {repo}\n"
if START in original and END in original:
    before = original.split(START, 1)[0]
    rest = original.split(START, 1)[1].split(END, 1)[1]
    updated = before + block + "\n\n" + rest.lstrip("\n")
else:
    updated = block + "\n\n" + original.lstrip("\n")
readme.write_text(updated, encoding="utf-8")
print("README visual setup guide installed")
