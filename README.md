# Buzz Lab Dashboard

Google Sheetsと連携した行動管理ダッシュボードアプリです。

## セットアップ手順

### 1. Python環境の準備

仮想環境（venv）の使用を推奨します。

```bash
# 仮想環境の作成
python3 -m venv .venv

# 仮想環境の有効化（Mac/Linux）
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 2. VS Codeの設定

このプロジェクトフォルダをVS Codeで開くと、推奨拡張機能（Python, Jinjaなど）のインストールを促すポップアップが表示されますので、「インストール」を選択してください。

- **Formatter**: Blackを使用するように設定済みです（保存時に自動整形）。
- **Debugging**: `F5` キーを押すと、「Python: Flask」構成でアプリがデバッグモードで起動します。

### 3. Google Sheets連携

`credentials.json` がプロジェクトルートに配置されていることを確認してください。
このファイルにはGoogle Service Accountの認証情報が含まれています。

## アプリの起動

VS Codeのターミナル、またはコマンドラインで以下を実行します：

```bash
python3 app.py
```

ブラウザで `http://localhost:8081` にアクセスしてください。

## 機能概要

- **行動管理シートとの同期**: スプレッドシートの「行動管理」シートからタスクを読み込みます。
- **ステータス管理**: ダッシュボード上で「未着手」「進行中」「完了」を変更すると、スプレッドシートに即座に反映されます。
- **週次表示**: タスクは「Week1」「Week2」などの週ごとにグループ化されます。
