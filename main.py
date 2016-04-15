from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty

from threading import Thread

from socketIO_client import SocketIO, LoggingNamespace
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)

from plyer import notification
import sys


class HeartbeatRoot(BoxLayout):
    newstatus = StringProperty("")
    statuscode = StringProperty("")
    devicename = StringProperty("")
    deviceid = StringProperty("")
    client_token = StringProperty(
        "6rgcw2zlr4ubpvcegjajqpnmehx5gp5zm1yigjzp1mgfvy6c")
    pushurl = StringProperty(
        "http://1dvxtg49adq5f5jtzm2a04p2sr2pje3fem1x6gfu2cyhr30p.pushould.com")

    def __init__(self, **kwargs):
        super(HeartbeatRoot, self).__init__(**kwargs)
        Clock.schedule_once(self.start_thread)

    def start_thread(self, *args):
        self.bind(newstatus=self.do_notify)
        pushthread = Thread(target=self.check_pushould)
        pushthread.daemon = True
        pushthread.start()

    def check_pushould(self):
        socketio = SocketIO(self.pushurl,
                            params={"client_token": self.client_token},
                            verify=False)
        socketio.on("send", self.add_status)
        socketio.emit("subscribe",
                      {"room:": "TestSecurity"})
        socketio.wait()

    def add_status(self, response):
        self.newstatus = response["statusmessage"]
        self.statuscode = response["statuscode"]
        self.devicename = response["devicename"]
        self.deviceid = response["deviceid"]
        print response
        print self.newstatus
        sys.stdout.flush()

    def do_notify(self, *args):
        print "Notification received"
        notification.notify(self.devicename, self.newstatus, timeout=50000)


class HeartbeatApp(App):
    def build(self):
        return HeartbeatRoot()

    def on_pause(self):
        True


if __name__ == "__main__":
    HeartbeatApp().run()
