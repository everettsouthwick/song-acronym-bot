const express = require("express");
const app = express();
const port = 3000;

const sqlite3 = require("sqlite3").verbose();
const db = new sqlite3.Database("main.db");

app.get("/:id", (req, res) => {
    const keywords = [];
    db.each(
        `SELECT Keyword, CommentText FROM Keywords WHERE SubredditId = ?`,
        [req.params.id],
        (err, row) => {
            if (err) {
                throw err;
            }
            keywords.push(row);
        },
        (err, i) => {
            if (err) {
                throw err;
            }
            console.log(`Total keywords: ${i}`);
            res.send(keywords.map((keyword) => `<p>${keyword.Keyword}</p>`).join(" "));
        }
    );
});

app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`);
});
