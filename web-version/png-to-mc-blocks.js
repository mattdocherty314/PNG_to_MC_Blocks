function pageLoad() {
    let runButton = document.getElementById("run");
    runButton.addEventListener("click", main);
}

async function main() {
    let output = document.getElementById("output");
    let blocksTextArea = document.getElementById("blocks");
    blocksTextArea.innerHTML = "";

    let blocks = await getListOfBlocks();
    output.innerHTML = "Got list of blocks...<br/>";
    let blockValues = await getAvgBlockValues(blocks);
    output.innerHTML += "Got average values of blocks...<br/>";
    let pngValues = await getPNGValues();
    output.innerHTML += "Got values of PNG...<br/>";

    let pixComp = 0;
    for (let coord_pngVal of Object.entries(pngValues)) {
        let coord = coord_pngVal[0];
        let pngVal = coord_pngVal[1];
        if (pngVal.alpha !== 0) {
            setTimeout(() => {
                let blockSim = getBlockSimilarity(pngVal, blockValues);
                displaySimilarities(coord, blockSim);
                if (pixComp % 50 === 0) {
                    output.innerHTML += `${coord} Completed!<br/>`;
                }
                pixComp += 1;
            }, 10)
        }
        
    }
}

function displaySimilarities(coord, blockSim) {
    let blocksTextArea = document.getElementById("blocks");
    blocksTextArea.innerHTML += `${coord}\n`;
    
    for (let block_sim of Object.entries(blockSim)) {
        let block = block_sim[0];
        let sim = block_sim[1];

        blocksTextArea.innerHTML += `${block}: ${sim}\n`;
    }
}

function getBlockSimilarity(pixel, blockVals) {
    let similarity = {};

    for (let block_value of Object.entries(blockVals)) {
        let block = block_value[0];
        let value = block_value[1];

        let diffR = Math.abs(value.red - pixel.red)/255;
        let diffG = Math.abs(value.green - pixel.green)/255;
        let diffB = Math.abs(value.blue - pixel.blue)/255;
        let diffA = Math.abs(value.alpha - pixel.alpha)/255;
        
        let diffOverall = 1 - (diffR+diffG+diffB+diffA) / 4;
        similarity[block] = diffOverall;
    }

    return sortDictionaryByValues(similarity);
}

async function getListOfBlocks() {
    let blockList = [];

    await fetch("http://localhost:3061/1-14-4_block")
    .then((res) => {
        return res.json();
    })
    .then((resJSON) => {
        resJSON.forEach(val => {
            if (val.endsWith(".png")) {
                blockList.push(val.slice(0, val.length-4));
            }
        });
    })

    return blockList;
}

async function getAvgBlockValues(blocks) {
    let avgVal = {};
    
    for (let b = 0; b < blocks.length; b++) {
        fetch(`http://localhost:3061/${blocks[b]}`)
        .then((res) => {
            return res.json();
        })
        .then((resJSON) => {
            avgVal[`${blocks[b]}`] = resJSON;
        })
    }

    return avgVal;
}

async function getPNGValues() {
    let pngValues = {};

    await fetch("http://localhost:3061/Redstone Survivalist Skin")
    .then((res) => {
        return res.json();
    })
    .then((resJSON) => {
        pngValues = resJSON
    })

    return pngValues;
}



window.addEventListener("load", pageLoad);

// Code provided by thefourtheye @ (https://stackoverflow.com/a/25500462)
function sortDictionaryByValues(dict) {
    let items = Object.keys(dict).map(function(key) {
        return [key, dict[key]];
    });
  
    items.sort(function(first, second) {
        return second[1] - first[1];
    });

    return Object.fromEntries(items.slice(0, 21)); // I modified this line
}