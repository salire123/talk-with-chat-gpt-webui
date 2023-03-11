# ## J2Py - Python <=> Jupyter utility script
# run this script to convert easily and reversably scripts and notebooks, while keeping the formatted cells, comments and outputs
# ### j2py
# - build shebangs from python version info
# ### GUI
# -   add icon
# -   add confirmation button if a file is going to be overwritten

import sys
import re
import random as rnd
import json
from copy import deepcopy
from pathlib import Path
from hashlib import md5

TITLE = r"""
   ___  ______      
  |_  | | ___ \     
    | | | |_/ /   _ 
    | |2|  __/ | | |
/\__/ / | |  | |_| |
\____/  \_|   \__, |
               __/ |
              |___/ 
"""

__all__ = [
    'TITLE',
    'OPTIONS',
    'py2j',
    'j2py',
    'guimode',
    'main',
]


class reg():
    """Store here all the regexes used in the script"""
    blank = r"^\s*$"
    code_separator = r"^# In\[([\d\s]*)\]:?.*"
    markdown = r"# (#.*\n)"
    simplecomment = r"# (.*)"
    scriptrow = r"^(\s*)(.+)$"
    start = r"(#.*!\/usr\/.*)|# coding.*|^$"


OPTIONS = {
    'noisy': True,
    'overwrite': False,
    'j2p': {
        'delete_markdown': False,  # ignore markdown
        # 'delete_raw': True,  # NA
        # 'keep_outputs': False,  # NA
        'keep_separators': True,  # No paste separators
    },
    'p2j': {
        'blank_separators': False,  # use blank rows to separate cells
        'in_separators': True,  # use In[ ] to separate code
        'markdown_separators': True,  # use # #text to separate markdown
    }
}

script_cell_template = {
    "cell_type": "",  # code, markdown or raw
    "execution_count": None,
    "id": "",
    "metadata": {},
    "outputs": [],
    "source": []
}

notebook_info = {
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": sys.version_info.major
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}


def p(*args, **kwargs):
    if OPTIONS['noisy']:
        print(*args, **kwargs)


def pairwise(ls):
    it = iter(ls)
    for el in it:
        yield el, next(it)


def gen_id(chars: str = "abcdefghijklmnopqrstuvwxyz0123456789",
           lens: list = [8, 4, 4, 4, 12], sep: str = "-"):
    """Not sure if it actually works"""
    return sep.join("".join(rnd.choice(chars) for i in range(l)) for l in lens)


def convert_name(s):
    if '.ipynb' in s:
        return s.replace('.ipynb', '.py')
    elif '.py' in s:
        return s.replace('.py', '.ipynb')
    else:
        raise BaseException(
            f"{s} not recognized among the possible file types - py or ipynb")


def fixrow(s):
    '''add a newline at the end of a row, if missing'''
    if s == '' or s is None:
        return '\n'
    if s[-1] != '\n':
        return s + '\n'
    return s


def py2j(dir_input: str, dir_output: str) -> str:
    p(dir_input, '->', dir_output)
    with open(dir_input) as py:
        rows = py.readlines()
        iterrows = iter(rows)

    split_cells = []
    cur = deepcopy(script_cell_template)  # cur is a single Jupyter cell
    cur['id'] = gen_id()
    cur['cell_type'] = 'code'
    cur['source'] = []
    start = True
    for row in iterrows:
        # if a cell at the beginning contains only comments, transform it into a markdown cell
        # ignore all beginning rows containing shebangs (for now, TODO improve using the info for the script itself?)
        if start:
            if re.match(reg.start, row):
                continue
            else:
                start = False
        # check if the rows contain the console separator '# In[int]:', or a markdown title separator '# #something'
        space_sep = re.match(reg.blank, row)
        # when a blank space is encountered, iterate next cells and evaluate whether the next one is a valid py script
        if space_sep and OPTIONS['p2j']['blank_separators']:
            temp = ['\n']
            for temprow in iterrows:
                if re.match(reg.blank, temprow):
                    temp.append(temprow)
                else:
                    # TODO duplicate match definition. not soo good
                    rowmatch = re.match(reg.scriptrow, temprow).groups()
                    if rowmatch[0] == '':
                        # all the past rows are just blank and not part of a func/class
                        # a new cell is created here
                        if cur['source']:
                            split_cells.append(cur)
                        cur = deepcopy(script_cell_template)
                        cur['id'] = gen_id()
                        cur['cell_type'] = 'code'
                    cur['source'].extend(temp)
                    break
            row = temprow
            # p(temprow
        cell_sep = re.match(reg.code_separator, row)
        mkdn_sep = re.match(reg.markdown, row)
        # when a cell separator is hit, split_cells gets updated and a new cell is generated
        if cell_sep and OPTIONS['p2j']['in_separators']:
            if cur['source']:
                split_cells.append(cur)
            cur = deepcopy(script_cell_template)
            cur['id'] = gen_id()
            cur['cell_type'] = 'code'
            cur['execution_count'] = cell_sep[1] if cell_sep[1] != ' ' else None
            continue
        # when a markdown separator is hit, a new cell is generated only if the current one isn't already a md cell
        elif mkdn_sep and cur['cell_type'] != 'markdown' and OPTIONS['p2j']['markdown_separators']:
            if cur['source']:
                split_cells.append(cur)
            cur = deepcopy(script_cell_template)
            cur['id'] = gen_id()
            cur['cell_type'] = 'markdown'
            cur['source'].append(mkdn_sep[1])
            # p(repr(mkdn_sep[1]), repr(mkdn_sep), repr(row))
        else:
            if cur['cell_type'] != 'markdown':
                cur['source'].append(row)
            else:
                try:
                    cur['source'].append(re.match(reg.simplecomment, row)[1])
                except:
                    cur['source'].append(row)
            # p('--added', repr(row), end='\n')
    else:
        split_cells.append(cur)

    # final json output
    json_output = {
        "cells": split_cells,
        **notebook_info
    }

    return savefile(dir_output, json.dumps(json_output, indent=True))


def j2py(dir_input: str, dir_output: str) -> str:
    p(dir_input, '->', dir_output)
    with open(dir_input) as nb:
        nb_dict = json.loads(nb.read())
    cells: list = nb_dict['cells']
    cell_rows = []
    for cell in cells:
        if cell['cell_type'] == 'code':
            exec_count = cell.get('execution_count', None)
            exec_count = exec_count if exec_count else ' '
            if OPTIONS['j2p']['keep_separators']:
                cell_rows.append(f"# In[{exec_count}]:\n")
            for row in cell.get('source', []):
                cell_rows.append(fixrow(row))
        elif cell['cell_type'] in ('markdown', 'raw'):
            if not OPTIONS['j2p']['delete_markdown']:
                for row in cell.get('source', []):
                    cell_rows.append(f"# {fixrow(row)}")
        else:
            raise BaseException(f'Unrecognized cell type: {cell["cell_type"]}')

    return savefile(dir_output, ''.join(cell_rows))


def runconversion(dir_input: str, dir_output: str) -> str:
    p(f"Script conversion started")
    p(f"{repr(dir_input)} --> {repr(dir_output)}")

    if dir_input.endswith('.py') and dir_output.endswith('.ipynb'):
        out = py2j(dir_input, dir_output)
    elif dir_input.endswith('.ipynb') and dir_output.endswith('.py'):
        out = j2py(dir_input, dir_output)
    elif re.search(r"(\.ipynb$|\.py$)", dir_input) and dir_output == '':
        out = runconversion(dir_input, convert_name(dir_input))
    else:
        raise Exception(
            f"Invalid names for conversion: '{dir_input}' and '{dir_output}'")
    return "File converted" if out else "File not converted"


def savefile(dir_output, filecontent):
    """Returns
    True if the file was saved
    False in case the file the file exists and overwrite disabled"""
    opt = 'w' if OPTIONS['overwrite'] else 'x'
    with open(dir_output, opt) as out_file:
        out_file.write(filecontent)
        p(f"saved to file {dir_output}")
    return True


def breakstr(s, cols=45):
    return '\n'.join(s[i:i+cols] for i in range(0, len(s), cols))


def samedata(f0: str, f1: str) -> bool:
    """Checks the content of two strings, returning true if they are not updated"""
    h0 = md5(f0.encode()).hexdigest()
    h1 = md5(f1.encode()).hexdigest()
    return h0 == h1


def guimode():
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename, askdirectory

    # configure UI
    gui = tk.Tk()
    gui.resizable(True, True)
    gui.title("J2Py")
    gui.rowconfigure(0, weight=10)
    gui.columnconfigure(0, weight=10)

    # input
    inputframe = ttk.Frame(gui, height=10, width=10,
                           padding="3 3 20 20")
    inputframe.grid(column=0, row=0, sticky="nw")
    inputvalue = tk.StringVar(master=inputframe)
    inputtext = ttk.Entry(inputframe, width=50,
                          textvariable=inputvalue)
    inputtext.grid(column=1, row=0, sticky='nwe')
    inputbutton = ttk.Button(inputframe, text="Input file",
                             command=lambda: openfile('in'))
    inputbutton.grid(column=0, row=0)
    # output
    outputvalue = tk.StringVar(master=inputframe)
    outputtext = ttk.Entry(inputframe, width=50,
                           textvariable=outputvalue)
    outputtext.grid(column=1, row=1, sticky='nwe')
    outputbutton = ttk.Button(inputframe, text="Output file",
                              command=lambda: openfile('out'))
    outputbutton.grid(column=0, row=1)
    # run button
    runbutton = ttk.Button(inputframe, text="Convert",
                           command=lambda: inner_run())
    runbutton.grid(column=0, row=2, sticky="nw")
    # status information
    status = tk.Label(inputframe, width=50,
                      text="Status Information", anchor='w')
    status.grid(column=0, row=3, columnspan=2, sticky='ew')

    # option buttons - global, p2j and j2p
    overwrite = tk.BooleanVar(value=OPTIONS['overwrite'])
    tk.Checkbutton(inputframe, text="Overwrite if file exists",
                   variable=overwrite,
                   onvalue=True, offvalue=False).grid(column=1, row=2, sticky='nw')
    overwrite.trace_add(mode='write',
                        callback=lambda x, y, z: refresh_options())

    p2jboxes = {}
    p2joptions = ttk.Frame(gui, height=10, width=10, padding="3 3 20 20")
    p2joptions.grid(column=1, row=0, sticky='nw', rowspan=3)
    tk.Label(p2joptions, text="Py->J Options").grid(row=0,
                                                    column=0, sticky='nw')
    for i, k in enumerate(OPTIONS['p2j'].keys()):
        bol = tk.BooleanVar(value=OPTIONS['p2j'][k])
        tk.Checkbutton(p2joptions,
                       text=k,
                       variable=bol,
                       onvalue=True,
                       offvalue=False,
                       ).grid(column=0, row=i+1, sticky="nw")
        bol.trace_add(mode='write',
                      callback=lambda x, y, z: refresh_options())
        p2jboxes[k] = bol

    j2pboxes = {}
    j2poptions = ttk.Frame(gui, height=10, width=10, padding="3 3 20 20")
    j2poptions.grid(column=2, row=0, sticky='nw', rowspan=3)
    tk.Label(j2poptions, text="J->Py Options").grid(row=0,
                                                    column=0, sticky='nw')
    for i, k in enumerate(OPTIONS['j2p'].keys()):
        bol = tk.BooleanVar(value=OPTIONS['j2p'][k])
        tk.Checkbutton(j2poptions,
                       text=k,
                       variable=bol,
                       onvalue=True,
                       offvalue=False,
                       ).grid(column=0, row=i+1, sticky="nw")
        bol.trace_add(mode='write',
                      callback=lambda x, y, z: refresh_options())
        j2pboxes[k] = bol

    # inner functions
    def refresh_options():
        """Callback for option editing"""
        p("OPTIONS EDITED")
        for k, v in p2jboxes.items():
            OPTIONS['p2j'][k] = p2jboxes[k].get()
        for k, v in j2pboxes.items():
            OPTIONS['j2p'][k] = j2pboxes[k].get()
        OPTIONS['overwrite'] = overwrite.get()
        print(OPTIONS)

    def openfile(var='in'):
        # TODO REWRITE HORRIBLE METHOD
        try:
            if var == 'in':
                out = Path(askopenfilename(initialdir='.'))
                inputvalue.set(out)
                outputvalue.set(convert_name(str(out)))
                if re.match(r".*\.py$", str(out)):
                    status.config(text=f"Py -> J")
                else:
                    status.config(text=f"J -> Py")
            else:
                out = Path(
                    askdirectory(initialdir='.')) / convert_name(
                        str(Path(inputvalue.get()).name))
                outputvalue.set(out)
                status.config(text=f"Output set")
        except Exception as e:
            status.config(text=f"Error: {e}")

    def inner_run():
        try:
            fin = inputtext.get()
            fout = outputtext.get()
            output = runconversion(fin, fout)
            status.config(text=output)
        except FileExistsError:
            status.config(text=f"File {Path(fout).name} ALREADY EXISTS!")
        except Exception as e:
            print(f"Error: {e}")
            status.config(text=breakstr(f"Error: {e}"))

    gui.mainloop()
    p("Gui closed")


def print_help():
    print(TITLE)
    print("J2Py conversion utility")
    print("Usage options")
    print(
        "j2py.py [input_file] [output_file] -w -h -m --use-blanks --ignore-ins --no-markdown --overwrite ")
    print(" (no arguments) or -w (windowed)")
    print("\tWill open the gui mode (suggested)")
    print(" -h --help")
    print("\tPrints this message and exits")
    print(" -m")
    print("\tAllows user to insert manually the input and output file")
    print("  Python --> Jupyter options:")
    print("--use-blanks")
    print("\tSPLIT code whenever there are blank lines")
    print("--ignore-ins")
    print("\tIGNORE the In[#] separators when")
    print("--no-markdown")
    print("\tWill ignore double hashtag rows (usually marking Markdown data)")
    print("  Jupyter --> Python options")
    print("--delete-markdown")
    print("\tIGNORE markdown and raw cells")
    print("--remove-separators")
    print("\tDoes NOT PASTE SEPARATORS (makes a cleaner output)")
    print("Other options")
    print("  --overwrite")
    print("\tWill OVERWRITE the destination file if already in the system")
    print("")


def main():
    if len(sys.argv) == 1:
        p("Window select called")
        # simplewindowselect()
        guimode()
        return

    # parse arguments
    iargs = iter(sys.argv[1:])
    dargs = {'files': []}
    for a in iargs:
        p(a)
        # match_ext = re.match(reg.arg_ext, a)
        # match_short =re.match(reg.arg_short, a)
        if a in ['-h', '--help']:
            print_help()
            return
        elif a == '-w':
            # simplewindowselect()
            guimode()
            return
        elif a == '-m':
            # MANUAL MODE
            p(TITLE)
            p('Manual Mode')
            dir_input = input(
                "Please insert the input file name (must be a .py or .ipynb file).")
            dir_output = input(
                f"Please insert the name of the output file (same name by default).")
            if dir_output == '':
                dir_output = convert_name(dir_input)
            dargs['files'] = [dir_input, dir_output]
        # py2j options
        elif a in ['--use-blanks']:
            OPTIONS['p2j']['blank_separators'] = True
        elif a in ['--ignore-ins']:
            OPTIONS['p2j']['in_separators'] = False
        elif a in ['--no-markdown']:
            OPTIONS['p2j']['markdown_separators'] = False
        # j2py options
        elif a in ['--delete-markdown']:
            OPTIONS['j2py']['delete_markdown'] = True
        elif a in ['--remove-separators']:
            OPTIONS['j2py']['keep_separators'] = False
        # other options
        elif a in ['--overwrite']:
            OPTIONS['overwrite'] = True
        else:
            dargs['files'].append(a)

    p(dargs)

    assert len(dargs['files']
               ) > 0, "You must select at least 1 file to convert"

    if len(dargs['files']) & 1 == 1:  # evenize the file arguments
        dargs['files'].append(convert_name(dargs[-1]))

    for inputfile, outputfile in pairwise(dargs['files']):
        runconversion(inputfile, outputfile)


if __name__ == '__main__':
    main()
