# -*- coding: utf-8 -*-
"""Выгрузка текста из docx: py extract_docx.py <N> — методичка из папки ЛРN,
либо py extract_docx.py <путь/ASCII>.docx — конкретный файл.
Кириллические пути внутри скрипта (\\u-эскейпы), командная строка остаётся ASCII."""
import sys, os, re, zipfile

def extract(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    xml = re.sub(r"<w:tab[^>]*/>", "\t", xml)
    xml = xml.replace("</w:tc>", " | ")
    xml = xml.replace("</w:tr>", "\n")
    xml = re.sub(r"<w:p [^>]*>|<w:p>", "\n", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    txt = (xml.replace("&amp;", "&").replace("&lt;", "<")
             .replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'"))
    lines = [ln.rstrip() for ln in txt.splitlines()]
    return "\n".join(ln for ln in lines if ln.strip())

if __name__ == "__main__":
    arg = sys.argv[1]
    if arg.endswith(".docx"):
        path = arg
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lab = os.path.join(root, "\u041b\u0420" + arg)
        cands = [f for f in os.listdir(lab) if f.lower().endswith(".docx")]
        path = os.path.join(lab, cands[0])
    sys.stdout.reconfigure(encoding="utf-8")
    print("FILE:", os.path.basename(path))
    print(extract(path))
