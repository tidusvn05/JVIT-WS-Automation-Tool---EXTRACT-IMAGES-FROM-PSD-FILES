const mergeImages = require('merge-images');
const { Canvas, Image } = require('canvas');
var fs = require('fs');
const { listFilesInDir } = require('./utils/common');

var PSD = require('psd');

// var psd = PSD.fromFile("s2_c1.psd");
// psd.parse();
const DisableTextLayerInChildren =  require('./processes/disableTextLayerInNode');

const file = process.argv[2] || './s2_c1.psd';
var start = new Date();
// console.log(psd.tree().export());
// console.log(psd.tree().childrenAtPath('長方形 1')[0].export());
// psd.tree().childrenAtPath('長方形 1')[0].saveAsPng('./output2.png');

// You can also use promises syntax for opening and parsing
// PSD.open("s2_c1.psd").then(function (psd) {
//   return psd.image.saveAsPng('./output.png');
// }).then(function () {
//   console.log("Finished!");
// });
 

PSD.open(file).then(function (psd) {
  psd.tree().descendants().forEach(async function (node) {
    // await mergeImagesInDir('./outputs/グループ 2859')
    console.log(node.name );
    return;

    if (node.name == "グループ 2859") {
      console.log("------");
      // node._children = [];
      // console.log(node._children);

      const children = await DisableTextLayerInChildren(node._children);
      console.log({ children });
      node._children = children;
      exportNodeToPng(node);
      return;
    }
    // if (node.isGroup()) return true;
    // node.saveAsPng("./output/" + node.name + ".png").catch(function (err) {
    //   console.log(err.stack);
    // });
  });
}).then(function () {
  console.log("Finished in " + ((new Date()) - start) + "ms");
}).catch(function (err) {
  console.log(err.stack);
});

// function filter

async function exportNodeToPng(node) {
  if (node.isGroup()) {

    await exportGroupToPng(node);
    return true;
  }

  node.saveAsPng("./output/" + node.name + ".png").catch(function (err) {
    console.log(err.stack);
  });
}


async function exportGroupToPng(node) {
  const dir = `./outputs/${node.name}`;
  if (!fs.existsSync(dir)){
    fs.mkdirSync(dir, { recursive: true });
  }

  for (const child of node._children) {
    console.log({child})
    child.saveAsPng(dir + '/' + child.name + ".png").catch(function (err) {
      console.log(err.stack);
    });
    // exportNodeToPng(child);
  }

}

async function mergeImagesInDir(dir) {
  // const files = await listFilesInDir(dir);
  // console.log({ files });

  // return;
  mergeImages([
    { 
      src: '/Volumes/Sources/JvitSources/ureru/support-process-psd/outputs/グループ 2859/レイヤー 530.png',
      x: 692, y: 128 
    },
    { src: '/Volumes/Sources/JvitSources/ureru/support-process-psd/outputs/グループ 2859/楕円形 1 のコピー 15.png', x: 694, y: 150 },
    { src: '/Volumes/Sources/JvitSources/ureru/support-process-psd/outputs/グループ 2859/楕円形 1 のコピー 16.png', x: 800, y: 272 },
    { src: '/Volumes/Sources/JvitSources/ureru/support-process-psd/outputs/グループ 2859/楕円形 1 のコピー 17.png', x: 779, y: 130 },
  ], {
    Canvas: Canvas,
    Image: Image
  }).then(b64 => {
    console.log({b64});
  });
}
