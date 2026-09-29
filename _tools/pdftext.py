import sys, fitz
pdf = sys.argv[1]
doc = fitz.open(pdf)
print("PAGES: %d" % len(doc))
for i, page in enumerate(doc):
    print("=== PAGE %d ===" % (i + 1))
    print(page.get_text().rstrip())
