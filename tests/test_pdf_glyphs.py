import ctypes
import hashlib
from types import SimpleNamespace
from backend import pdf_glyphs


def mock_page(monkeypatch, font_ids=(1, 1), raw_count=2):
    programs={1:b'verified-font-program',2:b'unknown-font-program'}
    monkeypatch.setattr(pdf_glyphs,'RUPEE_FONTS',{hashlib.sha256(programs[1]).hexdigest()})
    raw=pdf_glyphs.pdfium.raw
    monkeypatch.setattr(raw,'FPDFText_GetUnicode',lambda page,index:96)
    monkeypatch.setattr(raw,'FPDFText_GetTextObject',lambda page,index:index+1)
    monkeypatch.setattr(raw,'FPDFTextObj_GetFont',lambda obj:ctypes.c_void_p(font_ids[obj-1]))
    def font_data(font,buffer,length,size):
        data=programs[font.value]
        ctypes.cast(size,ctypes.POINTER(ctypes.c_ulonglong))[0]=len(data)
        if buffer is not None:
            for i,value in enumerate(data):buffer[i]=value
        return True
    monkeypatch.setattr(raw,'FPDFFont_GetFontData',font_data)
    return SimpleNamespace(count_chars=lambda:raw_count)


def test_currency_mapping_requires_exact_font_program_and_records_provenance(monkeypatch):
    page=mock_page(monkeypatch)
    text,mappings=pdf_glyphs.decode_currency(page,'` crore; ` per share')
    assert text=='₹ crore; ₹ per share'
    assert mappings==[{'font_hash':next(iter(pdf_glyphs.RUPEE_FONTS)),'from_codepoint':96,'to_codepoint':8377}]


def test_mixed_font_or_bounded_character_count_mismatch_remains_unchanged(monkeypatch):
    page=mock_page(monkeypatch,(1,2))
    assert pdf_glyphs.decode_currency(page,'` crore; ` literal')==('` crore; ` literal',[])
    page=mock_page(monkeypatch)
    assert pdf_glyphs.decode_currency(page,'` crore')==('` crore',[])
    assert pdf_glyphs.decode_currency(page,'INR crore')==('INR crore',[])
