var http = require('http');
var fs = require('fs');
var PNG = require('pngjs').PNG;

//create a server object:
http.createServer(function (req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.writeHead(200, {'Content-Type': 'application/json'});

    let url = decodeURI(req.url.split("?")[0]);
    switch(url) {
        case "/1-14-4_block":
            let dirList = fs.readdirSync("../../1-14-4_block/");

            res.write(JSON.stringify(dirList));
            res.end();

            break;
            
        case "/Redstone Survivalist Skin":
            let pixVal = getAllPixelColours("../../Redstone Survivalist Skin.png");

            res.write(JSON.stringify(pixVal));
            res.end();

            break;

        case "/favicon.ico":
            break;

        default:
            let value = getAveragePixelColour(url);

            res.write(JSON.stringify(value));
            res.end();

            break;
    }
}).listen(3061);

function getAllPixelColours(img) {
    let blockPNG = fs.readFileSync(`${img}`);
    let pixels = {};

    let data = PNG.sync.read(blockPNG);
    let colourData = data.data;
    let imageWidth = data.width;

    for (let c = 0; c < colourData.length; c += 4) {
        let x = parseInt((c / 4)) % (imageWidth);
        let y = parseInt((c / 4) / (imageWidth));

        pixels[`(${x}, ${y})`] = {
            'red': colourData[c],
            'green': colourData[c+1],
            'blue': colourData[c+2],
            'alpha': colourData[c+3]
        }
    }

    return pixels;
}

function getAveragePixelColour(img) {
    let blockPNG = fs.readFileSync(`../../1-14-4_block${img}.png`);
    let avgColour = {
        "red": 0,
        "green": 0,
        "blue": 0,
        "alpha": 0
    };

    let data = PNG.sync.read(blockPNG);
    let colourData = data.data;
    let imageArea = data.width * data.height;

    for (let c = 0; c < colourData.length; c++) {
        switch (c % 4) {
            case 0:
                avgColour.red += colourData[c] / imageArea;
                break;

            case 1:
                avgColour.green += colourData[c] / imageArea;
                break;

            case 2:
                avgColour.blue += colourData[c] / imageArea;
                break;

            case 3:
                avgColour.alpha += colourData[c] / imageArea;
                break;
        }
    }

    return avgColour;
}

