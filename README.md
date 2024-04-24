***Rumor Server***

This repository stores all code living on the server side of things for the Rumor chat application.

Language: Python

Network Protocol: UDP

The entry point of this code lives in Server.py. Once the server is started a UDP handler is created and it waits for incoming network requests from the chat clients. These requests consist of creating chats and sending messages between users.
