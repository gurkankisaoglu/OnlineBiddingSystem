from channels.generic.websocket import WebsocketConsumer
import json

class SockConsumer(WebsocketConsumer):

  waiters = set()
  
  def connect(self):
    print("connectt")
    SockConsumer.waiters.add(self)
    print([i for i in SockConsumer.waiters])
    self.accept()
  
  def disconnect(self,close_code):
    print("disconnected")
    pass

  def receive(self, text_data):
    print(json.loads(text_data))
    for i in SockConsumer.waiters:
      i.send(text_data=json.dumps({"msg":"broadcasted"}))
    self.send(text_data=json.dumps({"msg":"msmsmsmsmmsms"}))