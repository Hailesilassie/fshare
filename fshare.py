from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.metrics import sp,dp
from kivy.uix.label import Label
from kivy.lang import Builder
import threading ,socket
import os
addr = ("localhost",7500)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#server.bind(addr)
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
kv = Builder.load_string("""\
file:

<file@BoxLayout>:
	FileChooserIconView:
		multiselect:True
		id:file
""")

class MainPage(BoxLayout):
      def __init__(self,**kwd):
         super().__init__(**kwd)
         self.box2 = BoxLayout(orientation="horizontal")
         self.orientation = "vertical"
         self.status = Label(font_size=sp(40),size_hint=(1,None),height=80)
         self.send_btn = Button(text="send",font_size=sp(30),size_hint=(None,None),size=(160,80))
         self.send_btn.bind(on_release=self.fchoose)
         self.add_widget(self.status)
         self.anchorS = AnchorLayout(anchor_x="left",anchor_y="bottom",padding=(0,0,0,150))
         self.recv_btn = Button(text="recv",font_size=sp(30),size_hint=(None,None),size=(160,80))
         self.recv_btn.bind(on_release=self.getaddr)
         self.anchorR = AnchorLayout(anchor_x="right",anchor_y="bottom",padding=(0,0,0,150))
         self.anchorS.add_widget(self.send_btn)
         self.anchorR.add_widget(self.recv_btn)
         self.box2.add_widget(self.anchorS)
         self.box2.add_widget(self.anchorR)
         self.add_widget(self.box2)
      def getaddr(self,btn):
         self.addr_box = BoxLayout(orientation = "horizontal")
         self.addr = BoxLayout(orientation="vertical")
         self.addr.spacing = 100
         self.ok_btn = Button(text="Ok",font_size=sp(30),size_hint=(1,None),height=70,pos_hint={'top':1})
         self.ok_btn.bind(on_release=self.ok_resp)
         self.lab = Label(text="Address",font_size=sp(25),size_hint=(.4,None),height=80)
         self.addr_input = TextInput(hint_text="ex.192.168.1.1:7500",font_size=sp(20),size_hint=(.5,None),height=90)
         self.addr_box.add_widget(self.lab)
         self.addr_box.add_widget(self.addr_input)
         self.addr.add_widget(self.addr_box)
         self.addr.add_widget(self.ok_btn)
         self.addr_pop = Popup(title="address",content=self.addr,size_hint=(.6,.6))
         self.addr_pop.open()
      def ok_resp(self,btn):
        print(self.addr_input.text)
        self.addr_pop.dismiss()
        thr3 = threading.Thread(target=self.conn_to)
        thr3.start()
      def conn_to(self):
          try:
            client.connect(('localhost',7500))
          except:
             print("Address Error")
          thr4 = threading.Thread(target=self.recv_file)
          thr4.start()
      def recv_file(self):
          while True:
                finfo = client.recv(1024)
                print(finfo)
                finfo = finfo.decode()
                print(finfo) 
                finfo = finfo.split(";")
                with open(os.path.basename(finfo[0]),"wb") as f:
                     try:
                        fdata = client.recv(int(finfo[1]))
                        f.write(fdata)
                        print("receveing file  content")
                     except:
                         print("recveing file Error")
      def fchoose(self,btn):
         self.content = BoxLayout(orientation="vertical")
         self.select_btn = Button(background_color=(0,0,1,.5),size_hint=(1,None),height=80,text="Select",font_size=sp(35))
         self.content.add_widget(kv)
         self.select_btn.bind(on_release=self.unpop)
         self.content.add_widget(self.select_btn)
         self.pop = Popup(title="Choose File",content=self.content)
         self.pop.open()
      def unpop(self,btn):
        self.select_list = kv.ids.file.selection
        print(self.select_list)
        self.pop.dismiss()
        thr1 = threading.Thread(target=self.make_conn)
        thr1.start()
      def make_conn(self):
          server.bind(addr)
          server.listen()
          self.status.text = f"listeing on {addr}"
          self.conn,self.conn_addr = server.accept()
          self.status.text=f"connected with {self.conn_addr}"
          thr2 = threading.Thread(target=self.send_file)
          thr2.start()
      def send_file(self):
         for i in self.select_list:
                  ii = ";".join([i,str(os.path.getsize(i))])
                  print(ii)
              
                  self.conn.send(ii.encode())
                  print("file info sended")
                  try:
                     with open(i,"rb") as f:
                         fcontent = f.read()
                         print("reading file content")
                     try:
                        self.conn.send(fcontent)
                        print("sending file content")
                        with open(i,"wb")as f:
                            f.write(fcontent)
                     except:
                        print("sending content Error")
                  except:
                     print("file reading Error")
              
class MainApp(App):
     def build(self):
        return MainPage()


if __name__ == "__main__":
    MainApp().run()
