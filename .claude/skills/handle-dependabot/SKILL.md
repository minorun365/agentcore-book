---
name: handle-dependabot
description: 公開リポ（minorun365/agentcore-book）のDependabotアラート・PRを、読者のハンズオンを壊さない範囲で自動的に解消し続ける。/schedule での無人定期実行を想定
user-invocable: true
argument-hint: '[dry-run]'
model: sonnet
---

# Dependabot 自動対応スキル（公開リポ）

『AgentCore＆Strands Agents本』読者向け公開リポジトリ `minorun365/agentcore-book` で、Dependabot が検出するセキュリティアラート・依存更新を、**読者が書籍のハンズオン手順どおりに進めても支障が出ない範囲で自動的に解消し続ける**ためのスキル。`/schedule` での無人定期実行を前提に設計している。

> 💡 authoring リポ側にも同名 `/handle-dependabot` があるが、あちらは **対話的に原稿影響まで見る**スキル。こちらは **公開リポ専用・無人運用向け**で役割が異なる。

## 大前提（刊行後の運用ポリシー）

**「書籍どおりに読者が作業すれば自動でアップデートされるもの（＝原稿に登場しない依存のマイナー／パッチ更新）だけを自動で取り込む」**。これが唯一の判断基準。

- **原稿（書籍本文）はバージョンを固定している**。読者が原稿のコードブロックどおりに `uv add foo==X` した結果が `pyproject.toml` の直接依存ピン。**ここは Dependabot が何を言ってきても勝手に変えない**。原稿との乖離を絶対に作らない。
- 一方、`uv.lock` / `package-lock.json` に並ぶ**推移的依存（原稿に名前すら出てこない孫依存）**は、読者がロックを取り直せばどのみち動くバージョンに入れ替わる範囲。ここの semver 互換な更新（マイナー／パッチ）は無害なので、proactive に取り込んでよい。
- 見分け方はシンプル：**`pyproject.toml` / `package.json` に差分が出ない更新 ⇔ 原稿のピンが無傷 ⇔ 読者の手元で原稿どおり再現される ⇔ 取り込んでよい**。逆に `pyproject.toml` / `package.json` が 1 行でも変わる更新は、原稿との整合が絡むので**自動では絶対にやらない**。
- このスキルは GitHub 側の設定（`dependabot.yml`、リポジトリ Settings）を変更しない。Dependabot がセキュリティ更新PRを生成していなくても、アラートを直接ロックファイル修正で潰す。

## 読者影響の3分類

| 分類 | 条件 | 自動対応 |
|------|------|---------|
| 🟢 即取り込み | **`uv.lock` / `package-lock.json` だけ**が変わる更新（＝原稿に登場しない推移的依存の semver 互換更新）。Dependabot PR なら変更ファイルがロックファイルのみ。アラート修正なら `uv lock --upgrade-package` 後に `pyproject.toml` が無変更 | **無人で即マージ／即修正・コミット** |
| 🟡 著者通知 | `pyproject.toml` / `package.json` に差分が出るもの全般。具体的には ①直接依存のバージョン制約／ピンが変わる ②直接依存のメジャー更新 ③脆弱性を直すのに原稿のピンを動かす必要がある | **自動マージ・自動コミットしない**。GitHub Issue を作成/更新して @minorun365 にメンション通知し、判断を委ねる |
| 🔴 解消不能 | 制約・ピンをどう動かしても整合が取れない、互換バージョンの patched release が存在しない 等 | Issue で escalate。手は出さない |

> 迷ったら 🟡 に倒す。「原稿のピンを勝手に動かさない／読者のハンズオンを壊さない」が最優先で、セキュリティ対応の速さは二の次。コア依存（`strands-agents`, `bedrock-agentcore` 等）は通常 `pyproject.toml` の直接依存なので、ほぼ自動的に 🟡 になる。

## ワークフロー

引数に `dry-run` が指定された場合は、分類・サマリー報告までで止め、マージ・コミット・Issue 作成は行わない。

### Step 0: 前提確認・作業ディレクトリ

```bash
gh auth status
git -C ~/git/minorun365/agentcore-book remote get-url origin   # agentcore-book であることを確認
cd ~/git/minorun365/agentcore-book && git switch main && git pull --ff-only
```

公開リポのローカル clone は `~/git/minorun365/agentcore-book/`。`/schedule` のリモート実行で別の場所に checkout される場合は、そのリポルートを作業ディレクトリにする（`git rev-parse --show-toplevel`）。

### Step 1: 対象の洗い出し

オープンな Dependabot PR と未解決のセキュリティアラートの両方を取得する：

```bash
gh pr list --repo minorun365/agentcore-book --author "app/dependabot" --state open \
  --json number,title,headRefName,files
gh api repos/minorun365/agentcore-book/dependabot/alerts \
  --jq '[.[] | select(.state=="open")] | map({number, pkg: .dependency.package.name, ecosystem: .dependency.package.ecosystem, manifest: .dependency.manifest_path, severity: .security_advisory.severity, fixed_in: .security_vulnerability.first_patched_version.identifier})'
```

両方とも空なら「Dependabot 対応事項はありません」と報告して終了。

### Step 2: Dependabot PR の分類

各 PR について **diff 全文は読まない**（`uv.lock` の diff は巨大なため）。Step 1 で取得した `files` フィールドだけで判定する：

- 変更ファイルが `uv.lock` / `package-lock.json` **のみ** → 🟢
- `pyproject.toml` / `package.json` 内の直接依存が含まれる → PR タイトルの `from X to Y` でメジャー更新か・コア依存かを判定 → 🟡 or 🔴
  - 制約ファイルの差分だけ確認したいときは `gh pr diff <番号> --repo minorun365/agentcore-book -- '*.toml' 'package.json'` のようにパスを絞る（lock ファイルは除外）

### Step 3: アラート（対応 PR が無いもの）の分類と修正

Step 1 のアラートのうち、対応する Dependabot PR が**存在しない**ものを自力で修正する。`manifest` のディレクトリへ移動し、**対象パッケージだけ**をロックファイル上で安全バージョンに上げる：

**pip（uv）の場合**（例: `manifest=chapter8/uv.lock`, `pkg=python-multipart`, `fixed_in=0.0.27`）：

```bash
cd ~/git/minorun365/agentcore-book/chapter8
uv lock --upgrade-package python-multipart
git diff --stat
grep -A1 'name = "python-multipart"' uv.lock   # patched version 以上になったか確認
```

- `git diff --stat` の結果が **`uv.lock` のみ** → 🟢（次のステップでコミット）
- `pyproject.toml` も変わっている／`uv lock` がエラー／patched version に届かない → 制約を動かす必要あり → 🟡 or 🔴（Issue へ）

**npm の場合**（例: `manifest=chapter13/bookchecker/package.json`, `pkg=esbuild`）：

公開リポでは `package-lock.json` が `.gitignore` で**未追跡**。よって npm 系の脆弱性は「ロックファイルだけ差し替えてコミット」ができない。脆弱性のあるパッケージが推移的依存（例: `esbuild` ← `vite`）なら、それを潰すには親の直接依存（`vite` 等）を `package.json` で上げるしかなく、これは `package.json` 変更＝🟡 に該当する。**npm 系のアラートは自力修正せず、原則 🟡 として Issue 通知に回す**（実態確認のため `npm audit --json` の結果だけは Issue に貼ってよい）。

pip（uv）で同じパッケージが複数の章の `uv.lock` に出ている場合は章ごとに繰り返す。

### Step 4: 🟢 の確定（無人で実施）

確定前のセルフチェック（1 つでも該当したら 🟢 を取り消して 🟡 に降格）：

- マージ／コミットしようとしている差分に `pyproject.toml` / `package.json` が含まれていないか？
- 念のため心配なら、対象パッケージ名が原稿のコードブロックに出ていないか確認（authoring リポ `~/git/minorun365/agentcore-book-authoring/authoring/3_completed/` を `grep -rn '<パッケージ名>'`）。出ていたら原稿が固定しているバージョンなので 🟡。

`dry-run` でなく上記チェックを通過したら：

1. Dependabot PR（🟢）→ 即マージ：
   ```bash
   gh pr merge <番号> --repo minorun365/agentcore-book --squash --delete-branch
   ```
2. アラート直接修正（🟢）→ まとめてコミット＆プッシュ（複数パッケージを 1 コミットで可。メッセージは 1 行日本語）：
   ```bash
   cd ~/git/minorun365/agentcore-book
   git add -A
   git commit -m "⬆️ Dependabotアラート対応: <パッケージ名> をロックファイルで更新"
   git push origin main
   ```

### Step 5: 🟡 / 🔴 → GitHub Issue で著者通知

`dry-run` でなく、🟡・🔴 の項目があるとき：

1. 既存の通知 Issue を探す（重複作成防止）：
   ```bash
   gh issue list --repo minorun365/agentcore-book --state open \
     --search "in:title 🤖 Dependabot 要レビュー" --json number,title
   ```
2. あれば本文を編集して項目を追記、なければ新規作成（タイトル: `🤖 Dependabot 要レビュー: 自動マージできない依存更新があります`）。
3. 本文には必ず `@minorun365` をメンションし、各項目を箇条書きで：
   - 対象（PR番号 or アラート番号）／パッケージ／`from → to`／影響する章／分類（🟡 or 🔴）／自動マージしなかった理由（メジャー更新・コア依存・制約変更が必要 等）
   - 推奨アクション（例:「`/verify-reader-handson` でハンズオン影響を確認 → 問題なければ手動マージ」「書籍本文にバージョン記載があるなら authoring リポ側で `/update-lib-versions`」）

### Step 6: サマリー報告

会話（または `/schedule` の実行ログ）に報告：

- 🟢 マージ／修正した件数とパッケージ一覧
- 🟡 / 🔴 で Issue 化した件数と Issue URL
- 残課題（あれば）

## /schedule での運用

`/schedule` スキルで定期実行を登録できる（プロンプトに `/handle-dependabot` を指定）。無人実行時の挙動は固定：**🟢 は自動マージ・コミット、🟡/🔴 は Issue 通知のみ**。人間の判断が要る変更を勝手にマージすることはない。週次（毎週月曜 朝 など）が目安。

> ⚠️ このスキルファイル（`.claude/skills/handle-dependabot/SKILL.md`）は公開リポで `.gitignore` 除外されておりローカル限定。`/schedule` のリモート実行で確実に使うには、(a) 公開リポの `.gitignore` から `.claude/skills/` を外してコミットする、または (b) authoring リポ側に同等スキルを置いて運用する、のどちらかが必要。どちらにするかはみのるんと相談して決める（現状は (a)(b) どちらも未実施＝ローカル手動実行のみ動作）。

## 注意事項

- **🟢 以外は絶対に自動マージしない**。読者のハンズオンを壊すリスクがある変更は、必ず @minorun365 が `/verify-reader-handson` 等で確認してから手動マージする。
- `npm audit fix --force` は使わない（破壊的変更を伴う）。`--force` が必要なら 🟡 として Issue へ。
- `uv lock --upgrade`（パッケージ無指定の全体更新）は使わない。脆弱性のあるパッケージだけを `--upgrade-package` で狙い撃ちし、巻き添えの更新を最小化する。
- **原稿はライブラリのバージョンを固定している**。`pyproject.toml` / `package.json` の直接依存（＝原稿のコードブロックに出てくるパッケージ）を上げる変更は、原稿と公開リポを揃えて更新する必要があるため**このスキルでは絶対に勝手にやらない**。Issue で「authoring 側 `/update-lib-versions` で原稿のバージョン記載も更新 → 公開リポ側も追随」という対応案を提示し、@minorun365 の判断に委ねる。
- ロックファイルのみの変更は `coding-style.md` の対象外（自動生成物）。手書きの Python/TS は触らない。
- ハンズオン章（第2, 4, 13, 15章）の `package-lock.json` / `uv.lock` は「読者の手元と一致させる」方針。ロック更新コミット後、ファイルが消えていないことを確認する。
