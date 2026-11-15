"""Decode only visually verified embedded-font programs, never guessed glyphs."""
import ctypes
import hashlib
import pypdfium2 as pdfium

# RupeeForadian, verified against original TCS filing 038ef1c4…, PDF p.8.
# The name alone is insufficient: a different embedded font must fail closed.
RUPEE_FONTS={'9a18dab08e1c3851d9cd413c4fa453d1ce0346758c35e7c845d24763b782fa33'}


def decode_currency(textpage,text):
    if '`' not in text:return text,[]
    fonts={};matches=0
    for index in range(textpage.count_chars()):
        if pdfium.raw.FPDFText_GetUnicode(textpage,index)!=96:continue
        matches+=1
        obj=pdfium.raw.FPDFText_GetTextObject(textpage,index)
        font=pdfium.raw.FPDFTextObj_GetFont(obj) if obj else None
        if not font:return text,[]
        identity=ctypes.cast(font,ctypes.c_void_p).value
        if identity not in fonts:
            size=ctypes.c_ulonglong()
            if not pdfium.raw.FPDFFont_GetFontData(font,None,0,ctypes.byref(size)) or not 0<size.value<=1_000_000:return text,[]
            buffer=(ctypes.c_ubyte*size.value)()
            if not pdfium.raw.FPDFFont_GetFontData(font,buffer,size.value,ctypes.byref(size)):return text,[]
            fonts[identity]=hashlib.sha256(bytes(buffer)).hexdigest()
        if fonts[identity] not in RUPEE_FONTS:return text,[]
    # Bounded text and raw character streams must agree. A mixed-font backtick
    # or a filtered/reordered character cannot silently receive this mapping.
    if matches!=text.count('`'):return text,[]
    return text.replace('`','₹'),[{'font_hash':digest,'from_codepoint':96,'to_codepoint':8377} for digest in sorted(set(fonts.values()))]
