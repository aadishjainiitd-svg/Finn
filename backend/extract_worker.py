"""Isolated, incremental PDF parser. stdout is a page stream, never a log."""
import json
import sys
import pypdfium2 as pdfium

def main():
    if sys.platform != 'win32':
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(350*1024*1024,350*1024*1024))
    reader=pdfium.PdfDocument(sys.argv[1])
    try:
        if len(reader)>500: raise ValueError('page_limit')
        for index in range(len(reader)):
            page=reader[index]
            try:
                textpage=page.get_textpage()
                try:text=textpage.get_text_bounded()
                finally:textpage.close()
                if len(text)>180_000: raise ValueError('page_text_limit')
                print(json.dumps({'page':index+1,'text':text}),flush=True)
            finally:page.close()
    finally:reader.close()

if __name__=='__main__':
    try: main()
    except Exception as e:
        # No document contents, paths, secrets or exception payloads in logs.
        print(type(e).__name__,file=sys.stderr)
        sys.exit(1)

