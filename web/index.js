const express = require('express');
const app = express();
const port = 3000;

const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('main.db')

app.get('/:id', (req, res) => {
    db.each(`SELECT Keyword, CommentText FROM Keywords WHERE SubredditId = ?`, [req.params.id], (err, row) => {
        if (err) {
            throw err;
        }

        console.log(`${row.Keyword} => ${row.CommentText}`)
    })
  res.send('id: ' + req.params.id);
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})