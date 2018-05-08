#!/usr/bin/python
from Tkinter import * 

from xml.etree.ElementTree import parse

import string

DEFAULT_FORMATS = ("${severity}::${verbosity_str} ${file}(${line}) @ ${time} : ${context} [${id}] ${msg}",
                   "${verbosity_str} @ ${time} : ${context} [${id}] ${msg}",
                   "${time} : ${context} ${msg}")

uvm_verbosities = {"UVM_NONE":0, "UVM_LOW":100, "UVM_MEDIUM":200, "UVM_HIGH":300, "UVM_FULL":400, "UVM_DEBUG":500}
uvm_verbosity_strings = "asdfa" #{uvm_verbosities[v]:v for v in uvm_verbosities}

class ScrolledText(Frame):
    def __init__(self, parent=None, text='', file=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)               
        self.makewidgets()
        self.settext()
    def makewidgets(self):
        self.sbar = Scrollbar(self)

        text = Text(self, relief=SUNKEN)
        self.sbar.config(command=text.yview)                  
        text.config(yscrollcommand=self.sbar.set)           
        self.status = StringVar()
        self.status_widget = Label(self, textvar = self.status, relief=SUNKEN)
        self.status.set('status bar')
        self.status_widget.config(font=('courier', 10, 'normal'))
        self.status_widget.pack(side=BOTTOM, fill=X) 
        self.sbar.pack(side=RIGHT, fill=Y)                   
        text.pack(side=LEFT, expand=YES, fill=BOTH) 
        self.text = text


    def settext(self):
        self.text.config(state=NORMAL)
        scroll_location = self.text.yview()
        if self.file: 
            text = self.parse_log()
        self.text.delete('1.0', END)                   
        self.text.insert('1.0', text)                  
        self.text.mark_set(INSERT, '1.0')              
        self.text.focus()
        self.text.config(state=DISABLED)
        self.text.yview('moveto', scroll_location[0])

    def gettext(self):                               
        return self.text.get('1.0', END+'-1c')         

    def parse_log(self):
        log_data = ""
        data=parse(self.file)
        log=data.getroot()
        verbosity_value = 101
        verbosity_level = self.verbosity.get()
        if verbosity_level in uvm_verbosities:
            verbosity_value = uvm_verbosities[verbosity_level] + 1

        severity_value = self.severity.get()
        context_value = self.context.get()
        id_value = self.id.get()
        source_file_value = self.filer.get()


        message_template = string.Template(self.format.get() + '\n')
        for msg in log:
          if eval(msg.attrib['verbosity']) < verbosity_value:

            if context_value != ' ':
                if msg.attrib['context'] != context_value:
                    continue

            if id_value != ' ':
                if msg.attrib['id'] != id_value:
                    continue
            if source_file_value != ' ':
                if msg.attrib['file'] != source_file_value:
                    continue
            if severity_value != ' ':
                if msg.attrib['severity'] != severity_value:
                    continue
            try:
                verbosity_string = uvm_verbosity_strings[eval(msg.attrib['verbosity'])]
            except:
                verbosity_string = msg.attrib['verbosity']
            log_data += "data "#message_template.substitute({x:msg.attrib[x] for x in msg.keys()}, verbosity_str = verbosity_string, msg=msg.text)
        return log_data

    def pre_parse_log(self):
        data=parse(self.file)
        log=data.getroot()

        severity_set = set()
        file_set = set()
        id_set = set()
        context_set = set()
        for msg in log:
            severity_set.add(msg.attrib['severity'])
            file_set.add(msg.attrib['file'])
            id_set.add(msg.attrib['id'])
            context_set.add(msg.attrib['context'])

        return(severity_set, file_set, id_set, context_set)


class SimpleEditor(ScrolledText):                        
    def __init__(self, parent=None, file=None): 
        self.root = Tk()
        self.file = file
        frm = Frame(parent)
        self.root.title(self.file)

        frm.pack(fill=X)

        self.format = StringVar()
        self.format_widget = Combobox(frm, values = DEFAULT_FORMATS, textvar = self.format)
        self.format_widget.pack(side=BOTTOM, fill=X)

        self.format_widget.current(0)

        self.format_widget.bind('<Return>', self.updateLog)
        self.format_widget.bind('<<ComboboxSelected>>', self.updateLog)

        Button(frm, text='Find',  command=self.onFind).pack(side=LEFT)

        (severity_set, file_set, id_set, context_set) = self.pre_parse_log()
        
        values = list(uvm_verbosities.keys())
        values.sort(key = lambda x:uvm_verbosities[x])
        self.verbosity = Combobox(frm, values = values , state='readonly')
        self.verbosity.bind('<<ComboboxSelected>>', self.updateLog)
        self.verbosity.set("UVM_LOW")
        self.verbosity.pack(side=LEFT)

        severities = list(severity_set)
        severities.sort()
        self.severity = Combobox(frm, values = [' ',] + severities, state='readonly')
        self.severity.current(0)
        self.severity.bind('<<ComboboxSelected>>', self.updateLog)
        self.severity.pack(side=LEFT)

        contexts = list(context_set)
        contexts.sort()
        self.context = Combobox(frm, values = [' ',] + contexts, state='readonly')
        self.context.current(0)
        self.context.bind('<<ComboboxSelected>>', self.updateLog)
        self.context.pack(side=LEFT, expand=YES, fill=X)

        ids = list(id_set)
        ids.sort()
        self.id = Combobox(frm, values = [' ',] + ids, state='readonly')
        self.id.current(0)
        self.id.bind('<<ComboboxSelected>>', self.updateLog)
        self.id.pack(side=LEFT, expand=YES, fill=X)

        files = list(file_set)
        files.sort()
        self.filer = Combobox(frm, values = [' ',] + files, state='readonly')
        self.filer.current(0)
        self.filer.bind('<<ComboboxSelected>>', self.updateLog)
        self.filer.pack(side=LEFT, expand=YES, fill=X)

#       Button(frm, text='Refresh',  command=self.updateLog).pack(side=LEFT)

        Button(frm, text='Quit', command=frm.quit).pack(side=LEFT)

        ScrolledText.__init__(self, parent, file=file) 
        self.text.config(font=('courier', 12, 'normal'))
                                              
    def onFind(self):
        target = askstring('SimpleEditor', 'Search String?')
        if target:
            where = self.text.search(target, INSERT, END)  
            if where:                                    
                print(where)
                pastit = where + ('+%dc' % len(target))   
                self.text.tag_add(SEL, where, pastit)     
                self.text.mark_set(INSERT, pastit)         
                self.text.see(INSERT)                    
                self.text.focus()  

    def updateLog(self, *args):
        self.status.set(self.verbosity.get())
        self.settext()

if __name__ == '__main__':
    try:
        SimpleEditor(file=sys.argv[1]).mainloop()   
    except IndexError:
        SimpleEditor().mainloop()    
