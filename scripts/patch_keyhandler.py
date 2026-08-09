#!/usr/bin/env python3
"""
Kodi の KeyHandler.cpp に GUI操作音再生の呼び出しを追加するパッチスクリプト。

出典: https://github.com/xbmc/xbmc/issues/27184
      「Possible fix for missing gui sound with joystick」
      Kodi 21.2 (Omega) で動作確認済みと報告されている修正。

このスクリプトは “dispatchAction = guiAction;” という行を目印にして
その直後に3行を追加する。目印が見つからない場合は、Kodi側のコードが
変わっている可能性があるため、黙って失敗せずエラーで止まる。
その場合は GitHub の現在の KeyHandler.cpp を見て手動で当て直してほしい。

使い方: python3 patch_keyhandler.py <kodiリポジトリのパス>
"""

import sys
import pathlib

RELATIVE_PATH = "xbmc/input/keymaps/generic/KeyHandler.cpp"

ANCHOR = "dispatchAction = guiAction;"

ADDED_LINES = """dispatchAction = guiAction;
    CGUIComponent* gui = CServiceBroker::GetGUI(); // ADDED (GUI sound fix)
    if (gui) // ADDED (GUI sound fix)
      gui->GetAudioManager().PlayActionSound(guiAction); // ADDED (GUI sound fix)"""

INCLUDE_LINES = [
    '#include "ServiceBroker.h"',
    '#include "guilib/GUIAudioManager.h"',
]


def main() -> int:
    if len(sys.argv) != 2:
        print("使い方: python3 patch_keyhandler.py <kodiリポジトリのパス>", file=sys.stderr)
        return 1

    repo_root = pathlib.Path(sys.argv[1])
    target = repo_root / RELATIVE_PATH

    if not target.exists():
        print(
            f"ERROR: {target} が見つかりません。\n"
            "Kodiのバージョンによってファイルの場所が変わっている可能性があります。\n"
            "(旧バージョンでは xbmc/input/joysticks/keymaps/KeyHandler.cpp でした)",
            file=sys.stderr,
        )
        return 1

    text = target.read_text(encoding="utf-8")

    if "PlayActionSound(guiAction)" in text:
        print("既にパッチ適用済みのようです。スキップします。")
        return 0

    if ANCHOR not in text:
        print(
            f"ERROR: 目印の行 '{ANCHOR}' が {target} 内に見つかりませんでした。\n"
            "Kodi本体のコードが変わっている可能性があります。\n"
            "GitHubで現在のファイルを開いて、CKeyHandler::ProcessAction() 内を\n"
            "手動で確認・修正してください:\n"
            "  https://github.com/xbmc/xbmc/blob/master/xbmc/input/keymaps/generic/KeyHandler.cpp",
            file=sys.stderr,
        )
        return 1

    if text.count(ANCHOR) != 1:
        print(
            f"ERROR: 目印の行 '{ANCHOR}' が複数箇所に見つかりました。"
            "自動パッチは安全のため中止します。手動で確認してください。",
            file=sys.stderr,
        )
        return 1

    text = text.replace(ANCHOR, ADDED_LINES, 1)

    lines = text.split("\n")
    if not any(line.strip() == INCLUDE_LINES[0] for line in lines):
        for i, line in enumerate(lines):
            if line.startswith("#include"):
                lines[i:i] = INCLUDE_LINES
                break
        else:
            print("ERROR: #include 行が1つも見つからず、インクルードを追加できませんでした。", file=sys.stderr)
            return 1
        text = "\n".join(lines)

    target.write_text(text, encoding="utf-8")
    print(f"パッチを適用しました: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
