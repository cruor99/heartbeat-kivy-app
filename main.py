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

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class HeartbeatRoot(BoxLayout):
    newstatus = StringProperty("")
    statuscode = StringProperty("")
    devicename = StringProperty("")
    deviceid = StringProperty("")
    client_token = StringProperty(
        "clienttoken")
    pushurl = StringProperty(
        "https://urlhere.pushould.com")

    def __init__(self, **kwargs):
        super(HeartbeatRoot, self).__init__(**kwargs)
        Clock.schedule_once(self.start_thread)

    def start_thread(self, *args):
        self.bind(newstatus=self.do_notify)
        print self.client_token
        pushthread = Thread(target=self.check_pushould)
        pushthread.daemon = True
        pushthread.start()

    def check_pushould(self):
        socketio = SocketIO(
            self.pushurl,
            params={"client_token": str(self.client_token)},
            verify=False)
        socketio.on("send", self.add_status)
        socketio.emit("subscribe", {"room": "TestSecurity"})
        socketio.wait()

    def add_status(self, response):
        self.newstatus = str(response["statusmessage"])
        self.statuscode = str(response["statuscode"])
        self.devicename = str(response["devicename"])
        self.deviceid = str(response["deviceid"])
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
