# 🐦 Voice2Tweet Bot

スマホの音声入力で書き殴ったテキストを、Gemini APIを用いてツイート用に整形し、ワンタップでX（旧Twitter）アプリを開いて投稿できるボタンを提供する Discord Bot です。

![Status](https://img.shields.io/badge/status-準備完了-yellow)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ 特徴

- **音声入力対応**: スマホの音声入力で書いたテキストを自動整形
- **AI整形**: Gemini 1.5 Flash で誤字修正・要約（140字以内）
- **ワンタップ投稿**: Discordのボタンから直接Xアプリを起動
- **シンプル構成**: 単一ファイル（main.py）で完結

---

## 🎯 使い方

### 1. Bot にメッセージを送る
Discordで音声入力を使ってメッセージを送信します。

例:
```
えーと今日はですね、すごく良い天気だったのでですね、
散歩に行ってきたんですけど、桜がきれいでした
```

### 2. 整形結果を確認
Botが自動でテキストを整形して返信します。

整形後:
```
今日は良い天気だったので散歩に行ってきました！
桜がきれいでした🌸
```

### 3. ボタンをタップ
「Xアプリで開く」ボタンをタップすると、Xアプリが起動し、整形済みのテキストが入力された状態で開きます。

---

## 🚀 セットアップ

### 必要なもの
- Python 3.10 以上
- Discord Bot Token
- Google Gemini API Key

### インストール手順

#### 1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/isdf_tweet_drafter.git
cd isdf_tweet_drafter
```

#### 2. 仮想環境を作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

#### 4. 環境変数を設定
`.env.example` をコピーして `.env` を作成し、APIキーを設定します。

```bash
cp .env.example .env
```

`.env` ファイルを編集:
```env
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 5. Bot を起動
```bash
python main.py
```

---

## 🔑 API キーの取得方法

### Discord Bot Token
1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. 左メニューの「Bot」→「Add Bot」
4. **重要**: 「Privileged Gateway Intents」で「Message Content Intent」を有効化
5. 「Reset Token」→「Copy」でトークンを取得
6. 「OAuth2」→「URL Generator」でBotをサーバーに招待

### Google Gemini API Key
1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. 「Create API Key」をクリック
3. API Keyをコピー

---

## 📁 プロジェクト構成

```
isdf_tweet_drafter/
├── .env                  # 環境変数（Git管理対象外）
├── .env.example          # 環境変数テンプレート
├── .gitignore            # Git除外設定
├── requirements.txt      # Pythonパッケージ
├── main.py               # メインロジック（未実装）
├── README.md             # 本ファイル
├── REQUIREMENTS.md       # 詳細な要件定義書
├── IMPLEMENTATION_PLAN.md # 実装手順書
└── CLAUDE.md             # Claude Code用コンテキスト
```

---

## 📋 ドキュメント

- **[REQUIREMENTS.md](REQUIREMENTS.md)**: 詳細な要件定義書
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)**: ステップバイステップの実装手順
- **[CLAUDE.md](CLAUDE.md)**: プロジェクト全体のコンテキスト（AI開発用）

---

## 🛠️ 技術スタック

- **言語**: Python 3.10+
- **ライブラリ**:
  - `discord.py` - Discord Bot フレームワーク
  - `google-generativeai` - Gemini API クライアント
  - `python-dotenv` - 環境変数管理

---

## 🔧 トラブルシューティング

### Bot が起動しない
- `.env` ファイルが存在するか確認
- Python バージョンが 3.10 以上か確認

### メッセージを受信しない
- Discord Developer Portal で「Message Content Intent」が有効か確認
- Bot がサーバーに招待されているか確認

### Gemini API エラー
- API Key が正しいか確認
- Google AI Studio でクォータ制限を確認

詳細は [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) のトラブルシューティングセクションを参照してください。

---

## 🎯 MVP（最小実用製品）の成功基準

- [ ] Discord でメッセージを受信できる
- [ ] Gemini API でテキストが整形される
- [ ] 整形結果が Discord Embed で表示される
- [ ] ボタンクリックで X アプリが開く
- [ ] 整形後のテキストが 140 字以内に収まる

---

## 📝 今後の拡張予定

- [ ] 複数のトーン（フォーマル/カジュアル）選択機能
- [ ] 投稿履歴の保存
- [ ] 画像添付機能
- [ ] スレッド形式での複数案の提示
- [ ] 他のSNS（Instagram, Facebook）への対応

---

## 📄 ライセンス

MIT License

---

## 🤝 コントリビューション

現在は個人プロジェクトのため、コントリビューションは受け付けていません。

---

## 📞 お問い合わせ

問題が発生した場合は、Issue を作成してください。

---

**最終更新**: 2025-11-30
**ステータス**: 🟡 準備完了・実装待ち
