# Render デプロイガイド

このアプリを **Render** (https://render.com) にデプロイして、インターネット上で公開する手順です。
※Renderは無料プランで利用可能です。

## 事前準備

1.  **GitHubリポジトリの作成**:
    - このプロジェクトのコードをGitHubにプッシュしてください。
    - （まだの場合は、GitHubアカウント作成 -> New Repository -> コードのプッシュ を行ってください）

2.  **Renderアカウントの作成**:
    - [Render](https://render.com) にアクセスし、GitHubアカウントでログイン/登録します。

## デプロイ手順

1.  **New Web Service の作成**:
    - Renderのダッシュボードで「New +」ボタン -> 「Web Service」を選択。
    - GitHubリポジトリを連携し、今回のリポジトリ（Buzz Lab）を選択します。

2.  **設定項目の入力**:
    以下の通りに入力してください。

    | 項目 | 設定値 |
    |---|---|
    | **Name** | `buzz-lab-app` （任意の名前） |
    | **Region** | `Singapore` (近いので推奨) など |
    | **Branch** | `main` (または `master`) |
    | **Runtime** | `Python 3` |
    | **Build Command** | `pip install -r requirements.txt` |
    | **Start Command** | `gunicorn app:app` |
    | **Plan** | `Free` |

3.  **環境変数の設定 (重要)**:
    「Advanced」セクション、または作成後の「Environment」タブで以下の変数を追加します。

    - **Key**: `GOOGLE_CREDENTIALS`
    - **Value**: `credentials.json` の中身を**すべてコピーして貼り付け**てください。
      - ファイルの中身（`{ "type": "service_account", ... }`）を改行を含めてそのまま貼り付ければOKです。

4.  **デプロイ実行**:
    - 「Create Web Service」ボタンを押すと、デプロイが始まります。
    - 数分で完了し、`https://buzz-lab-app.onrender.com` のようなURLが発行されます。

## UTAGE / Notion への埋め込み

発行されたURL（例: `https://buzz-lab-app.onrender.com`）を使って埋め込みます。

- **UTAGE**: カスタムHTML要素に以下を入力
  ```html
  <iframe src="https://buzz-lab-app.onrender.com" width="100%" height="800px" style="border:none;"></iframe>
  ```
- **Notion**: `/embed` と入力し、URLを貼り付け。
