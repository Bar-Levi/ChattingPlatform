import threading
import socket
import pickle
from tkinter import *
from tkinter import ttk


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = "127.0.0.1"  # Should be synchronized with the relevant server ip.
client.connect((server_ip, 5050))
BACKGROUND_COLOR = "light blue"
CLIENT_MSG_COLOR = "#288aeb"
PROFILE_MSG_COLOR = "gray"
CHAT_TEXT_COLOR = "#f2f2f2"
window = Tk()
SCREEN_WIDTH = window.winfo_screenwidth()
SCREEN_HEIGHT = window.winfo_screenheight()
window.title("Chatting Platform - by Bar Levi")
window.resizable(False, False)
window.config(bg=BACKGROUND_COLOR)
RETURN_ICON = PhotoImage(file="Assets/backward.png")
MSG_MAX_LEN = 35


def CenterWindow(win):
    center_x = int(SCREEN_WIDTH / 2 - win.winfo_reqwidth() / 2)
    center_y = int(SCREEN_HEIGHT / 2 - win.winfo_reqheight() / 2)
    return '+' + center_x + '+' + center_y  # Placing the window at the middle of the screen.


window.geometry(CenterWindow(window))  # Placing the window at the middle of the screen.
status = {"Menu": 1, "Register": 0, "SignIn": 0, "Home": 0, "Search": 0, "PreviousChats": 0, "Profile": 0, "Chat": 0}
bad_username = False
found = False
signed_in = False
registered = False
invalid_message = False
search_results = []
HEADER = 128
CURRENT_CLIENT_NAME = None
PROFILE = {"name": None, "friends_count": None}
CURRENT_CHAT = []
previous_chats_names = []  # A list of names.


class Message:
    def __init__(self, text, client_name):
        self.text = str(text)
        self.sender = client_name  # Name of the message's sender.


def Receive():
    length = int(client.recv(HEADER).decode("utf-8"))
    real_message = client.recv(length).decode("utf-8")
    return real_message


def Send(msg):  # msg is decoded.
    message = msg.encode("utf-8")
    message_length = str(len(msg)).encode("utf-8")
    message_length += b" " * (HEADER - len(message_length.decode("utf-8")))
    client.send(message_length)
    client.send(message)


def SendItem(item):
    i = pickle.dumps(item)
    client.send(i)  # Already encoded by pickle.


def ReceiveItem():
    msg = client.recv(1024)
    i = pickle.loads(msg)
    return i


def client_receive():
    global bad_username, status, search_results, PROFILE, CURRENT_CHAT, registered, signed_in, previous_chats_names
    while True:
        try:
            message = Receive()  # Where the client is getting messages constantly.
            if message == "!GoodUsername!":
                registered = True
                signed_in = False
                bad_username = False
                print("!GoodUsername!")
                status["Register"] = 0
                status["Home"] = 1
                HandleWindows()
            elif message == "!BadUsername!":
                print("!BadUsername!")
                bad_username = True
                HandleWindows()
            elif message == "!GoodSigningIn!":
                registered = False
                signed_in = True
                bad_username = False
                print("!GoodUsername!")
                status["SignIn"] = 0
                status["Home"] = 1
                HandleWindows()
            elif message == "!BadSigningIn!":
                print("!BadUsername!")
                bad_username = True
                HandleWindows()
            elif message == "!FindingNames!":
                search_results = []
                result = Receive()
                while result != "!DoneSearching!":
                    print(result)
                    search_results.append(result)
                    result = Receive()
                HandleWindows()
            elif message == "!ProfileInfo!":
                PROFILE["friends_count"] = Receive()
                status["Search"] = 0
                status["Profile"] = 1
                HandleWindows()
            elif message == "!GettingChat!":  # Opening the chat.
                CURRENT_CHAT = ReceiveItem()
                print("Getting Chat ->", CURRENT_CHAT)
                status["Profile"] = 0
                status["PreviousChats"] = 0
                status["Chat"] = 1
                HandleWindows()
            elif message == "!GetNewChat!":  # Updating the chat.
                print("!GetNewChat!")
                CURRENT_CHAT = ReceiveItem()
                HandleWindows()
            elif message == "!SendingPreviousNames!":
                previous_chats_names = ReceiveItem()  # Getting a list of names.
            elif message != "":
                print("Message is :", message)

        except:
            pass
            # client.close()


def SendRegister():
    status["Menu"] = 0
    status["Register"] = 1
    HandleWindows()


def SendSignIn():
    status["Menu"] = 0
    status["SignIn"] = 1
    HandleWindows()


receive_thread = threading.Thread(target=client_receive)
receive_thread.start()


def ShowProfile(name):
    Send("!SendProfileInfo!")
    Send(name)
    PROFILE["name"] = name


def OpenChat():
    Send("!OpenChat!")
    Send(CURRENT_CLIENT_NAME)
    Send(PROFILE["name"])


def HandleWindows():
    print(status)
    # ------------------------------------------------  Menu Window  --------------------------------------------------
    if status["Menu"]:
        for feature in window.winfo_children():
            feature.pack_forget()
        Label(window, text="Welcome to Chatting!", font=('David', 20, 'underline'), bg=BACKGROUND_COLOR).pack()
        register_button = Button(window, text="Register", command=SendRegister, highlightbackground=BACKGROUND_COLOR)
        sign_in_button = Button(window, text="Sign In", command=SendSignIn, highlightbackground=BACKGROUND_COLOR)
        register_button.pack()
        sign_in_button.pack()

    # ------------------------------------------------  Registering Window  -------------------------------------------
    if status["Register"]:
        for feature in window.winfo_children():
            feature.pack_forget()

        def BackToMenu():
            status["Register"] = 0
            status["Menu"] = 1
            HandleWindows()

        return_button = Button(window, image=RETURN_ICON, command=BackToMenu, highlightbackground=BACKGROUND_COLOR).pack(anchor="w")
        Label(window, text="Register", font=('David', 20, 'underline'), bg=BACKGROUND_COLOR).pack()
        username_label = Label(window, text="Username:", font=('David', 12, 'underline'), bg=BACKGROUND_COLOR)
        username_label.pack()
        username_textbox = Entry(window, bg="white", highlightbackground=BACKGROUND_COLOR)
        username_textbox.pack()
        password_label = Label(window, text="Password:", font=('David', 12, 'underline'), bg=BACKGROUND_COLOR)
        password_label.pack()
        password_textbox = Entry(window, bg="white", highlightbackground=BACKGROUND_COLOR)
        password_textbox.pack()
        if bad_username:
            error_label = Label(window, text="Username is already taken, please try a different one.", fg="red", bg=BACKGROUND_COLOR)
            error_label.pack()

        def SubmitRegistering():
            global CURRENT_CLIENT_NAME
            Send("!CheckRegistering!")
            CURRENT_CLIENT_NAME = username_textbox.get()
            Send(CURRENT_CLIENT_NAME)
            Send(password_textbox.get())

        submit_button = Button(window, text="Submit", command=SubmitRegistering, highlightbackground=BACKGROUND_COLOR)
        submit_button.pack()

    # ------------------------------------------------  Signing In Window  --------------------------------------------
    if status["SignIn"]:
        for feature in window.winfo_children():
            feature.pack_forget()

        def BackToMenu():
            status["SignIn"] = 0
            status["Menu"] = 1
            HandleWindows()

        return_button = Button(window, image=RETURN_ICON, command=BackToMenu, highlightbackground=BACKGROUND_COLOR).pack(anchor="w")
        Label(window, text="Sign In", font=('David', 20, 'underline'), bg=BACKGROUND_COLOR).pack()
        username_label = Label(window, text="Username:", font=('David', 12, 'underline'), bg=BACKGROUND_COLOR)
        username_label.pack()
        username_textbox = Entry(window, bg="white", highlightbackground=BACKGROUND_COLOR)
        username_textbox.pack()
        password_label = Label(window, text="Password:", font=('David', 12, 'underline'), bg=BACKGROUND_COLOR)
        password_label.pack()
        password_textbox = Entry(window, bg="white", highlightbackground=BACKGROUND_COLOR)
        password_textbox.pack()
        if bad_username:
            error_label = Label(window, text="Username/password is not valid, please try again.", fg="red", bg=BACKGROUND_COLOR)
            error_label.pack()

        def SubmitSigningIn():
            global CURRENT_CLIENT_NAME
            Send("!CheckSigningIn!")
            CURRENT_CLIENT_NAME = username_textbox.get()
            Send(CURRENT_CLIENT_NAME)
            Send(password_textbox.get())

        submit_button = Button(window, text="Submit", command=SubmitSigningIn, highlightbackground=BACKGROUND_COLOR)
        submit_button.pack()

    # ------------------------------------------------  Home Window  --------------------------------------------------
    if status["Home"]:
        for feature in window.winfo_children():
            feature.pack_forget()

        def BackToRegOrSign():
            status["Home"] = 0
            if signed_in:
                status["SignIn"] = 1
            if registered:
                status["Register"] = 1
            HandleWindows()

        return_button = Button(window, image=RETURN_ICON, command=BackToRegOrSign, highlightbackground=BACKGROUND_COLOR).pack(anchor="w")
        Label(window, text="Options", font=('David', 20, 'underline'), bg=BACKGROUND_COLOR).pack()

        def GoToSearch():
            status["Home"] = 0
            status["Search"] = 1
            HandleWindows()

        def GoToPreviousChats():
            status["Home"] = 0
            status["PreviousChats"] = 1
            HandleWindows()

        search_button = Button(window, text="Search friends", bg="light gray", command=GoToSearch, highlightbackground=BACKGROUND_COLOR)
        search_button.pack()
        chats_button = Button(window, text="Previous Chats", bg="light gray", command=GoToPreviousChats, highlightbackground=BACKGROUND_COLOR)
        chats_button.pack()

    # ------------------------------------------------  Search Window  ------------------------------------------------
    if status["Search"]:
        for feature in window.winfo_children():
            feature.pack_forget()

        def BackToHome():
            status["Search"] = 0
            status["Home"] = 1
            HandleWindows()

        return_button = Button(window, image=RETURN_ICON, command=BackToHome, highlightbackground=BACKGROUND_COLOR).pack(anchor="w")
        Label(window, text="Search", font=('David', 20, 'underline'), bg=BACKGROUND_COLOR).pack()
        search_label = Label(window, text="Enter a name to search", bg=BACKGROUND_COLOR)
        search_label.pack()
        search_textbox = Entry(window, bg="white", highlightbackground=BACKGROUND_COLOR)
        search_textbox.pack()

        def SubmitSearching():
            global found
            print("SubmitSearching")
            found = True
            Send("!Searching!")
            username = search_textbox.get()
            Send(username)

        submit_button = Button(window, text="Search", command=SubmitSearching, highlightbackground=BACKGROUND_COLOR)
        submit_button.pack()
        if found:
            found_names_label = Label(window, text="Search results:", bg=BACKGROUND_COLOR)
            found_names_label.pack()
        for result in search_results:
            print("result:", result)
            result_button = Button(window, text=result, command=lambda name=result: ShowProfile(name), highlightbackground=BACKGROUND_COLOR)
            result_button.pack()

    # ------------------------------------------------  Chats Window  -------------------------------------------------
    if status["PreviousChats"]:
        for feature in window.winfo_children():
            feature.pack_forget()

        def BackToHome():
            status["PreviousChats"] = 0
            status["Home"] = 1
            HandleWindows()

        return_button = Button(window, image=RETURN_ICON, command=BackToHome, highlightbackground=BACKGROUND_COLOR)
        return_button.pack(anchor="w")
        header = Label(window, text="Previous Chats", font=('David', 20, 'underline'), bg=BACKGROUND_COLOR)
        header.pack()
        Send("!OpenPreviousChats!")
        Send(CURRENT_CLIENT_NAME)

        def OpenPreviousChat(name):
            PROFILE["name"] = name
            OpenChat()

        if len(previous_chats_names) == 0:
            Label(window, text="There aren't any previous chats", bg=BACKGROUND_COLOR).pack()
        else:
            for name in previous_chats_names:
                if name != CURRENT_CLIENT_NAME:
                    Button(window, text=name, highlightbackground=BACKGROUND_COLOR, command=lambda x=name: OpenPreviousChat(x)).pack()

    # ------------------------------------------------  Profile Window  -----------------------------------------------
    if status["Profile"]:
        print("Profile is:", PROFILE)
        for feature in window.winfo_children():
            feature.pack_forget()

        def BackToSearch():
            status["Profile"] = 0
            status["Search"] = 1
            HandleWindows()

        return_button = Button(window, image=RETURN_ICON, command=BackToSearch, highlightbackground=BACKGROUND_COLOR).pack(anchor="w")
        Label(window, text=PROFILE['name'] + "'s Profile", font=('David', 20, 'underline'), bg=BACKGROUND_COLOR).pack()
        header_label = Label(window, text=PROFILE['name'] + "'s Profile", bg=BACKGROUND_COLOR)
        header_label.pack()
        friends_label = Label(window, text="Friends: " + PROFILE["friends_count"], bg=BACKGROUND_COLOR)
        friends_label.pack()

        def CreateFriendship():
            Send("!CreateFriendship!")
            Send(CURRENT_CLIENT_NAME)
            Send(PROFILE["name"])

        add_friend_button = Button(window, text="Add friend", bg="light gray", command=CreateFriendship, highlightbackground=BACKGROUND_COLOR)
        add_friend_button.pack()
        open_chat_button = Button(window, text="Open chat", bg="light gray", command=OpenChat, highlightbackground=BACKGROUND_COLOR)
        open_chat_button.pack()

    # ------------------------------------------------  Chat Window  --------------------------------------------------
    if status["Chat"]:
        for feature in window.winfo_children():
            feature.pack_forget()

        def BackToProfile():
            status["Chat"] = 0
            status["Profile"] = 1
            HandleWindows()

        return_button = Button(window, image=RETURN_ICON, command=BackToProfile, highlightbackground=BACKGROUND_COLOR).pack(anchor="w")
        Label(window, text="Chat with "+ PROFILE['name'], font=('David', 20, 'underline'), bg=BACKGROUND_COLOR).pack()
        wrapper = LabelFrame(window)
        my_canvas = Canvas(wrapper)
        my_canvas.pack(side=LEFT)
        yscrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=my_canvas.yview)
        yscrollbar.pack(side=RIGHT, fill="y")
        my_canvas.config(yscrollcommand=yscrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.config(scrollregion=my_canvas.bbox('all')))
        my_frame = Frame(my_canvas)
        my_canvas.create_window((0, 0), window=my_frame, anchor="nw")
        wrapper.pack(fill="both", expand="yes", padx=10, pady=10)
        window_width = 79  # Constant
        label = Label(my_frame, text=" " * window_width, fg=CHAT_TEXT_COLOR)
        label.pack(anchor='e')
        chat_length = len(CURRENT_CHAT)
        if chat_length < 9:
            for _ in range(9 - chat_length):
                label = Label(my_frame)
                label.pack()
        for msg in CURRENT_CHAT:
            if msg.sender == CURRENT_CLIENT_NAME:
                label = Label(my_frame, text=msg.text, bg=CLIENT_MSG_COLOR, fg=CHAT_TEXT_COLOR)
                label.pack(anchor='w')
            elif msg.sender == PROFILE['name']:
                label = Label(my_frame, text=msg.text, bg=PROFILE_MSG_COLOR, fg=CHAT_TEXT_COLOR)
                label.pack(anchor='e')
        textbox = Entry(window, bg="white", highlightbackground=BACKGROUND_COLOR)
        textbox.pack()

        def SendMessage():
            global CURRENT_CHAT, invalid_message
            if 0 < len(textbox.get()) <= MSG_MAX_LEN:  # A message got to be 1-35 letters long.
                invalid_message = False
                print("CURRENT_CHAT ->", CURRENT_CHAT)
                Send("!UpdatingChat!")
                SendItem(Message(textbox.get(), CURRENT_CLIENT_NAME))
            else:
                invalid_message = True
                HandleWindows()

        send_button = Button(window, text="Send", command=SendMessage, highlightbackground=BACKGROUND_COLOR)
        send_button.pack()
        over_length_label = Label(window, text="Your message should be 1-35 letters long.", fg="red", bg=BACKGROUND_COLOR)
        if invalid_message:
            over_length_label.pack()
        my_canvas.update_idletasks()
        my_canvas.yview_moveto('1.0')  # Sticking the scroll tab to the bottom when opening the window.


    window.mainloop()


HandleWindows()
