import os
import wx
import wx.adv
import wx.html
import threading
import time
from queue import Queue
from sys import maxsize

from bot.whatsappbot import Whatsappbot
from bot.db import *



class WhatsappPanel(wx.Panel):


        

        #----------------------------------------------------------------------
        def __init__(self, parent):
            wx.Panel.__init__(self, parent)
            self.time_in_secs = {'15 Minutes':900 , '30 Minutes': 1800, '45 Minutes':2700, '1 hour':3600, '75 Minutes': 4500, '90 Minutes':5400, '105 Minutes':+6300, '2 Hours':7200, '2 and a half hours': 9000, '3 Hours':10800 , '3 and a half hours':12600, '4 hours':14400, '4 and a half hours':16200, '5 hours':18000, '6 hours':21600, '7 hours':25200, '8 hours':28800, '9 hours':32400, '12 Hours':43200, '24 hours':86400}

            # boolean to check whether the field is checked
            self.select_all = False
            
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
            if readGroupNames:
                self.name_message = readGroupNames()
                self.group_names = list(self.name_message.keys())
            else:
                self.group_names = []
            self.groupListBox = wx.CheckListBox(parent = self, id = -1, choices=self.group_names, style=wx.LB_MULTIPLE, name="groupListBox")

            # event listener to listen for clicks
            self.Bind(wx.EVT_CHECKLISTBOX, self.displayMessage)

            #sizer to hold button
            btnSizer = wx.BoxSizer(wx.HORIZONTAL)


            # add checkbox button to button sizer
            self.check_all = wx.CheckBox(self, id=-1, label="", name="checkAllButton")
            # register event handler
            self.Bind(wx.EVT_CHECKBOX, self.select_all_groups, self.check_all)
            btnSizer.Add(self.check_all,0,wx.TOP, 5)

            btnData = [("Add Group", btnSizer, self.addGroup),
            ("Save Group", btnSizer, self.onSaveGroup),
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
            # display message
            if self.name_message:
                self.messageTxtField.AppendText(self.name_message[self.group_names[0]])
            # add label to sizer
            messageBoxSizer.Add(messageNameLbl, 0)
            messageBoxSizer.Add(self.messageTxtField, 1, wx.EXPAND)
            # Add save button
            messageButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
            save_message_button = self.btnBuilder("Save Message", messageButtonSizer, self.onSaveMessage)
            self.launch_bot_button = self.btnBuilder("Launch Whatsapp", messageButtonSizer, self.onLaunchBot)
            self.send_message_button = self.btnBuilder("Send Saved Messages to Groups", messageButtonSizer, self.onSend)
            self.send_current_message_button = self.btnBuilder("Send Current Messages to All Groups", messageButtonSizer, self.onSendCurrent)
            self.schedule_message_button = self.btnBuilder("Schedule Messages", messageButtonSizer, self.onScheduleMessages)
            self.send_message_button.Disable()
            self.send_current_message_button.Disable()
            self.schedule_message_button.Disable()
            self.close_button = self.btnBuilder("Close Bot", messageButtonSizer, self.onClose)
            self.close_button.Disable()



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
        def displayMessage(self, evt):
            group_names = self.get_group_names()
            if group_names:
                # display group name in message box
                self.messageTxtField.Clear()
                # update list of group names and messages
                self.name_message = readGroupNames()
                self.messageTxtField.AppendText(self.name_message.get(group_names[0], ""))


        #-----------------------------------------------------------------------
        def onSaveMessage(self, evt):
            # get selected groups
            # update message in sqlite database
            group_names = self.get_group_names()
            if group_names:
                msg = "Are you sure you want to save the message for the selected groups\n {0}?".format(('\n'.join(group_names)))
                retCode = wx.MessageBox(msg, caption="Confirm Saving", style=wx.YES_NO | wx.ICON_INFORMATION)
                if (retCode == wx.YES):
                    #saving logic in databse
                    msg = self.get_messages()
                    msg = '\n'.join(msg)
                    messages = [msg]* len(group_names)
                    # save in databse                
                    updateGroupNames(group_names, messages)
            else:
                wx.MessageBox("You have to choose atleast one group", "Error Saving", wx.OK | wx.ICON_ERROR)

                    


        #-----------------------------------------------------------------------
        def addGroup(self, evt):
            # Create Dialog Box
            message = "Enter name of group to message"
            dialog_message = wx.GetTextFromUser(message, caption="Input text", default_value="", parent=None)
            if dialog_message != "":
                # Add item to list box
                if dialog_message not in self.group_names:
                    self.group_names.append(dialog_message)
                    self.groupListBox.Append(dialog_message)
                else:
                    wx.MessageBox("Group Name already in the list", "Error", wx.OK | wx.ICON_ERROR)
                

        #-----------------------------------------------------------------------
        def onSaveGroup(self, evt):
            group_names = self.get_group_names()
            msg = self.get_messages()
            msg = '\n'.join(msg)
            messages = [msg]* len(group_names)
            if group_names:
                
                addGroupNames(group_names, messages)
                    
            else:
                wx.MessageBox("You have not choosen any groups", "Error Saving", wx.OK | wx.ICON_ERROR)


            

        #-----------------------------------------------------------------------
        def deleteGroup(self, evt):
            group_names = self.get_group_names()
            if group_names:
                for name in group_names:
                    if deleteGroupName(name):
                        index = self.groupListBox.FindString(name)
                        self.groupListBox.Delete(index)
                        self.group_names.remove(name)
                        self.messageTxtField.Clear()
                        #msg = "{0} deleted succesfully".format(name)
                        #wx.MessageBox(msg, "Success", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("You have not choosen any groups to delete", "Error Deleting", wx.OK | wx.ICON_ERROR)


        #------------------------------------------------------------------------
        def get_group_names(self):
            group_names = self.groupListBox.GetCheckedStrings()
            return group_names

        #------------------------------------------------------------------------
        def get_messages(self):
            msg_lines = self.messageTxtField.GetNumberOfLines()
            message = []
            for line in range(msg_lines):
                msg = self.messageTxtField.GetLineText(line)
                message.append(msg)
            return message

        #------------------------------------------------------------------------
        def onLaunchBot(self, evt):
                # Create whatsappBot 
                self.bot = Whatsappbot()
                self.send_message_button.Enable()
                self.send_current_message_button.Enable()
                self.close_button.Enable()
                self.schedule_message_button.Enable()
                self.launch_bot_button.Disable()
                


        #------------------------------------------------------------------------
        def onSend(self,evt):
            self.send_message_button.Disable()
            # get message from text field
            #message = self.get_messages()
            # get groups selected
            group_names = self.get_group_names()

            # fetch group and corresponding message
            groups = fetchGroupMessages(group_names)
            


            if group_names:                # launch confirmation dialogue
                retCode = wx.MessageBox("Are you sure you want to post messages to the selected group?", caption="Confirm Sending", style=wx.YES_NO | wx.ICON_INFORMATION)

                if (retCode == wx.YES):
                    # for group in group names send_message
                    """
                    for name in group_names:
                        self.bot.send_message(name, message, window = self)"""
                    # Launch search in separate thread
                    self.order_queue = Queue(maxsize = 100)
                    self.quit_event = threading.Event()
                    message_thread = threading.Thread(target=self.bot.send_messages, args=(self.order_queue, self.quit_event, self, groups), daemon=True)
                    # add thread to thread of active threads
                    message_thread.start()
                            
            else:
                print("One of the field was empty")
                retCode = wx.MessageBox("Either the message is empty or no group name is selected", caption="Empty fileds", style=wx.YES_NO | wx.ICON_ERROR)
            
            # enable send message button again
            self.send_message_button.Enable()

        #--------------------------------------------------------------------
        
        #------------------------------------------------------------------------
        def onSendCurrent(self,evt):
            self.send_current_message_button.Disable()
            # get message from text field
            message = self.get_messages()
            # get groups selected
            group_names = self.get_group_names()

            


            if group_names and message:                # launch confirmation dialogue
                retCode = wx.MessageBox("Are you sure you want to post messages to the selected group?", caption="Confirm Sending", style=wx.YES_NO | wx.ICON_INFORMATION)

                if (retCode == wx.YES):
                    # for group in group names send_message
                    """
                    for name in group_names:
                        self.bot.send_message(name, message, window = self)"""
                    # Launch search in separate thread
                    self.order_queue = Queue(maxsize = 100)
                    self.quit_event = threading.Event()
                    message_thread = threading.Thread(target=self.bot.send_current_messages, args=(self.order_queue, self.quit_event, self, group_names, message), daemon=True)
                    # add thread to thread of active threads
                    message_thread.start()
                            
            else:
                print("One of the field was empty")
                retCode = wx.MessageBox("Either the message is empty or no group name is selected", caption="Empty fileds", style=wx.YES_NO | wx.ICON_ERROR)
            
            # enable send message button again
            self.send_current_message_button.Enable()


        #-----------------------------------------------------------------------
        def onScheduleMessages(self, evt):
            # get sending interval
            # get script running time
            ## setup loop
            # call self.on send
            # wait for interval selected
            # refresh window
            dlg = ScheduleDialog(self)
            dlg.ShowModal()
            interval = self.time_in_secs[dlg.interval.GetValue()]
            workload = self.time_in_secs[dlg.workload.GetValue()]

            if interval > workload:
                wx.MessageBox("The workload has to be greater than the interval", caption="Incorrect Parameters", style=wx.YES| wx.ICON_ERROR)
            else:
                # create a task
                # spawn a thread to run the task
                self.schedule_messages(interval, workload)


            dlg.Destroy()

        


        #--------------------------------------------------------------------
        def schedule_messages(self, interval, workload):
            # fetch group names and message

            # get groups selected
            group_names = self.get_group_names()

            # fetch group and corresponding message
            groups = fetchGroupMessages(group_names)

            if group_names:
                # launch confirmation dialogue
                retCode = wx.MessageBox("Are you sure you want to schedule messages to the selected group?", caption="Confirm Sending", style=wx.YES_NO | wx.ICON_INFORMATION)

                if (retCode == wx.YES):
                    # for group in group names send_message
                    """
                    for name in group_names:
                        self.bot.send_message(name, message, window = self)"""
                    # Launch search in separate thread
                    self.order_queue = Queue(maxsize = 100)
                    self.quit_event = threading.Event()

                    
                    message_thread = threading.Thread(target=self.bot.schedule_messages, args=(self.order_queue, self.quit_event, self, groups, interval, workload), daemon=True)
                    # add thread to thread of active threads
                    message_thread.start()
                            
            else:
                print("One of the field was empty")
                retCode = wx.MessageBox("Either the message is empty or no group name is selected", caption="Empty fileds", style=wx.YES_NO | wx.ICON_ERROR)

        





            
        #-----------------------------------------------------------------------
        def log_message_to_txt_field(self, msg):
            self.logTxtField.AppendText(msg)
            self.logTxtField.AppendText("\n")

         #-----------------------------------------------------------------------
        def select_all_groups(self, evt):
            if not self.select_all:
                # tick all fields in self.checklistbox
                for i in range(0,self.groupListBox.GetCount()):
                    self.groupListBox.Check(i, True)
                self.select_all = True
            else:
                # Untick all fields in self.checklistbox
                for i in range(0,self.groupListBox.GetCount()):
                    self.groupListBox.Check(i, False)
                self.select_all = False

            


        
        #------------------------------------------------------------------
        def onClose(self, evt):
            try:
                self.bot.stop_bot()
            except AttributeError:
                pass
            self.send_message_button.Disable()
            self.current_message_button.Disable()
            self.launch_bot_button.Enable()
            self.close_button.Disable()
            self.schedule_message_button.Disable()

        

        


class WhatsappBotFrame(wx.Frame):
    """Whatsapp GUI Frame"""
    def __init__(self, parent):
        self.title = "Whatsapp Bot"
        wx.Frame.__init__(self, parent, -1, self.title, size=(1200,700))
        self.createMenuBar()

        self.createPanel()
        self.SetIcon(wx.Icon("assets/whatsappbot.ico"))

    def createPanel(self):
        self.whatsappPanel = WhatsappPanel(self)
        self.box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer.Add(self.whatsappPanel, 1, wx.EXPAND)
        self.SetSizer(self.box_sizer)


    def menuData(self):
        return [("&File", (

                    ("About...", "Show about window", self.OnAbout),
                    ("Export Settings", "Export Database", self.OnExport),
                    ("Import Settings", "Import Database", self.OnImport),
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
        self.whatsappPanel.onClose(evt=event)
        self.Destroy()

    def OnAbout(self, event):
        dlg = WhatsappbotAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExport(self, event):
        dlg = wx.FileDialog(self, "Export Bot settings to", os.getcwd(), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.bot'
            self.filename = filename
            print(self.filename)
            self.export_database()
        dlg.Destroy()

    def export_database(self):
        import sqlite3
        con = sqlite3.connect('bot.db')
        with open(self.filename, 'w', encoding="utf-8") as f:
            for line in con.iterdump():
                f.write('%s\n' % line)
        wx.MessageBox("The export has been completed successfully.", caption="Export was successful", style=wx.OK | wx.ICON_INFORMATION)



    wildcard = "Database files (*.bot)|*.bot|All files (*.*)|*.*"
    def OnImport(self, event):
        dlg = wx.FileDialog(self, "Import Bot Settings", os.getcwd(), style=wx.FD_OPEN, wildcard=self.wildcard)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.import_database()
            dlg.Destroy()

    def import_database(self):
        retCode = wx.MessageBox("Are you sure? This action is irreversible and will erase your current settings", caption="Confirm Import", style=wx.YES_NO | wx.ICON_INFORMATION)
        if (retCode == wx.YES):
            import sqlite3
            
            con = sqlite3.connect('bot.db')
            delete_all_tables(con)
            # delete all tables in the db
            f = open(self.filename,'r', encoding="utf-8")
            str = f.read()
            con.executescript(str)
            wx.MessageBox("The import has been completed successfully.",caption="Successful import", style=wx.OK| wx.ICON_INFORMATION)
            # rearrange elements
            self.whatsappPanel.Hide()
            self.box_sizer.Detach(self.whatsappPanel)
            self.whatsappPanel.Destroy()

            self.createPanel()
            self.Refresh()
            self.Layout()






        

    
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


#-------------------------------------------------------------------------
class ScheduleDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'Schedule Messages',
                          size=(450, 150) )

        button = wx.Button(self, wx.ID_OK, "Okay")

        sizer = wx.BoxSizer(wx.VERTICAL)
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Labels
        intervalNameLbl = wx.StaticText(self, -1, "Send messages every: ")
        sampleList = ['15 Minutes', '30 Minutes', '45 Minutes', '1 hour', '75 Minutes', '90 Minutes', '105 Minutes', '2 Hours', '2 and a half hours', '3 Hours', '3 and a half hours', '4 hours', '4 and a half hours', '5 hours', '6 hours', '7 hours', '8 hours', '9 hours', '12 Hours', '24 hours']
        self.interval = wx.ComboBox(self, -1, "30 Minutes", (15, 30), wx.DefaultSize,sampleList, wx.CB_DROPDOWN)
        # Labels
        workloadNameLbl = wx.StaticText(self, -1, "For: ")
        self.workload= wx.ComboBox(self, -1, "2 Hours", (15, 30), wx.DefaultSize,sampleList, wx.CB_DROPDOWN)
        #add combobox to horizontal sizer
        horizontal_sizer.Add(intervalNameLbl, 1, wx.ALL, 5)
        horizontal_sizer.Add(self.interval, 1, wx.ALL, 5)
        horizontal_sizer.Add(workloadNameLbl, 1, wx.ALL, 5)
        horizontal_sizer.Add(self.workload, 1, wx.ALL, 5)
        
        sizer.Add(horizontal_sizer, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(button, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()







#----------------------------------------------------------------------


from datetime import date, datetime, timedelta
class WhatsappBotApp(wx.App):

    def OnInit(self):
        bmp = wx.Image("assets/splash.png").ConvertToBitmap()
        wx.adv.SplashScreen(bmp, wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                1000, None, -1)
        wx.Yield()

        


        frame = WhatsappBotFrame(None)
        self.locale = wx.GetLocale()
        frame.Show(True)
        self.SetTopWindow(frame)
        expiry_date = self.check_expiry()
        
        if (expiry_date > datetime.now()):
            #difference = expiry_date - datetime.now()
            #self.logger.info("Executing trial version. You have %s days remaining.", difference.days)
            return True
        else:
            wx.MessageBox('Your trial period has expired.', 'SharkBot Message Error Box', wx.OK | wx.ICON_ERROR)
            return False
        return True

    def check_expiry(self):
        """checks if trial license is valid, returns expiry date"""
        sell_date = '2022-01-14'
        sell_date = datetime.strptime(sell_date, '%Y-%m-%d')
        expiry_date = sell_date + timedelta(30)
        return expiry_date

if __name__ == '__main__':
    
    app = WhatsappBotApp(False)
    app.MainLoop()