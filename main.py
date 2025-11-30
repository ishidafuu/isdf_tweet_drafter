#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice2Tweet Bot - Discord Bot for converting voice-input text to tweet-ready format
"""

import os
import logging
from urllib.parse import quote
from typing import Optional

import discord
from discord import ButtonStyle
from discord.ui import Button, View
from dotenv import load_dotenv
import google.generativeai as genai

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 環境変数のバリデーション
if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN が .env ファイルに設定されていません")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY が .env ファイルに設定されていません")

# Gemini API の設定
genai.configure(api_key=GEMINI_API_KEY)

# システムインストラクション（定数として管理）
SYSTEM_INSTRUCTION = """あなたはSNS投稿の編集アシスタントです。
ユーザーから入力されたテキスト（音声入力による乱雑なメモ）を、
X（旧Twitter）への投稿に適した形式にリライトしてください。

ルール:
1. 誤字脱字を修正し、自然な口語体にする。
2. 必ず140文字以内に収める。
3. ハッシュタグは付けない。
4. 絵文字を使用しない。
5. 結果のテキストのみを出力する（説明文は不要）。
"""

# Gemini モデルの初期化
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_INSTRUCTION
)

# Discord Intents の設定
intents = discord.Intents.default()
intents.message_content = True  # Message Content Intent を有効化（必須）

client = discord.Client(intents=intents)


class TweetButton(View):
    """Xアプリで開くボタンを提供するビュー"""

    def __init__(self, tweet_text: str):
        super().__init__(timeout=None)
        self.is_truncated = False

        # Discord のボタンURL最大長は512文字
        MAX_URL_LENGTH = 512
        BASE_URL = "https://twitter.com/intent/tweet?text="

        # URLエンコードして長さをチェック
        truncated_text = tweet_text
        encoded_text = quote(truncated_text)
        tweet_url = f"{BASE_URL}{encoded_text}"

        # URL長が制限を超える場合は段階的に短くする
        while len(tweet_url) > MAX_URL_LENGTH and len(truncated_text) > 0:
            # 10文字ずつ短くして再試行
            truncated_text = truncated_text[:-10].rstrip()
            if truncated_text:
                truncated_text += "…"  # 省略記号を追加
            encoded_text = quote(truncated_text)
            tweet_url = f"{BASE_URL}{encoded_text}"

        # 切り詰めが発生したかチェック
        if len(truncated_text) < len(tweet_text):
            self.is_truncated = True
            logger.warning(
                f"URL長制限のためボタンのテキストを切り詰めました: "
                f"{len(tweet_text)}文字 → {len(truncated_text)}文字"
            )
        else:
            logger.info(f"Twitter Intent URL生成成功 (長さ: {len(tweet_url)}文字)")

        # ボタンを常に追加（切り詰め後のテキストを使用）
        button = Button(
            label="Xアプリで開く",
            style=ButtonStyle.link,
            url=tweet_url,
            emoji="🐦"
        )
        self.add_item(button)


async def format_text_with_gemini(text: str) -> Optional[str]:
    """
    Gemini API を使ってテキストを整形する

    Args:
        text: 整形前のテキスト

    Returns:
        整形後のテキスト（エラー時は None）
    """
    try:
        logger.info(f"Gemini API にリクエスト送信: {text[:50]}...")
        response = model.generate_content(text)

        formatted_text = response.text.strip()
        logger.info(f"Gemini API レスポンス: {formatted_text}")

        # 140文字チェック
        if len(formatted_text) > 140:
            logger.warning(f"整形後のテキストが140文字を超えています: {len(formatted_text)}文字")
            # 再試行（より厳密な指示）
            retry_prompt = f"{text}\n\n（上記を140文字以内に要約してください）"
            response = model.generate_content(retry_prompt)
            formatted_text = response.text.strip()
            logger.info(f"再試行後のテキスト: {formatted_text} ({len(formatted_text)}文字)")

        return formatted_text

    except Exception as e:
        logger.error(f"Gemini API エラー: {e}")
        return None


@client.event
async def on_ready():
    """Bot 起動時のイベント"""
    logger.info(f'Bot がログインしました: {client.user.name} (ID: {client.user.id})')
    logger.info('------')


@client.event
async def on_message(message: discord.Message):
    """メッセージ受信時のイベント"""

    try:
        # Bot 自身のメッセージは無視（無限ループ防止）
        if message.author == client.user:
            return

        # 空メッセージのバリデーション
        if not message.content or not message.content.strip():
            logger.debug("空メッセージを受信したため無視")
            return

        # 特定チャンネル以外は無視
        if message.channel.name != "tweet-drafter":
            logger.debug(f"チャンネル '{message.channel.name}' はスキップ（tweet-drafter のみ対応）")
            return

        logger.info(f"メッセージ受信: {message.author.name}: {message.content[:50]}...")

        # 処理中リアクションを追加
        try:
            await message.add_reaction("⏳")
        except Exception as e:
            logger.warning(f"リアクション追加エラー: {e}")

        # Gemini API でテキストを整形
        formatted_text = await format_text_with_gemini(message.content)

        # 処理中リアクションを削除
        try:
            await message.remove_reaction("⏳", client.user)
        except Exception as e:
            logger.warning(f"リアクション削除エラー: {e}")

        # エラー処理
        if formatted_text is None:
            error_embed = discord.Embed(
                title="❌ エラーが発生しました",
                description="テキストの整形中にエラーが発生しました。もう一度お試しください。",
                color=discord.Color.red()
            )
            await message.channel.send(embed=error_embed)
            return

        # Discord Embed の作成
        embed = discord.Embed(
            title="✨ テキスト整形完了",
            color=discord.Color.blue()
        )

        # 整形前のテキスト（最初の100文字まで表示）
        original_preview = message.content[:100]
        if len(message.content) > 100:
            original_preview += "..."
        embed.add_field(
            name="📝 整形前",
            value=f"```{original_preview}```",
            inline=False
        )

        # 整形後のテキスト
        embed.add_field(
            name="🎯 整形後（投稿用）",
            value=formatted_text,
            inline=False
        )

        # 文字数カウント表示
        char_count = len(formatted_text)
        char_status = "✅" if char_count <= 140 else "⚠️"
        embed.add_field(
            name="📊 文字数",
            value=f"{char_status} {char_count} / 140 文字",
            inline=False
        )

        # ボタン付きで送信
        view = TweetButton(formatted_text)

        # 切り詰めの有無によってフッターを変更
        if view.is_truncated:
            embed.set_footer(text="⚠️ ボタンのテキストは一部省略されています。完全版は上記の「整形後」をコピーしてください")
        else:
            embed.set_footer(text="下のボタンをタップしてXアプリで投稿できます")

        await message.channel.send(embed=embed, view=view)

        # 完了リアクション
        try:
            await message.add_reaction("✅")
        except Exception as e:
            logger.warning(f"完了リアクション追加エラー: {e}")

    except Exception as e:
        # 予期しないエラーをキャッチして Discord に通知
        logger.error(f"on_message で予期しないエラーが発生: {e}", exc_info=True)
        try:
            error_embed = discord.Embed(
                title="❌ システムエラーが発生しました",
                description=f"予期しないエラーが発生しました。管理者に連絡してください。\n\n```{str(e)}```",
                color=discord.Color.red()
            )
            await message.channel.send(embed=error_embed)
        except Exception as send_error:
            logger.error(f"エラーメッセージの送信にも失敗: {send_error}")


def main():
    """メイン関数"""
    try:
        logger.info("Bot を起動しています...")
        client.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Bot の起動に失敗しました: {e}")
        raise


if __name__ == "__main__":
    main()
