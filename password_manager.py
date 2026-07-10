import argparse, json, os, getpass, base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VAULT_FILE = "vault.json"

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480000)
    return kdf.derive(password.encode())

def encrypt_data(key: bytes, data: dict, salt: bytes) -> dict:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    plaintext = json.dumps(data).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

def decrypt_data(key: bytes, entry: dict) -> dict:
    aesgcm = AESGCM(key)
    nonce = base64.b64decode(entry["nonce"])
    ciphertext = base64.b64decode(entry["ciphertext"])
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode())

def load_vault(master_password: str):
    try:
        with open(VAULT_FILE, "r") as f:
            vault = json.load(f)
        salt = base64.b64decode(vault["salt"])
        key = derive_key(master_password, salt)
        return vault, key, salt
    except FileNotFoundError:
        salt = os.urandom(16)
        key = derive_key(master_password, salt)
        vault = {"salt": base64.b64encode(salt).decode(), "entries": {}}
        return vault, key, salt

def save_vault(vault: dict):
    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f)

def add_entry(master_password: str):
    vault, key, salt = load_vault(master_password)
    website = input("Website: ")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    entry = {"username": username, "password": password}
    encrypted_entry = encrypt_data(key, entry, salt)
    vault["entries"][website] = encrypted_entry
    save_vault(vault)
    print(f"Entry for {website} added.")

def get_entry(master_password: str, website: str):
    vault, key, salt = load_vault(master_password)
    if website in vault["entries"]:
        entry = vault["entries"][website]
        decrypted = decrypt_data(key, entry)
        print(f"Website: {website}\nUsername: {decrypted['username']}\nPassword: {decrypted['password']}")
    else:
        print("No entry found.")

def list_entries(master_password: str):
    vault, key, salt = load_vault(master_password)
    print("Stored websites:")
    for site in vault["entries"]:
        print("-", site)

def delete_entry(master_password: str, website: str):
    vault, key, salt = load_vault(master_password)
    if website in vault["entries"]:
        del vault["entries"][website]
        save_vault(vault)
        print(f"Entry for {website} deleted.")
    else:
        print("No entry found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Secure Password Manager")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(func=add_entry)

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("website")
    get_parser.set_defaults(func=get_entry)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=list_entries)

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("website")
    delete_parser.set_defaults(func=delete_entry)

    args = parser.parse_args()
    master_password = getpass.getpass("Master Password: ")

    if args.command == "add":
        args.func(master_password)
    elif args.command == "get":
        args.func(master_password, args.website)
    elif args.command == "list":
        args.func(master_password)
    elif args.command == "delete":
        args.func(master_password, args.website)
