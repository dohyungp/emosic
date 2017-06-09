import random
from passwordhelper import PasswordHelper
from dbhelper import DBHelper
import numpy as np

domains = [ "naver.com", "gmail.com", "daum.net", "hotmail.com", "ncia.com", "yahoo.com"]
letters = [chr(l) for l in range(48, 58)]
letters.extend([chr(l) for l in range(65, 91)])
letters.extend([chr(l) for l in range(97, 123)])
ratings = np.arange(1, 4.5, 0.5).tolist()

def get_one_random_domain(domains):
    return domains[random.randint(0, len(domains)-1)]


def get_one_random_name(letters):
    email_name = ""
    for i in range(random.randint(8, 10)):
        email_name = email_name + letters[random.randint(0, len(letters) - 1)]
    return email_name


def generate_random_users():
    PH = PasswordHelper()
    DB = DBHelper()
    for _ in range(0, 670):
        one_name = str(get_one_random_name(letters))
        one_domain = str(get_one_random_domain(domains))
        email = one_name + "@" + one_domain
        print(email)
        name = one_name
        pw = "123456"
        salt = PH.get_salt()
        hashed = PH.get_hash(pw.encode('utf-8') + salt)
        DB.add_user(email, name, salt, hashed)


def main():
    generate_random_users()


if __name__ == "__main__":
    main()