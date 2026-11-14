"""Isolated, incremental PDF parser. stdout is a page stream, never a log."""
import json
import sys
from pypdf import PdfReader

def main():
    if sys.platform != 'win32':
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(350*1024*1024,350*1024*1024))
    reader=PdfReader(sys.argv[1],strict=False)
    if reader.is_encrypted: raise ValueError('encrypted_pdf')
    if len(reader.pages)>500: raise ValueError('page_limit')
    for n,page in enumerate(reader.pages,1):
        text=page.extract_text() or ''
        if len(text)>180_000: raise ValueError('page_text_limit')
        print(json.dumps({'page':n,'text':text}),flush=True)

if __name__=='__main__':
    try: main()
    except Exception as e:
        # No document contents, paths, secrets or exception payloads in logs.
        print(type(e).__name__,file=sys.stderr)
        sys.exit(1)

