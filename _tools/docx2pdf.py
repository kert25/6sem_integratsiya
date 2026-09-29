# -*- coding: utf-8 -*-
"""docx -> pdf через MS Word COM: py docx2pdf.py <in.docx> <out.pdf>"""
import sys, os

def main():
    src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    import win32com.client  # pywin32
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(src, ReadOnly=True)
        doc.SaveAs2(dst, FileFormat=17)
        doc.Close(False)
    finally:
        word.Quit()
    print("OK %s (%d b)" % (dst, os.path.getsize(dst)))

main()
