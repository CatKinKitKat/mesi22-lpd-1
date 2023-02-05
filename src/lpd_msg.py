#!/usr/bin/env python3

import argparse
import csv
import datetime
import os

import cryptography
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_signing_key_pair():
    key = cryptography.hazmat.primitives.asymmetric.ed25519.Ed25519PrivateKey.generate()
    private_key_bytes = key.private_bytes(
        encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
        format=cryptography.hazmat.primitives.serialization.PrivateFormat.PKCS8,
        encryption_algorithm=cryptography.hazmat.primitives.serialization.NoEncryption()
    )
    private_key: str = private_key_bytes.decode("utf-8")
    public_key: str = private_key.public_key().public_bytes(
        encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
        format=cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, public_key


def generate_encryption_key_pair():
    key = cryptography.hazmat.primitives.asymmetric.rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=cryptography.hazmat.backends.default_backend()
    )
    private_key_bytes = key.private_bytes(
        encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
        format=cryptography.hazmat.primitives.serialization.PrivateFormat.PKCS8,
        encryption_algorithm=cryptography.hazmat.primitives.serialization.NoEncryption()
    )
    private_key: str = private_key_bytes.decode("utf-8")
    public_key: str = private_key.public_key().public_bytes(
        encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,
        format=cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, public_key


def sign_message(message, private_signing_key: str):
    key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
        private_signing_key,
        password=None,
        backend=cryptography.hazmat.backends.default_backend()
    )
    signature = key.sign(message)
    return signature


def verify_signature(message, signature, public_signing_key: str):
    key = cryptography.hazmat.primitives.serialization.load_pem_public_key(
        public_signing_key,
        backend=cryptography.hazmat.backends.default_backend()
    )
    try:
        key.verify(
            signature,
            message
        )
        return True
    except cryptography.exceptions.InvalidSignature:
        return False


def encrypt_message(message, public_encryption_key: str):
    key = cryptography.hazmat.primitives.serialization.load_pem_public_key(
        public_encryption_key,
        backend=cryptography.hazmat.backends.default_backend()
    )
    encrypted_message = key.encrypt(
        message,
        cryptography.hazmat.primitives.asymmetric.padding.OAEP(
            mgf=cryptography.hazmat.primitives.asymmetric.padding.MGF1(
                algorithm=cryptography.hazmat.primitives.hashes.SHA256()),
            algorithm=cryptography.hazmat.primitives.hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message


def decrypt_message(encrypted_message, private_encryption_key: str):
    key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
        private_encryption_key,
        password=None,
        backend=cryptography.hazmat.backends.default_backend()
    )
    message = key.decrypt(
        encrypted_message,
        cryptography.hazmat.primitives.asymmetric.padding.OAEP(
            mgf=cryptography.hazmat.primitives.asymmetric.padding.MGF1(
                algorithm=cryptography.hazmat.primitives.hashes.SHA256()),
            algorithm=cryptography.hazmat.primitives.hashes.SHA256(),
            label=None
        )
    )
    return message


def create_user(name: str):
    private_signing_key, public_signing_key = generate_signing_key_pair()
    private_encryption_key, public_encryption_key = generate_encryption_key_pair()

    if not os.path.exists("users"):
        os.mkdir("users")
    if not os.path.exists("users/users.csv"):
        with open("users/users.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "id", "public_signing_key", "public_encryption_key"])
    with open("users/users.csv", "r") as file:
        reader = csv.reader(file)
        users = list(reader)
        id = len(users)
    with open("users/users.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow([name, id, public_signing_key, public_encryption_key])

    with open(name + "_private_signing_key.pem", "w") as file:
        file.write(private_signing_key)
    with open(name + "_private_encryption_key.pem", "w") as file:
        file.write(private_encryption_key)
    return private_signing_key, private_encryption_key

    print("User created with id" + id)
    print("Keys saved in", name + "_private_signing_key.pem", "and", name + "_private_encryption_key.pem")
    print("Please keep them safe and don't share them with anyone")


def send_message(user1: str, user2: str, private_signing_key: str, message: str):
    if not os.path.exists("chats"):
        os.mkdir("chats")
    if not os.path.exists("chats/" + user1 + "_" + user2 + ".csv"):
        with open("chats/" + user1 + "_" + user2 + ".csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["to", "from", "message", "signature", "timestamp"])

    with open("users/users.csv", "r") as file:
        reader = csv.reader(file)
        users = list(reader)
        for user in users:
            if user[0] == user2:
                public_encryption_key = user[3]
                break
        else:
            raise Exception("User not found")

    encrypted_message = encrypt_message(message.encode("utf-8"), public_encryption_key)

    signature = sign_message(encrypted_message, private_signing_key)

    with open("chats/" + user1 + "_" + user2 + ".csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow([user1, user2, encrypted_message, signature, datetime.datetime.now()])

    print("Message sent")


def receive_chat_bulk(user1: str, user2: str, private_encryption_key: str):
    if not os.path.exists("chats"):
        os.mkdir("chats")
    if not os.path.exists("chats/" + user1 + "_" + user2 + ".csv"):
        with open("chats/" + user1 + "_" + user2 + ".csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["to", "from", "message", "signature"])

    with open("users/users.csv", "r") as file:
        reader = csv.reader(file)
        users = list(reader)
        for user in users:
            if user[0] == user2:
                public_signing_key = user[2]
                public_encryption_key = user[3]
                break
        else:
            raise Exception("User not found")

    with open("chats/" + user1 + "_" + user2 + ".csv", "r") as file:

        reader = csv.reader(file)

        decrypted_messages = []
        for message in reader:
            if message[0] == user1 and message[1] == user2:
                if verify_signature(message[2], message[3], public_signing_key):
                    decrypted_messages.append(decrypt_message(message[2], private_encryption_key).decode("utf-8"))
            elif message[0] == user2 and message[1] == user1:
                if verify_signature(message[2], message[3], public_signing_key):
                    decrypted_messages.append(decrypt_message(message[2], private_encryption_key).decode("utf-8"))

    return decrypted_messages


def receive_chat(user1: str, user2: str, private_encryption_key: str):
    if not os.path.exists("chats"):
        os.mkdir("chats")
    if not os.path.exists("chats/" + user1 + "_" + user2 + ".csv"):
        with open("chats/" + user1 + "_" + user2 + ".csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["to", "from", "message", "signature"])

    with open("users/users.csv", "r") as file:
        reader = csv.reader(file)
        users = list(reader)
        for user in users:
            if user[0] == user2:
                public_signing_key = user[2]
                public_encryption_key = user[3]
                break
        else:
            raise Exception("User not found")

    with open("chats/" + user1 + "_" + user2 + ".csv", "r") as file:

        reader = csv.reader(file)
        next(reader)

        message = list(reader)[-1]

        if message[0] == user1 and message[1] == user2:
            print("Message received from", user2)
            if verify_signature(message[2], message[3], public_signing_key):
                decrypted_message = decrypt_message(message[2], private_encryption_key).decode("utf-8")
        elif message[0] == user2 and message[1] == user1:
            print("Message sent from you to", user2)
            if verify_signature(message[2], message[3], public_signing_key):
                decrypted_message = decrypt_message(message[2], private_encryption_key).decode("utf-8")

    return decrypted_message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--help", help="show this help message and exit", action="store_true")
    parser.add_argument("-r", "--register", help="register a new user", action="store_true")
    parser.add_argument("-s", "--send", help="send a message to a user", action="store_true")
    parser.add_argument("-b", "--bulk", help="receive all messages from a user", action="store_true")
    parser.add_argument("-l", "--last", help="receive the last message from a user", action="store_true")
    parser.add_argument("-t", "--to", help="the user to send the message to")
    parser.add_argument("-u", "--username", help="the username of the user")
    parser.add_argument("-m", "--message", help="the message to send")
    parser.add_argument("-z", "--sign-key", help="the path to the signing key")
    parser.add_argument("-x", "--enc-key", help="the path to the encryption key")
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        exit()

    if args.register:
        if not args.username:
            print("Please specify the username")
            exit()
        else:
            username = args.username
            create_user(username)
            exit()

    if args.send:
        if not args.username:
            print("Please specify the username")
            exit()
        elif not args.to:
            print("Please specify the user to send the message to")
            exit()
        elif not args.message:
            print("Please specify the message to send")
            exit()
        elif not args.sign_key:
            print("Please specify the path to the signing key")
            exit()

        username = args.username
        to = args.to
        message = args.message
        sign_key = args.sign_key

        send_message(username, to, message, sign_key)

    if args.last:
        if not args.username:
            print("Please specify the username")
            exit()
        elif not args.to:
            print("Please specify the user to receive the message from")
            exit()
        elif not args.enc_key:
            print("Please specify the path to the encryption key")
            exit()

        username = args.username
        to = args.to
        enc_key = args.enc_key

        print(receive_chat(username, to, enc_key))

    if args.bulk:
        if not args.username:
            print("Please specify the username")
            exit()
        elif not args.to:
            print("Please specify the user to receive the messages from")
            exit()
        elif not args.enc_key:
            print("Please specify the path to the encryption key")
            exit()

        username = args.username
        to = args.to
        enc_key = args.enc_key

        print(receive_chat_bulk(username, to, enc_key))


if __name__ == "__main__":
    main()
