from Client import Client
import time

user1 = Client()

user2 = Client()

user3 = Client()

print("register user1")
user1.register("new@mail.com", "name surname", "password123", 1000)

print("register user2")
user2.register("user@mail.com", "user surname", "password125", 10000)

print("register user3")
user3.register("watcher@mail.com", "watch surname", "password125", 0)


print("verify user1")
user1.verify()

print("verify user2")
user2.verify()

print("verify user3")
user3.verify()

print("user3 watch")
user3.watch_user("araba")

time.sleep(1)

print("create user1")
user1.create_item("car", "araba", "egea", ("increment", 5, 1000), 10)

print("user3 watch car")
user3.watch("car")

print("user2 bid")
user2.bid("car", 500)

print("user1 start auc")
user1.start_auction("car")

print("user2 bid")
user2.bid("car", 700)

print("user2 bid")
user2.bid("car", 1000)

time.sleep(1)

user1.close()
user2.close()
user3.close()