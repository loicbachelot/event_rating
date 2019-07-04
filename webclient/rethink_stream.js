var r = require('rethinkdb');
var app = require('http').createServer(handler)
var io = require('socket.io')(app);
var fs = require('fs');

app.listen(1337);

console.log("Running");

function handler(req, res) {
    fs.readFile('./templates/index.html',
        function (err, data) {
            if (err) {
                res.writeHead(500);
                return res.end('Error loading index.html');
            }

            res.writeHead(200);
            res.end(data);
        });
}

io.on('connection', function (socket) {
    socket.on('newMap', function (data) {
        console.log("New map on the system");
        r.connect({host: '', port: 28015}, function (err, conn) {
            if (err) throw err;
            connection = conn;

            r.table('tweets').limit(1000).run(connection, function (err, cursor) {

                if (err) throw err;
                cursor.each(function (err, row) {
                    if (err) throw err;
                    io.emit("oldTweet", JSON.stringify(row, null, 2));
                    console.log(JSON.stringify(row, null, 2))
                });
            });


        });
    });

});

r.connect({host: '', port: 28015}, function (err, conn) {
    if (err) throw err;
    connection = conn;

    r.table('tweets').changes().run(connection, function (err, cursor) {
        if (err) throw err;
        cursor.each(function (err, row) {
            if (err) throw err;
            io.emit("Tweet", JSON.stringify(row, null, 2));
        });
    });


});
