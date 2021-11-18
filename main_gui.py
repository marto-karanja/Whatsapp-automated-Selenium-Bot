import os
import wx
import wx.adv
import wx.html
import threading
import time
from queue import Queue
from sys import maxsize

from bot.whatsappbot import Whatsappbot



class WhatsappPanel(wx.Panel):

        #----------------------------------------------------------------------
        def __init__(self, parent):
            wx.Panel.__init__(self, parent)
            
            self.layout()

        #----------------------------------------------------------------------
        def layout(self):
            # create main horizontal sizer
            self.mainSizer = wx.BoxSizer(wx.VERTICAL)
            # create two box sizers
            groupBoxSizer = wx.BoxSizer(wx.VERTICAL)
            messageBoxSizer = wx.BoxSizer(wx.VERTICAL)
            # add a label
            groupNameLbl = wx.StaticText(self, -1, "Group names:")
            groupNameLbl.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            # add list box and button to group boxgroup
            self.group_names = []
            self.groupListBox = wx.CheckListBox(parent = self, id = -1, choices=self.group_names, style=wx.LB_MULTIPLE, name="groupListBox")

            #sizer to hold button
            btnSizer = wx.BoxSizer(wx.HORIZONTAL)

            btnData = [("Add Group", btnSizer, self.addGroup),
            ("Delete Group", btnSizer, self.deleteGroup)]

            for data in btnData:
                label, sizer, handler = data
                self.btnBuilder(label, sizer, handler)

            # Add label, checkbox list and buttons to groupboxSizer
            groupBoxSizer.Add(groupNameLbl, 0)
            groupBoxSizer.Add(self.groupListBox, 1, wx.EXPAND)
            groupBoxSizer.Add(btnSizer, 0, wx.EXPAND)

            

            # Add to main sizer
            controlPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
            controlPanelSizer.Add(groupBoxSizer, 1, wx.EXPAND|wx.ALL, 5)
            # Populate message box sizer
            # add a label
            messageNameLbl = wx.StaticText(self, -1, "Message:")
            messageNameLbl.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.messageTxtField = wx.TextCtrl(self, -1, "", style=wx.TE_RICH2|wx.TE_MULTILINE)
            # add label to sizer
            messageBoxSizer.Add(messageNameLbl, 0)
            messageBoxSizer.Add(self.messageTxtField, 1, wx.EXPAND)
            # Add save button
            messageButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
            save_message_button = self.btnBuilder("Save Message", messageButtonSizer, self.onSaveMessage)
            self.launch_bot_button = self.btnBuilder("Launch Whatsapp", messageButtonSizer, self.onLaunchBot)
            self.send_message_button = self.btnBuilder("Send Message to Groups", messageButtonSizer, self.onSend)
            self.send_message_button.Disable()


            messageBoxSizer.Add(messageButtonSizer, 0, wx.EXPAND|wx.ALL)
            controlPanelSizer.Add(messageBoxSizer, 2, wx.EXPAND|wx.ALL, 5 )
            
            self.mainSizer.Add(controlPanelSizer, 1, wx.EXPAND)
            # add log panel sizer
            logBoxSizer = wx.BoxSizer(wx.VERTICAL)
            self.logTxtField = wx.TextCtrl(self, -1, "", style=wx.TE_RICH|wx.TE_MULTILINE)
            logLbl = wx.StaticText(self, -1, "Program Status:")
            logLbl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            logBoxSizer.Add(logLbl, 0, wx.ALL, 5)
            logBoxSizer.Add(self.logTxtField, 1, wx.EXPAND|wx.ALL, 5)
            self.mainSizer.Add(logBoxSizer, 1, wx.EXPAND | wx.ALL)
            self.SetSizer(self.mainSizer)
            self.Fit()
            
        #----------------------------------------------------------------------
        def btnBuilder(self, label, sizer, handler):
            """
            Builds a button, binds it to an event handler and adds it to a sizer
            """
            btn = wx.Button(self, label=label)
            btn.Bind(wx.EVT_BUTTON, handler)
            sizer.Add(btn, 0, wx.ALL|wx.CENTER, 3)
            return btn

        #-----------------------------------------------------------------------
        def onSaveMessage(self, evt):
            # get selected groups
            # update message in sqlite database
            pass

        #-----------------------------------------------------------------------
        def addGroup(self, evt):
            group_name = "AWWB Kikuyu"
            # Create Dialog Box
            message = "Enter name of group to message"
            dialog = wx.GetTextFromUser(message, caption="Input text", default_value="", parent=None)
            if dialog != "":
                # Add item to list box
                self.groupListBox.Append(dialog)
            

        #-----------------------------------------------------------------------
        def deleteGroup(self, evt):
            pass


        #------------------------------------------------------------------------
        def get_group_names(self):
            group_names = self.groupListBox.GetCheckedStrings()
            return group_names

        #------------------------------------------------------------------------
        def onLaunchBot(self, evt):
                # Create whatsappBot 
                self.bot = Whatsappbot()
                self.send_message_button.Enable()
                


        #------------------------------------------------------------------------
        def onSend(self,evt):
            # get message from text field
            msg_lines = self.messageTxtField.GetNumberOfLines()
            message = []
            for line in range(msg_lines):
                msg = self.messageTxtField.GetLineText(line)
                message.append(msg)
            message = '\n'.join(message) 
            print(message)
            # get groups selected
            group_names = self.get_group_names()
            if group_names and message:
                # launch confirmation dialogue
                retCode = wx.MessageBox("Are you sure you want to post messages to the selected group?", caption="Confirm Sending", style=wx.YES_NO | wx.ICON_INFORMATION)

                if (retCode == wx.YES):
                    # for group in group names send_message
                    """
                    for name in group_names:
                        self.bot.send_message(name, message, window = self)"""
                    # Launch search in separate thread
                    self.order_queue = Queue(maxsize = 100)
                    self.quit_event = threading.Event()
                    message_thread = threading.Thread(target=self.bot.send_messages, args=(self.order_queue, self.quit_event, self, group_names, message), daemon=True)
                    # add thread to thread of active threads
                    message_thread.start()
                            
            else:
                print("One of the field was empty")
                retCode = wx.MessageBox("Either the message is empty or no group name is selected", caption="Empty fileds", style=wx.YES_NO | wx.ICON_ERROR)
            
        #-----------------------------------------------------------------------
        def log_message_to_txt_field(self, msg):
            self.logTxtField.AppendText(msg)
            self.logTxtField.AppendText("\n")

        

        


class WhatsappBotFrame(wx.Frame):
    """Whatsapp GUI Frame"""
    def __init__(self, parent):
        self.title = "Whatsapp Bot"
        wx.Frame.__init__(self, parent, -1, self.title, size=(800,600))
        self.createMenuBar()

        self.createPanel()
        self.SetIcon(wx.Icon("assets/whatsappbot.ico"))

    def createPanel(self):
        whatsappPanel = WhatsappPanel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(whatsappPanel, 1, wx.EXPAND)
        self.SetSizer(box)


    def menuData(self):
        return [("&File", (

                    ("About...", "Show about window", self.OnAbout),
                    ("&Quit", "Quit", self.OnCloseWindow)))]

    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def createMenu(self, menuData):
        menu = wx.Menu()
        for eachItem in menuData:
            if len(eachItem) == 2:
                label = eachItem[0]
                subMenu = self.createMenu(eachItem[1])
                menu.AppendMenu(wx.NewId(), label, subMenu)
            else:
                self.createMenuItem(menu, *eachItem)
        return menu

    def createMenuItem(self, menu, label, status, handler, kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1, label, status, kind)
        self.Bind(wx.EVT_MENU, handler, menuItem)

    def OnCloseWindow(self, event):
        self.Destroy()

    def OnAbout(self, event):
        dlg = WhatsappbotAbout(self)
        dlg.ShowModal()
        dlg.Destroy()
    
class WhatsappbotAbout(wx.Dialog):
    text = '''
<html>
<body bgcolor="#ACAA60">
<center><table bgcolor="#455481" width="100%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center"><h1>Whatsapp Bot</h1></td>
</tr>
</table>
</center>
<p><b>Whatsapp Bot</b> is a an automated group messenger for the <b>Whatsapp platform
</p>
<p><b>Whatsapp Bot</b> is brought to you by
<b>Martin Karanja</b> and <b>Kushmart Technologies Limited</b>, Copyright
&copy; 2021-2022.</p>
</body>
</html>
'''

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About Sketch',
                          size=(440, 400) )

        html = wx.html.HtmlWindow(self)
        html.SetPage(self.text)
        button = wx.Button(self, wx.ID_OK, "Okay")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()

class WhatsappBotApp(wx.App):

    def OnInit(self):
        bmp = wx.Image("assets/splash.png").ConvertToBitmap()
        wx.adv.SplashScreen(bmp, wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                1000, None, -1)
        wx.Yield()

        frame = WhatsappBotFrame(None)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    app = WhatsappBotApp(False)
    app.MainLoop()