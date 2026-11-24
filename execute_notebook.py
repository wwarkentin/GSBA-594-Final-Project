"""Execute this project's plain Python cells and capture rich outputs, without a kernel.
For interactive use, open the notebook in Jupyter instead. No magics are supported.
"""
from pathlib import Path
import base64
import contextlib
import io
import json
import os
import traceback

ROOT=Path(__file__).resolve().parent

def execute():
    path=ROOT/'Peloton_Analysis.ipynb'
    notebook=json.loads(path.read_text())
    namespace={'__name__':'__main__'}
    counter=0
    original=Path.cwd()
    os.chdir(ROOT)
    try:
        for cell in notebook['cells']:
            if cell['cell_type']!='code':continue
            counter+=1;outputs=[]
            def display(value):
                if hasattr(value,'_repr_png_'):
                    png=value._repr_png_()
                    if isinstance(png,tuple):png=png[0]
                    if png:
                        encoded = png if isinstance(png,str) else base64.b64encode(png).decode()
                        outputs.append({'output_type':'display_data','metadata':{},'data':{'image/png':encoded}})
                        return
                if hasattr(value,'_repr_html_'):
                    html=value._repr_html_()
                    if html:
                        outputs.append({'output_type':'display_data','metadata':{},'data':{'text/html':html,'text/plain':repr(value)}})
                        return
                outputs.append({'output_type':'display_data','metadata':{},'data':{'text/plain':str(value)}})
            namespace['display']=display
            stream=io.StringIO()
            try:
                with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
                    exec(compile(''.join(cell['source']),f'notebook-cell-{counter}','exec'),namespace)
            except Exception:
                print(traceback.format_exc());raise
            if stream.getvalue():outputs.insert(0,{'output_type':'stream','name':'stdout','text':stream.getvalue()})
            cell['outputs']=outputs;cell['execution_count']=counter
        path.write_text(json.dumps(notebook,indent=2))
        print(f'Executed {counter} notebook code cells successfully.')
    finally:os.chdir(original)

if __name__=='__main__':execute()
