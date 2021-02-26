
module.exports = function(node) {
  try {
    const type = node.get('typeTool');
    const fonts = type.fonts();
    if (fonts.length > 0)
      return true;
  } catch (e) {
    
  }
  return false;
}