import threading
import socket
import pickle

host_ip = socket.gethostbyname(socket.gethostname())  # host_ip = 127.0.0.1
host_ip = "127.0.0.1"  # Should be synchronized with the clients ip for connection.
print(host_ip)
port = 5050
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host_ip, port))
server.listen()
ACCOUNTS = []  # List of the registered Account objects.
USERNAMES = []  # List of the registered accounts' usernames.
HEADER = 128


class Account:  # A class which represents each account of the platform.
    def __init__(self, username, password):
        self.username = username  # Account's username.
        self.password = password  # Account's password.
        self.friends_list = []  # A list of the account's friends' names.
        self.chats = {}  # A dictionary which includes an account names as keys, and a list of relevant Message objects as values.
        self.client = None  # The specific connection of the account (might change each time the account logging in).
        self.currently_chatting = ""  # The username of the account we are currently talking to.


class Message:  # A class which represents a single message.
    def __init__(self, text, client_name):
        self.text = str(text)  # The message's text.
        self.sender = client_name  # The name of the message's sender.


# Function to handle clients' connections


def SendItem(client, item):  # Function which sends any kind of object to the client by "pickle" library.
    i = pickle.dumps(item)
    client.send(i)  # "i" is Already encoded by pickle.


def ReceiveItem(client):   # Function which gets any kind of object from the client by "pickle" library.
    msg = client.recv(1024)
    i = pickle.loads(msg)
    return i


def handle_client(client):  # The main function which connects between the server and the clients by ...
    # ... receiving messages constantly and sending the relevant data according to each received message.
    global ACCOUNTS
    while True:
        try:
            message = Receive(client)  # Here the server is getting messages constantly from the clients.
            if message == "!Register!":
                print("ClientIsRegistering...")
            elif message == "!CheckRegistering!":  # Checking a registration attempt of a client.
                username = Receive(client)  # Receiving client's username.
                password = Receive(client)  # Receiving client's password.
                if username in USERNAMES:  # If the client's registration username is already exists on the server.
                    print("Bad")
                    Send(client, "!BadUsername!")  # Let the client know he chose an invalid username.
                else:
                    print("Good")
                    Send(client, "!GoodUsername!")  # Let the client know he chose a valid username.
                    USERNAMES.append(username)  # Add the new username to the list USERNAMES.
                    new_acc = Account(username, password)  # Initializing a new Account object for the new account.
                    new_acc.client = client  # Updating the Account object's client.
                    ACCOUNTS.append(new_acc)  # Adding the new Account object to the list ACCOUNTS.
                    for account in ACCOUNTS:
                        for acc in ACCOUNTS:
                            account.chats[acc.username] = []  # For each registered account, adding to its "chats" dictionary a new key and value ...
                            # key: the new username, value: an empty list which would become a Message objects list.

            elif message == "!CheckSigningIn!":  # Checking a registration attempt of a client.
                good_signing_in = False  # Boolean indicator.
                username = Receive(client)  # Receiving client's username.
                password = Receive(client)  # Receiving client's password.
                for account in ACCOUNTS:  # Comparing the specific account details with the previous registered accounts.
                    if account.username == username and account.password == password:  # If username and password are matched to each other.
                        account.client = client  # Updating the current relevant client socket for situations of reconnecting.
                        Send(client, "!GoodSigningIn!")  # Let the client know that the details are correct.
                        good_signing_in = True
                if not good_signing_in:  # If our good_signing_in = False, that means the username/password are wrong.
                    Send(client, "!BadSigningIn!")  # Let the client know the details are wrong.

            elif message == "!Searching!":  # Searching an account by username.
                search_name = Receive(client)  # Receiving the searched name.
                try:
                    Send(client, "!FindingNames!")  # Letting the client know that the server is about to send him the result names.
                    for name in USERNAMES:  # Checking each registered username.
                        if search_name.lower() in name.lower():  # If the searched name is in the username.
                            Send(client, name)  # Sending the result username to the client.
                    Send(client, "!DoneSearching!")  # Letting the client know we finished to search.
                except:
                    print("There isn't any found username.")

            elif message == "!SendProfileInfo!":  # Sending an account's information to the client.
                print("SendProfileInfo")
                profile_username = Receive(client)  # Receiving the wanted profile's username.
                Send(client, "!ProfileInfo!")  # Letting the client know that we're going to send the profile information.
                print("Username:", profile_username)
                for account in ACCOUNTS:  # Checking each registered account's username.
                    print(account.username)
                    if account.username == profile_username:  # If the account's username is the wanted username.
                        Send(client, len(account.friends_list))  # Sending the client the amount of the wanted account's friends.
                        break

            elif message == "!CreateFriendship!":  # The client is creating a friendship.
                client_name = Receive(client)  # Receiving the current client's username.
                profile_name = Receive(client)  # Receiving the other profile's username for friendship creation.
                for account in ACCOUNTS:  # Checking each registered account's username.
                    if account.username == client_name:  # If the account is the current client.
                        if profile_name not in account.friends_list:  # If the profile's username is NOT already on our client's friends list.
                            account.friends_list.append(profile_name)  # Adding the profile username to our client's friends list.
                    elif account.username == profile_name:  # If the account is the profile's account.
                        if client_name not in account.friends_list:  # If the current client's username is NOT already on the profile account's friends list.
                            account.friends_list.append(client_name)  # Adding the current client's username to the profile account's friends list.

            elif message == "!OpenChat!":  # The client is opening a chat with another profile.
                client_name = Receive(client)  # Receiving the current client's username.
                profile_name = Receive(client)  # Receiving the other profile's username.
                for account in ACCOUNTS:
                    print(account.username)
                    if account.username == client_name:
                        account.currently_chatting = profile_name
                        try:
                            chat = account.chats[profile_name]
                            print("Sending Chat ->", chat)
                        except:
                            print("There isn't a chat yet")
                            chat = []
                        Send(client, "!GettingChat!")
                        SendItem(client, chat)

            elif message == "!UpdatingChat!":
                updated_chat = []
                new_message = ReceiveItem(client)
                print("NEW_MESSAGE->", new_message.text, "-", new_message.sender)
                for account in ACCOUNTS:
                    try:
                        if account.username == client_name:
                            if len(account.chats[profile_name]) == 0:  # If there isn't any previous message.
                                account.chats[profile_name].append(Message("                                         ", "DefaultName"))
                            account.chats[profile_name].append(new_message)
                            print(account.username, "Chat With", profile_username, "->")
                            for msg in account.chats[profile_name]:
                                print(msg.text)
                            updated_chat = account.chats[profile_name]
                        elif account.username == profile_name:
                            account.chats[client_name].append(new_message)
                    except Exception as e:
                        print("EXCEPTION -", e)
                for account in ACCOUNTS:
                    print(account.username, "currently chatting", account.currently_chatting, "........")
                    if (account.username == client_name and account.currently_chatting == profile_name) or (account.username == profile_name and account.currently_chatting == client_name):
                        print(0)
                        Send(account.client, "!GetNewChat!")
                        print("Updated", account.username)
                        try:
                            SendItem(account.client, updated_chat)
                        except Exception as e:
                            print("EXCEPTION ->", e)
                        print(1)

            elif message == "!OpenPreviousChats!":
                previous_chats_names = []
                client_name = Receive(client)
                Send(client, "!SendingPreviousNames!")
                print("name:", client_name)
                for acc in ACCOUNTS:
                    if acc.username == client_name:
                        for name in list(acc.chats.keys()):
                            if len(acc.chats[name]) != 0:
                                previous_chats_names.append(name)
                        SendItem(client, previous_chats_names)

        except:
            pass
# Main function to receive the clients connection


def receive():
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        Send(client, '\nyou are now connected!')
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


def Receive(client):
    length = int(client.recv(HEADER).decode("utf-8"))
    real_message = client.recv(length).decode("utf-8")
    return real_message


def Send(client, msg):  # msg is decoded.
    msg = str(msg)
    message = msg.encode("utf-8")
    message_length = str(len(msg)).encode("utf-8")
    message_length += b" " * (HEADER - len(message_length.decode("utf-8")))
    client.send(message_length)
    client.send(message)


if __name__ == "__main__":
    receive()


