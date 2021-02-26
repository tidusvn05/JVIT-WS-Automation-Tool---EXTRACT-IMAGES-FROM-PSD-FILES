
// async function DisableTextLayerInNode(node) {
//   console.log( "process");
// }
const nodeTypeIsText = require('../typeCheckers/nodeTypeIsText');

module.exports = async function (children) {
  const newChildren = [];
  console.log( "process");
  // const node = children[1];
  // delete children[0];
  // delete children[1];
  for (const child of children) {
    if (nodeTypeIsText(child)) continue;

    newChildren.push(child);
  }
  // console.log(Object.keys(l.layer));

  // const type = l.get('typeTool');
  // console.log(l.layer.metadata());
  // console.log(l.layer.header);
  return newChildren;
}