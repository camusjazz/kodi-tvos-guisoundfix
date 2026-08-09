# Kodi tvOS GUI音修正 — クラウドMacビルド

Mac実機なしで、GitHub ActionsのクラウドmacOSランナー上で
Kodi (tvOS) にGUI操作音の修正パッチを当ててビルドするための最小構成。

**このリポジトリがやること：ソースの取得 → パッチ適用 → コンパイル → 未署名の`.ipa`を出力**
**このリポジトリがやらないこと：署名・AppleTVへのインストール**
　→ 署名とインストールは、これまで使ってきたWindows側の手順
　（Payload編集→7-Zip圧縮→`.ipa`リネーム→サイドロード）にそのまま渡す。
　公式ビルドシステムが吐き出す`.ipa`は最初から未署名なので、この分担で問題ない。

## セットアップ手順

1. GitHubで新しい空のリポジトリを作成する（Public/Privateどちらでも可）
2. このフォルダの中身（`.github/`と`scripts/`）をそのリポジトリにそのままpushする
   ```
   git init
   git add .
   git commit -m "add kodi tvos build workflow"
   git branch -M main
   git remote add origin https://github.com/<あなたのアカウント>/<リポジトリ名>.git
   git push -u origin main
   ```
3. GitHubのリポジトリページ → **Actions** タブを開く
4. 左側の **Build Kodi tvOS (GUI sound fix)** を選択
5. 右側の **Run workflow** ボタンを押す（`xbmc_ref`は空欄なら`master`が使われる）
6. 実行が終わるまで待つ（**初回は依存関係のフルビルドが入るため、数時間かかる可能性があります**）
7. 完了したら実行結果のページ下部 **Artifacts** から `kodi-tvos-guisoundfix-ipa` をダウンロード
8. 中身の`.ipa`を、これまでの `C:\Users\saka-\Downloads\KodiWork2` の手順に差し替えて
   サイドロード・動作確認

## 正直に共有しておきたい不確実な点

- **KeyHandler.cppの現在の中身を実際には確認できていません。** パッチの根拠は
  GitHub Issue #27184 で報告されている、Kodi 21.2 (Omega) で動作確認済みの修正内容です。
  スクリプトは目印の行が見つからない場合エラーで止まる作りにしていますが、
  もし止まった場合は下記URLで現在のコードを見て手動調整が必要です。
  https://github.com/xbmc/xbmc/blob/master/xbmc/input/keymaps/generic/KeyHandler.cpp
- **公式ドキュメントはXcode 12.4/Catalina または 13.x/Montereyでのみ動作確認**と明記しています。
  GitHub Actionsの`macos-15`ランナーはこれよりかなり新しいXcodeが載っているため、
  古いビルドスクリプトが新しいXcode/Clangで警告・エラーになる可能性はゼロではありません。
  失敗した場合はエラーメッセージを見ながら一緒に調整しましょう。
- **無料枠のmacOSランナー分数（月2,000分だが10倍消費）を、初回のフルビルドだけで
  使い切ってしまう可能性があります。** 2回目以降は依存関係のキャッシュが効くので
  短くなる見込みですが、保証はできません。

## 対策が的外れだった場合の切り分け

このパッチはKodiが「ジョイスティック」として認識する入力機器のGUI音不具合を狙ったものです。
Siri Remoteとキーボードの両方で無音という今回の症状は、この不具合の報告範囲より広いため、
本格ビルド前に、デバッグログを有効にした状態でボタンを押した直後のログを一度見せてもらえると、
「Joystick」として処理されているかどうかを確認でき、無駄なビルド時間を避けられます。
