Python environment
==================
Python: 2.7..9
OS: passed on Mac, not try on other OS but suppose it should be fine.

Python packages:
beautifulsoup4
tornado
pycrypto
MySQL-python
requests
lxml
sqlalchemy
Use the following command to install them
>pip install -r ./requirements.txt


The solution
==============
The current implementation is to use tornado as web server with the following components
- word_counting_server.py:   The tornado web server running on 8000 by default, but can be changed
- core.py:
   1. The main classs for handling counting the word on a web page
   2. A web words filter for filtering the words we are interested, currently it is very simple solution by defining
      unwanted words in a json file, the real solution can be more complicated
   3. A class for handking encryption and decryption
- settings.py:  The basic configuratin in the project
- db_models.py: The domain model for storing the result into database
- utils.py:  some shared common functions
- static folder
   1. Static css
   2. keys file
   3. html pages and templates

The current structure demos the possible structure in real solution, may look like unnecessary complicated.

The questions
==============
How to keep the keys for encryption a decryption safer?
I would think it will be combination of the way of creating them and using them, how to manage them
- Store them separately
- Use a sequence of pairing keys for different content rather than using a singele pairing key
- Change them from time to time
- "Encry" or hash the keys when storing them.


How to run
==========
>python <path to word_countng_server.py>
>python word_countng_server.py

The home page will be
http://<server address>:8000/index/
e.g. http://localhost:8000/index/


If you want to change the database connection, please change the following definition in settings.py
SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost:3306/words'