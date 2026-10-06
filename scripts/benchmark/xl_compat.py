import re, openpyxl
from openpyxl.worksheet.formula import ArrayFormula
def split_args(s):
    out=[];depth=0;cur='';q=False;br=0
    for ch in s:
        if ch=='"': q=not q
        if not q:
            if ch=='(':depth+=1
            elif ch==')':depth-=1
            elif ch=='[':br+=1
            elif ch==']':br-=1
            elif ch==',' and depth==0 and br==0:
                out.append(cur);cur='';continue
        cur+=ch
    out.append(cur);return out
def conv(f):
    key='_xlfn.XLOOKUP('
    while key in f:
        i=f.index(key);j=i+len(key);depth=1;q=False;k=j
        while depth>0:
            ch=f[k]
            if ch=='"':q=not q
            if not q:
                if ch=='(':depth+=1
                elif ch==')':depth-=1
            k+=1
        a=split_args(f[j:k-1])
        core=f"INDEX({a[2]},MATCH({a[0]},{a[1]},0))"
        if len(a)>3 and a[3].strip()!='': core=f"IFERROR({core},{a[3]})"
        f=f[:i]+core+f[k:]
    return f
def make_verify_copy(src,dst):
    wb=openpyxl.load_workbook(src)
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                v=c.value
                if isinstance(v,ArrayFormula):
                    v.text=conv(v.text)
                elif isinstance(v,str) and v.startswith('='):
                    c.value=conv(v)
    wb.save(dst)
