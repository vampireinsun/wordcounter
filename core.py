import requests
import json
import os

from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from Crypto import Random

from utils import read_content_from_file, write_content_to_file


class WordFilter(object):
    """
    The purpose of class is for filtering un-wanted word for counter
    current simple implementation is to put the un-wanted word in a txt file
    """

    def __init__(self, dict_file):
        self.dict_file = dict_file
        self.unwanted_words_list = json.loads(read_content_from_file(self.dict_file)) or []

    def is_wanted(self, word):
        return word not in set(self.unwanted_words_list)


class InvalidWebURL(Exception):
    pass


class RequestWebContentFailure(Exception):
    pass


class WedPageWordCounter(object):

    def __init__(self, word_filter):
        self.word_filter = word_filter

    def _counting_words(self, content, top_n):
        word_counter = {}
        soup = BeautifulSoup(content, "lxml")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        for word_line in chunks:
            words = word_line.split(" ")
            for word in words:
                word = word.strip("()*-_ ^.!;:\n\t\"").lower()
                if word and self.word_filter.is_wanted(word):
                    if word not in word_counter:
                        word_counter[word] = 0
                    word_counter[word] += 1

        word_counter = sorted(word_counter.items(), key=lambda item: item[1], reverse=True)
        if len(word_counter) <= top_n:
            return word_counter
        else:
            return word_counter[:top_n]

    def start_scan(self, web_url, top_n=100):
        if not web_url:
            raise InvalidWebURL("Invalid URL")

        response = requests.get(web_url)
        if response.status_code == 200:
            return self._counting_words(response.content, top_n)
        else:
            raise RequestWebContentFailure("Failed to retrieve the web content {}.".format(str(response.status_code)))


class SimpleEncryption(object):

    def __init__(self, key_store_location):
        self.public_key = None
        self.private_key = None
        self.key_store_location = key_store_location
        self._load_keys()

    def _load_keys(self):
        required_create_new = True
        if os.path.exists(self.key_store_location):
            try:
                self.public_key = RSA.importKey(read_content_from_file(
                        os.path.join(self.key_store_location, "public_key")))
                self.private_key = RSA.importKey(read_content_from_file(
                        os.path.join(self.key_store_location, "private_key")))
                required_create_new = False
            except Exception:
                pass

        if required_create_new:
            random_generator = Random.new().read
            key = RSA.generate(1024, random_generator)
            write_content_to_file(os.path.join(self.key_store_location, "public_key"),
                                  key.publickey().exportKey())
            write_content_to_file(os.path.join(self.key_store_location, "private_key"),
                                  key.exportKey())
            self.public_key = key.publickey()
            self.private_key = key

    def encrypt_content(self, content):
        enc_data = self.public_key.encrypt(str(content), 32)
        return enc_data[0]

    def decrypt_content(self, content):
        return self.private_key.decrypt(content)

