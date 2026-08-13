# Kodi tvOS — GUI操作音の修正版ビルド

Mac実機なしで、GitHub ActionsのクラウドmacOSランナー上でKodi (tvOS) をビルドし、
AppleTVでGUI操作音が鳴らない問題を修正するための構成。

## 解決した問題

tvOSのKodiでは、メニュー操作時のGUI音が一切鳴らない（動画の音声は正常）。
設定は全て正しく、sounds.xmlも読み込まれているのに無音のままだった。

## 原因

Kodiは `CInputManager::OnKey()` の中でのみ `PlayActionSound()` を呼んでいる。
しかしtvOSのSiri Remote入力はこの経路を通らないため、
**「音を鳴らせ」という命令自体が一度も発行されていなかった。**

診断用ログを埋め込んだビルドで、ボタンを何度押しても
`PlayActionSound` が一度も呼ばれないことを確認して特定した。

## 修正内容

`scripts/patch_onaction.py` が `CApplication::OnAction()` に
`PlayActionSound()` の呼び出しを追加する。ここは全てのアクションが通る場所。

## 使い方

Actionsタブ → Run workflow → `xbmc_ref` に `21.3-Omega` を入力して実行。
完了後、Artifactsから未署名の `.ipa` をダウンロードする。
署名とインストールは別途（atvloadly等を使用）。

## Xcode 16.4 と 21.3-Omega の互換性対応

ビルドを通すために、以下の既知の問題を回避している。

| 対象 | 問題 | 対処 |
|------|------|------|
| zlib | `TARGET_OS_MAC` の誤発動で `fdopen` がApple公式ヘッダと衝突 | 該当行を削除 |
| libpng | 同上で古い `<fp.h>` を読もうとする | 条件式から `TARGET_OS_MAC` を除去 |
| libffi | Clang 17以降でCFI疑似命令が通らない | `ffi_cfi.h` でCFI出力を無効化 |
| Kodi本体 | `TVOSNSUserDefaults.h` に `#include <vector>` が不足 | includeを追加 |

依存関係は「パッチ→ビルド」を成功するまで繰り返す方式で処理している
（ソースは順次展開されるため、一度のパッチでは行き渡らないため）。

## 注意

- 公式IPAに同梱されているバイナリアドオン（pvr.*, vfs.*, inputstream.* 等）は含まれない
- 依存関係は `--enable-debug=no` でリリースビルドしている
