const path = require('path');

const dbconnection = require('./utils/db');

const express = require('express');
const bodyParser = require('body-parser');

const app = express();

app.set('view engine', 'ejs');
app.set('views', 'views');

const routes = require('./routes/route');

app.use(express.json());

app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

app.use(routes);

const port = 8000
const host = "localhost"

dbconnection().then(() => {
    app.listen(port, () => {
        console.log(`Server running at http://${host}:${port}/`);
    });
}).catch((error) => {
    console.error("Error starting the server: ", error.message);
});
