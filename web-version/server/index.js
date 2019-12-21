var http = require('http');
var fs = require('fs');

//create a server object:
http.createServer(function (req, res) {
    let url = req.url.split("?")[0]
    switch(url) {
        case "/1-14-4_block":
            let dirList = fs.readdirSync("../../1-14-4_block/");

            res.setHeader('Access-Control-Allow-Origin', '*');
            res.writeHead(200, {'Content-Type': 'application/json'});

            res.write(JSON.stringify(dirList));
            res.end();

            break;
            
        case "/get-pixel-value":
            let args = req.url.split("?")[1];
            break;

        default:
            let value = getAveragePixelColour(url);

            res.setHeader('Access-Control-Allow-Origin', '*');
            res.writeHead(200, {'Content-Type': 'application/json'});

            res.write(JSON.stringify(value));
            res.end();

            break;
    }
}).listen(3061);

function getAveragePixelColour(img) {
    let avgColour = {
        "red": -1,
        "green": -1,
        "blue": -1,
        "alpha": -1
    };


}
