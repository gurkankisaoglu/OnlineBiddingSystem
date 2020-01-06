from channels.generic.websocket import WebsocketConsumer
import json

class SockConsumer(WebsocketConsumer):

  waiters = {}
  
  def connect(self):
    print("connectt")
    self.accept()
  
  def disconnect(self,close_code):
    print("disconnected")
    pass

  def receive(self, text_data):
    msg = json.loads(text_data)
    if(msg["op"]=="socket_open"):
      SockConsumer.waiters[msg["user_id"]]=self
    
    self.send(text_data=json.dumps({"msg":"msmsmsmsmmsms"}))