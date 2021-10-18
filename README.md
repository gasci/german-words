# german

Try out my weekend project to practice German and NoSQL with Flask:

https://de-words.herokuapp.com/

Using a NoSQL database benefits when you need just one type of database object with varying fields. For example, a noun has "artikel" and "plural" fields whereas a verb has a "perfect" field. With NoSQL, instead of defining two models ("noun", "verb"), it is enough to define just one "word" model since the entries can accept different types of fields just like a JSON object.

The project is a simple but powerful replica of Anki.

The complete tech stack: MongoDB, Flask, Bootstrap, jQuery.
