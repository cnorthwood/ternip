"""

Graphical User Interface for the Tarsqi Toolkit

"""

import os
import sys
import popen2
import time
import re

import wx
import wx.html

from tarsqi import TarsqiControl
from ttk_path import TTK_ROOT
from demo.display import HtmlGenerator
from docmodel.model import DocumentModel
from docmodel.xml_parser import Parser
from library.tarsqi_constants import PREPROCESSOR, GUTIME, EVITA, SLINKET, S2T
from library.tarsqi_constants import CLASSIFIER, BLINKER, CLASSIFIER, LINK_MERGER


# User choices for the document type and other processing options.
# Note: need to use strings here, wxPython on OSX is forgiving if we
# use True instead of 'True' but wxPython on RHEL5 chokes on it.
CHOICES_DOCUMENT_TYPE = [ 'simple-xml', 'timebank', 'rte3', 'atee', ]
CHOICES_TRAP_ERRORS = ['True', 'False']

# colors and titles
HTML_BACKGROUND_COLOUR = '#ffffee'
HTML_BACKGROUND_COLOUR = '#ffffff'
TITLE_SPLASH_WINDOW = 'TARSQI'
TITLE_CONTROL_WINDOW = 'Tarsqi Control Panel'



class TarsqiApp(wx.App):

    """The Tarsqi Application consists, on startup, of one frame. That
    frame is either a splash screen or the control panel, this can be
    changed easily in the OnInit method."""
    
    def OnInit(self):
        #self.frame = SplashFrame()
        self.frame = ControlFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


class TarsqiFrame(wx.Frame):

    """Abstract class that contains common functionality for the windows
    in the Tarsqi application. It is not supposed to have any instances."""

    def __init__(self, parent, id, title, size=(800,800), pos=(50,50),
                 style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE):
        wx.Frame.__init__(self, parent,wx.ID_ANY, title, size=size, pos=pos, style=style)

    def OnExit(self, e):
        self.Close(True)

    def OnClose(self, e):
        self.Close(True)

    def CreateMenuItem(self, menu, label, handler_function):
        menu_item = menu.Append(wx.ID_ANY, label)
        self.Bind(wx.EVT_MENU, handler_function, menu_item)

    def AddButton(self, panel, label, handler, boxsizer=None, proportion=0, style=wx.ALL, border=5):
        """Creates a Button and adds it to a Panel and to a BoxSizer if one is
        specified. Returns the Button."""
        button = wx.Button(panel, label=label)
        self.Bind(wx.EVT_BUTTON, handler, button)
        if boxsizer:
            boxsizer.Add(button, proportion, style, border)
        return button
        
    def DisplayFile(self, filename, tag=False):
        """Display an HTML file. Assumes there is a document instance variable
        so this method is only useful for instances of SplashWindow
        and ResultsWindow. TableWindow has its own version of this
        method, those two should be merged."""
        opentag = ''
        closetag = ''
        if tag:
            opentag = '<'+tag+'>' 
            closetag = '</'+tag+'>' 
        text = "<html><body bgcolor=%s>%s%s%s</body></html>" % \
            (HTML_BACKGROUND_COLOUR, opentag, file_contents(filename), closetag)
        self.document.SetPage(text)

    def BuildMenuBar(self, menubar_spec):
        """Take a menubar specification (which is a tuple) and build a menubar."""
        menus = []
        for menu_spec in menubar_spec:
            #print "\nMENU : ", menu_spec
            menu_name = menu_spec[0]
            menu = wx.Menu()
            for menuitem_spec in menu_spec[1]:
                if menuitem_spec == "SEPARATOR":
                    menu.AppendSeparator()
                else:
                    (label, handler) = menuitem_spec
                    self.CreateMenuItem(menu, label, handler)
            menus.append((menu_name, menu))
        menubar = wx.MenuBar()
        for menu in menus:
            menubar.Append(menu[1], menu[0])
        self.SetMenuBar(menubar)


        
class SplashFrame(TarsqiFrame):

    """Just a splash window with nothing but a nice picture in it, should
    use a SplashWindow for this."""

    def __init__(self):
        TarsqiFrame.__init__(self, None , wx.ID_ANY, title=TITLE_SPLASH_WINDOW,
                             size=(750,550), pos=(25,25))
        panel = wx.Panel(self)
        self.document = wx.html.HtmlWindow(panel, wx.ID_ANY, style=wx.TE_MULTILINE)
        os.chdir(TTK_ROOT + os.sep + 'demo' + os.sep + 'html')
        self.DisplayFile('splash.html')
        os.chdir(TTK_ROOT)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.document, 1, wx.ALL|wx.EXPAND, 5)
        self.AddButton(panel, "Open Control Panel", self.OnOpenControlFrame,
                       sizer, style=wx.BOTTOM|wx.LEFT)
        self.CreateMenuBar()
        panel.SetSizer(sizer)
        panel.Layout()

    def CreateMenuBar(self):
        self.BuildMenuBar(
            [("&File",
              [("Open Control Panel\tCtrl-C", self.OnOpenControlFrame),
               ("Exit\tCtrl-E", self.OnExit)])])

    def OnOpenControlFrame(self, e):
        frame = ControlFrame(self)
        frame.Show()



class ControlFrame(TarsqiFrame):

    
    def __init__(self, parent=None):

        TarsqiFrame.__init__(self, parent, wx.ID_ANY, title=TITLE_CONTROL_WINDOW,
                             size=(1000,600), pos=(25,25), style=wx.DEFAULT_FRAME_STYLE)

        self.InitializeParameters()

        panel = wx.Panel(self)
        self.CreateMenuBar()
        self.CreateStatusBar()

        process_box = self.CreateProcessBox(panel)
        options_box = self.CreateOptionsBox(panel)
        
        self.components = ComponentsWindow(self)
        self.text_Info = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE)
        #self.text_Info.SetBackgroundColour(wx.BLUE)
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(process_box, proportion=0, flag=wx.TOP, border=5)
        box.Add(options_box, proportion=0, flag=wx.TOP, border=5)
        bbox = wx.BoxSizer(wx.HORIZONTAL)
        bbox.Add(self.components, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        bbox.Add(self.text_Info, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        box.Add(bbox, proportion=1, flag=wx.EXPAND)

        self.SetDefaultContentTag()
        panel.SetSizer(box)
        panel.Layout()

        
    def CreateProcessBox(self, panel):
        self.label_FileName = wx.StaticText(panel, wx.ID_ANY, "File Name")
        self.text_FileName = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_READONLY)
        self.button_LoadFile = self.AddButton(panel, "Load File", self.LoadFile)
        self.button_LoadText = self.AddButton(panel, "Load Text", self.LoadText)
        self.button_Process = self.AddButton(panel, "Process File", self.OnParse)
        self.button_View = self.AddButton(panel, "View Results", self.OnViewResult)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.label_FileName, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        box.Add(self.text_FileName, 6, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        box.Add(self.button_LoadFile, 2, wx.ALL|wx.ALIGN_CENTER, 5)
        box.Add(self.button_LoadText, 2, wx.ALL|wx.ALIGN_CENTER, 5)
        box.Add(self.button_Process, 2, wx.ALL|wx.ALIGN_CENTER, 5)
        box.Add(self.button_View, 2, wx.ALL|wx.ALIGN_CENTER, 5)
        return box

    def CreateOptionsBox(self, panel):
        # TODO: add code to guess a document type from the file path,
        # rather than just using simple-xml
        (box1, self.choice_InputType) = \
            self.CreateLabeledChoiceField(panel, "Document Type", CHOICES_DOCUMENT_TYPE, 0)
        self.Bind(wx.EVT_CHOICE, self.OnChangedInputType, self.choice_InputType)
        (box2, self.choice_TrapErrors) = \
            self.CreateLabeledChoiceField(panel, "Trap Errors", CHOICES_TRAP_ERRORS, 0)
        (box3, self.text_ContentTag) = self.CreateLabeledTextField(panel, "Content Tag")
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(box1, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        box.Add(box2, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        box.Add(box3, 0,  wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        return box
    
    def CreateLabeledTextField(self, panel, label):
        """Creates a pair of a StaticText and a TextCtrl, and puts them in a
        BoxSizer, returns a tuple of the BoxSizer and the TextCtrl."""
        label = wx.StaticText(panel, wx.ID_ANY, label)
        text = wx.TextCtrl(panel, wx.ID_ANY)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.RIGHT|wx.ALIGN_CENTER, 5)
        box.Add(text, 1, wx.ALIGN_CENTER)
        return (box, text)

    def CreateLabeledChoiceField(self, panel, label, choices, selection=-1):
        """Creates a pair of a StaticText and a Choice, and puts them in a
        BoxSizer, returns a tuple of the BoxSizer and the Choice."""
        label = wx.StaticText(panel, wx.ID_ANY, label)
        choice = wx.Choice(panel, wx.ID_ANY, choices=choices)
        if selection > -1:
            choice.SetSelection(selection)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(label, 0, wx.RIGHT|wx.ALIGN_CENTER, 5)
        box.Add(choice, 1, wx.ALIGN_CENTER)
        return (box, choice)
        
    def InitializeParameters(self):
        self.indir = os.path.join(TTK_ROOT, 'data', 'in')
        self.indir_user = os.path.join(TTK_ROOT, 'data', 'in', 'User')
        self.displaydir = os.path.join(TTK_ROOT, 'data', 'display')
        self.demodir = os.path.join(TTK_ROOT, 'demo')
        self.tangodir = os.path.join(TTK_ROOT, 'demo', 'tango-v15')
        self.parsed = False
        
    def CreateMenuBar(self):
        self.BuildMenuBar(
            [("&File",
              [("Process File\tCtrl-P", self.OnParse),
               ("View Results\tCtrl-V", self.OnViewResult),
               "SEPARATOR",
               ("Exit\tCtrl-E", self.OnClose)]),
             ("&Input",
              [("Load Text\tCtrl-T", self.LoadText),
               ("Load File\tCtrl-F", self.LoadFile)])])
        
    def DisplayFilename(self, name):
        path_components = name.split(os.sep)
        if len(path_components) > 3:
            path_components = path_components[-3:]
        self.text_FileName.SetValue(os.sep.join(path_components))

    def LoadFile(self,e):
        dlg = wx.FileDialog(self, "Choose a file", self.indir, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.file_basename = dlg.GetFilename()
            self.file_dirname = dlg.GetDirectory()
            self.file_path = os.path.join(self.file_dirname, self.file_basename)
            print "\nOPENING FILE:", self.file_path
            self.DisplayFilename(self.file_path)
            self.text_Info.SetValue(file_contents(self.file_path))
            self.parsed = False
        dlg.Destroy()

    def LoadText(self,e):
        """The problem with this method is that it uses a TextEntryDialog
        which cannot be sized so a rather small text entry windows
        comes up. See test_textdialog.py for a first attempt."""
        dlg = wx.TextEntryDialog(None, "Enter text for temporal parsing", 'Text Input', '', 
                                 style=wx.TE_MULTILINE|wx.CANCEL|wx.OK)
        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetValue()
            self.file_basename = 'x-' + str(time.time())
            self.file_dirname = self.indir_user
            self.file_path = os.path.join(self.file_dirname, self.file_basename)
            print "\nOPENING FILE:", self.file_path
            self.WriteTextToFile(text, self.file_path)
            self.DisplayFilename(self.file_path)
            self.text_Info.SetValue(file_contents(self.file_path))
            self.parsed = False
        dlg.Destroy()

    def WriteTextToFile(self, text, filename):
        text = protect_text(text)
        file = open(self.file_path, "w")
        #file.write('<?xml version="1.0" ?>' + "\n")
        file.write("<DOC>\n")
        file.write("<DOCNO>%s</DOCNO>\n" % filename)
        file.write('<DOCTYPE SOURCE="user"></DOCTYPE>' + "\n")
        file.write("<TEXT>\n")
        file.write(text)
        file.write("</TEXT>\n</DOC>\n")
        file.close()


    def GetOption_DocType(self):
        """Return the selected document type, returns None if nothing was
        selected."""
        selection = self.choice_InputType.GetSelection()
        if selection > -1:
            return CHOICES_DOCUMENT_TYPE[selection]
        else:
            return None

    def GetOption_TrapErrors(self):
        """Return the tarp_errors setting, which is a boolean."""
        choice = CHOICES_TRAP_ERRORS[self.choice_TrapErrors.GetSelection()]
        # need to do this because the choice box contains strings
        if choice == 'True':
            return True
        else:
            return False


    def OnChangedInputType(self, e):
        """Change the content_tag and the selected components when the
        document type changes."""
        self.SetDefaultContentTag()
        self.components.UpdateComponentSelection(self)

    def SetDefaultContentTag(self):
        doc_type = self.GetOption_DocType()
        tag = DocumentModel().get_default_content_tag(doc_type)
        self.text_ContentTag.SetValue(tag)



    def OnParse(self, e):

        print 'PROCESSING FILE:', self.file_path

        base_path = os.path.join(self.displaydir, self.file_basename)
        self.file_out =  base_path + '.ALL.xml'
        self.file_display_local = base_path + '.d.local.html'
        self.file_display_all = base_path + '.d.all.html'

        doc_type = self.GetOption_DocType()
        trap_errors = self.GetOption_TrapErrors()
        pipeline = self.components.GetPipeline()

        options = {'trap_errors': trap_errors,
                   'pipeline': pipeline }

        print 'DOCUMENT TYPE:', doc_type
        print 'OPTIONS:'
        for option, val in options.items():
            print "    %s -> %s" % (option, val)

        print 'PROCESSING...'
        tc = TarsqiControl(doc_type, options, self.file_path, self.file_out)
        tc.process()
        #self.text_Info.SetValue(file_contents(self.file_out))
        self.text_Info.SetValue(xml_tree(self.file_out))
        print 'CREATED:', self.file_out

        # Create display file using various intermediate files created
        # by the TarsqiControl instance.
        generator = HtmlGenerator(tc.FILE_CLA)
        generator.create_file(base_path + '.sli.html', [SLINKET, S2T])
        generator.create_file(base_path + '.bli.html', [BLINKER])
        generator.create_file(base_path + '.cla.html', [CLASSIFIER])
        generator.create_file(base_path + '.all.html', [SLINKET, S2T, BLINKER, CLASSIFIER])
        generator.create_events_table(base_path + '.events.html')
        generator.create_timexes_table(base_path + '.timexes.html')
        generator.create_links_table(base_path + '.links.html')
        generator = HtmlGenerator(tc.FILE_MER)
        generator.create_file(base_path + '.mer.html', [SLINKET, S2T, BLINKER, CLASSIFIER])

        self.parsed = True


    def OnViewResult(self, e):
        if self.parsed:
            frame = ResultFrame(self)
            frame.Show()
        else:
            print 'WARNING: file not yet parsed'


class ResultFrame(TarsqiFrame):

    def __init__(self, parent):

        title = parent.file_basename
        TarsqiFrame.__init__(self, parent, wx.ID_ANY, title=title,
                             size=(800,800), pos=(200,150),
                             style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)

        # copy needed files etc from parent window
        self.file_basename = parent.file_basename
        self.displaydir =  parent.displaydir
        self.tangodir = parent.tangodir

        base_path = os.path.join(self.displaydir, self.file_basename)
        self.file_display_sli = base_path + '.sli.html'
        self.file_display_bli = base_path + '.bli.html'
        self.file_display_cla = base_path + '.cla.html'
        self.file_display_all = base_path + '.all.html'
        self.file_display_mer = base_path + '.mer.html'

        panel = wx.Panel(self)

        self.document = wx.html.HtmlWindow(panel, wx.ID_ANY, style=wx.TE_MULTILINE)

        # topSizer contains the display buttons
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.AddButton(panel, "Slinket", self.OnViewSlinket, topSizer)
        self.AddButton(panel, "Blinker", self.OnViewBlinker, topSizer)
        self.AddButton(panel, "Classifier", self.OnViewClassifier, topSizer)
        self.AddButton(panel, "All", self.OnViewAll, topSizer)
        self.AddButton(panel, "Merged", self.OnViewMerged, topSizer)
        self.AddButton(panel, "Tables", self.OnView, topSizer)
        self.AddButton(panel, "Graph", self.OnTango, topSizer)
        self.AddButton(panel, "TBox", self.OnTBox, topSizer)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(topSizer)
        mainSizer.Add(self.document, 1, wx.ALL|wx.EXPAND, 5)

        self.CreateMenuBar()
        self.CreateStatusBar()
        self.DisplayFile(self.file_display_sli)
        
        panel.SetSizer(mainSizer)
        panel.Layout()


    def CreateMenuBar(self):
        self.BuildMenuBar(
            [("&File",
              [("Exit\tCtrl-E", self.OnExit)]),
             ("&View",
              [("All Tables", self.OnView),
               ("Timexes", self.OnViewTimexes),
               ("Events", self.OnViewEvents),
               ("TLinks", self.OnViewTLinks),
               ("Graph", self.OnTango),
               ("TBox", self.OnTBox)])])

    def OnViewSlinket(self, e):
        print 'Opening', self.file_display_sli
        self.DisplayFile(self.file_display_sli)

    def OnViewBlinker(self, e):
        print 'Opening', self.file_display_bli
        self.DisplayFile(self.file_display_bli)

    def OnViewClassifier(self, e):
        print 'Opening', self.file_display_cla
        self.DisplayFile(self.file_display_cla)

    def OnViewAll(self, e):
        print 'Opening', self.file_display_all
        self.DisplayFile(self.file_display_all)

    def OnViewMerged(self, e):
        print 'Opening', self.file_display_mer
        self.DisplayFile(self.file_display_mer)

    def OnTango(self, e):
        os.chdir(self.tangodir)
        file = self.displaydir + os.sep + self.file_basename + '.ALL.xml'
        command = 'java -jar tango_v15.jar file=' + file
        print 'OPENING TANGO:', command
        popen2.popen2(command)

    def OnTBox(self, e):
        """To load a tbox picture"""
        pass

    def OnView(self, e):
        self.OnViewTimexes(e)
        self.OnViewEvents(e)
        self.OnViewTLinks(e)

    def OnViewEvents(self, e):
        eventsfile = self.displaydir + os.sep + self.file_basename + '.events.html'
        title = "Events in " + self.file_basename
        TableFrame(self, title, eventsfile, size=(650,500), pos=(600,50)).Show()

    def OnViewTimexes(self, e):
        timexesfile = self.displaydir + os.sep + self.file_basename + '.timexes.html'
        title = "Timexes in " + self.file_basename
        TableFrame(self, title, timexesfile, size=(550,500), pos=(800,400)).Show()

    def OnViewTLinks(self, e):
        tlinksfile = self.displaydir + os.sep + self.file_basename + '.links.html'
        title = "Tlinks in " + self.file_basename
        TableFrame(self, title, tlinksfile, size=(600,500), pos=(700,300)).Show()


        
class TableFrame(TarsqiFrame):

    """Window class for the tables with events, timexes and links."""
    
    def __init__(self, parent, title, file, size, pos):
        TarsqiFrame.__init__(self,parent, wx.ID_ANY, title=title, size=size, pos=pos)
        panel = wx.Panel(self)
        self.document = wx.html.HtmlWindow(panel, wx.ID_ANY, style=wx.TE_MULTILINE)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.document, 1, wx.ALL|wx.EXPAND, 5)
        self.DisplayFile(file)
        self.CreateMenuBar()
        panel.SetSizer(mainSizer)
        panel.Layout()

    def CreateMenuBar(self):
        self.BuildMenuBar(
            [("&File",
              [("Exit\tCtrl-E", self.OnExit)])])


class ComponentsWindow(wx.Window):

    """Window that contains all checkboxes for component selection."""
    
    def __init__(self, parent):

        wx.Window.__init__(self, parent, style=wx.SUNKEN_BORDER)

        # a CheckBox for each tarsqi component
        label = wx.StaticText(self, wx.ID_ANY, 'Components     ')
        self.cb_tokenizer = wx.CheckBox(self, wx.ID_ANY, "Tokenizer")
        self.cb_tagger = wx.CheckBox(self, wx.ID_ANY, "Tagger")
        self.cb_chunker = wx.CheckBox(self, wx.ID_ANY, "Chunker")
        self.cb_gutime = wx.CheckBox(self, wx.ID_ANY, "GUTime")
        self.cb_evita = wx.CheckBox(self, wx.ID_ANY, "Evita")
        self.cb_slinket = wx.CheckBox(self, wx.ID_ANY, "Slinket")
        self.cb_s2t = wx.CheckBox(self, wx.ID_ANY, "S2T")
        self.cb_blinker = wx.CheckBox(self, wx.ID_ANY, "Blinker")
        self.cb_classifier = wx.CheckBox(self, wx.ID_ANY, "Classifier")
        self.cb_merger = wx.CheckBox(self, wx.ID_ANY, "LinkMerger")
        self.label = wx.StaticText(self, wx.ID_ANY, "")
        self.bt_SelectAll = wx.Button(self, wx.ID_ANY, "Select All")
        self.bt_DeselectAll = wx.Button(self, wx.ID_ANY, "Deselect All")

        # group the preprocessors
        self.Bind(wx.EVT_CHECKBOX, self.OnSetTokenizer, self.cb_tokenizer)
        self.Bind(wx.EVT_CHECKBOX, self.OnSetTagger, self.cb_tagger)
        self.Bind(wx.EVT_CHECKBOX, self.OnSetChunker, self.cb_chunker)

        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.bt_SelectAll)
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, self.bt_DeselectAll)

        # display all boxes
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.cb_tokenizer, 0, wx.ALL, 5)
        sizer.Add(self.cb_tagger, 0, wx.ALL, 5)
        sizer.Add(self.cb_chunker, 0, wx.ALL, 5)
        sizer.Add(self.cb_gutime, 0, wx.ALL, 5)
        sizer.Add(self.cb_evita, 0, wx.ALL, 5)
        sizer.Add(self.cb_slinket, 0, wx.ALL, 5)
        sizer.Add(self.cb_s2t, 0, wx.ALL, 5)
        sizer.Add(self.cb_blinker, 0, wx.ALL, 5)
        sizer.Add(self.cb_classifier, 0, wx.ALL, 5)
        sizer.Add(self.cb_merger, 0, wx.ALL, 5)
        sizer.Add(self.label, 0, wx.TOP, 5)
        sizer.Add(self.bt_SelectAll, 0, wx.ALL, 5)
        sizer.Add(self.bt_DeselectAll, 0, wx.ALL, 5)
        self.SetSizer(sizer)
        self.Layout()

        self.SetComponentMappings()
        self.UpdateComponentSelection(parent)
        

    def UpdateComponentSelection(self, parent):
        """Take the default pipeline from the input type choice and export it
        to the components checkboxes."""
        doc_type = parent.GetOption_DocType()
        pipeline = DocumentModel().get_default_pipeline(doc_type)
        self.SetAllValues(False)
        for element in pipeline:
            for checkbox in self.componentname_to_checkbox[element]:
                checkbox.SetValue(True)

                
    def SetComponentMappings(self):
        # an ordered list of all components, where each component
        # consists of a button name, a button and a tarsqi name
        self.components = [
            ('tokenizer', self.cb_tokenizer, PREPROCESSOR),
            ('gutime', self.cb_gutime, GUTIME),
            ('evita', self.cb_evita, EVITA),
            ('slinket', self.cb_slinket, SLINKET),
            ('s2t', self.cb_s2t, S2T),
            ('blinker', self.cb_blinker, BLINKER),
            ('classifier', self.cb_classifier, CLASSIFIER),
            ('merger', self.cb_merger, LINK_MERGER) ]
        # mapping the tarsqi component name to a list of checkboxes
        self.componentname_to_checkbox = {
            PREPROCESSOR: [self.cb_tokenizer, self.cb_tagger, self.cb_chunker],
            GUTIME: [self.cb_gutime],
            EVITA: [self.cb_evita],
            SLINKET: [self.cb_slinket],
            S2T: [self.cb_s2t],
            BLINKER: [self.cb_blinker],
            CLASSIFIER: [self.cb_classifier],
            LINK_MERGER: [self.cb_merger] }

    def GetPipeline(self):
        pipeline = []
        for comp in self.components:
            name = comp[2]
            checkbox = comp[1]
            if checkbox.GetValue():
                pipeline.append(name)
        return ','.join(pipeline)
        
    def OnSetTokenizer(self, e):
        val = self.cb_tokenizer.GetValue()
        self.cb_tagger.SetValue(val)
        self.cb_chunker.SetValue(val)

    def OnSetTagger(self, e):
        val = self.cb_tagger.GetValue()
        self.cb_tokenizer.SetValue(val)
        self.cb_chunker.SetValue(val)

    def OnSetChunker(self, e):
        val = self.cb_chunker.GetValue()
        self.cb_tokenizer.SetValue(val)
        self.cb_tagger.SetValue(val)

    def OnSelectAll(self, e):
        self.SetAllValues(True)
        
    def OnDeselectAll(self, e):
        self.SetAllValues(False)
        
    def AllCheckBoxes(self):
        return [ self.cb_tokenizer, self.cb_tagger, self.cb_chunker,
                 self.cb_gutime, self.cb_evita, self.cb_slinket, 
                 self.cb_s2t, self.cb_blinker, self.cb_classifier,
                 self.cb_merger ]

    def SetAllValues(self, boolean):
        for box in self.AllCheckBoxes():
            box.SetValue(boolean)



def run_shell_command(command):
    print 'RUNNING SHELL SCRIPT:', command
    r, e = popen2.popen2(command)
    for line in r.readlines():
        print 'RUNNING COMMAND:', line,
    print e

def file_contents(filename):
    """Return the contents of filename."""
    f = open(filename, 'r')
    contents = f.read()
    f.close()
    return contents

def protect_text(text):
    """Take a text string and protect XML specual characters. Should also
    do something with non-ascii characters as well as with things like
    &#2435; and &quote;"""
    re_protect1 = re.compile('&')
    re_protect2 = re.compile('<')
    re_protect3 = re.compile('>')
    text = re_protect1.sub('&amp;', text)
    text = re_protect2.sub('&lt;', text)
    text = re_protect3.sub('&gt;', text)
    return text.encode('ascii', 'xmlcharrefreplace')

def xml_tree(filename, tab='  ', stack=[]):
    """Takes an xml file, opens it, and creates a string that shows the
    XML tree."""
    file = open(filename, 'r')
    tree_string = ''
    DOC = Parser().parse_file(file)
    for element in DOC.elements:
        if element.is_opening_tag(): stack.append(element)
        if element.is_tag():
            indent = (len(stack) - 1) * tab
        else:
            indent = (len(stack) + 0) * tab
        content_string = element.content
        content_string = content_string.strip()
        if content_string.startswith('<TLINK') or \
                content_string.startswith('<SLINK') or \
                content_string.startswith('<MAKEINSTANCE'):
            content_string = content_string[:-2] + ' />'
        if  content_string != '' and \
                content_string not in ['</TLINK>', '</SLINK>', '</MAKEINSTANCE>']:
            str = "%s %s\n" % (indent, content_string)
            tree_string += str
        if element.is_closing_tag(): stack.pop()
    return tree_string

    
if __name__ == '__main__':
    # redirection needs to be specified for OSX since default there is True
    TarsqiApp(redirect=False).MainLoop()


