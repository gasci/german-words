# german

## Introduction
Try out my weekend project to practice German and NoSQL with Flask:

https://de-words.herokuapp.com/

Using a NoSQL database benefits when you need just one type of database object with varying fields. For example, a noun has "artikel" and "plural" fields whereas a verb has a "perfect" field. With NoSQL, instead of defining two models ("noun", "verb"), it is enough to define just one "word" model since the entries can accept different types of fields just like a JSON object.

* The project is a simple but powerful replica of Anki.
* The complete tech stack: `MongoDB, Flask, Bootstrap, jQuery`.

## Local development
The following environment variables are required in a `.env` file:

```bash
# mongodb connection configuration
MONGO_CLI_USERNAME
MONGO_CLI_DATABASE
MONGO_CLI_PW
MONGO_CLI_CLUSTER

# secret key for the flask server
FLASK_SECRET_KEY

# allow registration
CAN_REGISTER=True
```

```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

