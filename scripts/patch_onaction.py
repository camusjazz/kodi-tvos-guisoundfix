import pathlib, re, sys

src = pathlib.Path.home() / "kodi" / "xbmc" / "application" / "Application.cpp"
if not src.exists():
    sys.exit("ERROR: not found: %s" % src)

text = src.read_text(encoding="utf-8")
if "GUISOUND-ONACTION" in text:
    print("already patched"); sys.exit(0)

i = text.index("#include")
e = text.index("\n", i) + 1
text = (text[:e]
        + '#include "ServiceBroker.h"\n'
        + '#include "guilib/GUIComponent.h"\n'
        + '#include "guilib/GUIAudioManager.h"\n'
        + '#include "utils/log.h"\n'
        + text[e:])

m = re.search(r"bool\s+CApplication::OnAction\s*\(\s*const\s+CAction\s*&\s*(\w+)\s*\)\s*\{", text)
if not m:
    sys.exit("ERROR: CApplication::OnAction not found")
p = m.group(1)

code = ('\n  {  // GUISOUND-ONACTION\n'
        '    CGUIComponent* guiComp = CServiceBroker::GetGUI();\n'
        '    if (guiComp)\n'
        '    {\n'
        '      CLog::Log(LOGINFO, "GUISOUND-ONACTION: id={}", %s.GetID());\n'
        '      guiComp->GetAudioManager().PlayActionSound(%s);\n'
        '    }\n'
        '  }\n' % (p, p))

text = text[:m.end()] + code + text[m.end():]
src.write_text(text, encoding="utf-8")
print("patched CApplication::OnAction OK")
