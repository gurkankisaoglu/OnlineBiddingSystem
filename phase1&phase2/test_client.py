from Client import Client
import time

user1 = Client()

user2 = Client()

user3 = Client()

print("register user1")
user1.register("new@mail.com", "name surname", "password123", 1000)

print("\nregister user2")
user2.register("user@mail.com", "user surname", "password125", 10000)

print("\nregister user3")
user3.register("watcher@mail.com", "watch surname", "password125", 900)

print("\nverify user1")
user1.verify()

print("\nverify user2")
user2.verify()

print("\nverify user3")
user3.verify()

print("\nuser3 watch")
user3.watch_user("araba")

time.sleep(1)

print("\ncreate user1")
user1.create_item("car", "araba", "egea", ("increment", 5, 1000), 10)

print("\nuser1 list_items")
user1.list_items(user1.email, "araba")

print("\nuser3 watch car")
user3.watch("car")

print("\nuser2 bid")
user2.bid("car", 500)

print("\nuser1 start auc")
user1.start_auction("car")

print("\nuser2 bid")
user2.bid("car", 700)

print("\nuser3 bid")
user3.bid("car", 850)

print("\nuser2 bid")
user2.bid("car", 1000)

print("\nuser reports")
user1.report()
user2.report()
user3.report()

print("\nview of car item")
user1.view('car')

time.sleep(1)

user1.close()
user2.close()
user3.close()