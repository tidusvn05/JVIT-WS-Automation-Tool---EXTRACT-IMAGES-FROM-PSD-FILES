const { resolve } = require('path');
const { readdir } = require('fs').promises;

exports.listFilesInDir = async (dir) => {
  const dirents = await readdir(dir, { withFileTypes: true });
  const files = await Promise.all(dirents.map((dirent) => {
    const res = resolve(dir, dirent.name);
    return dirent.isDirectory() ? getFiles(res) : res;
  }));
  const allFiles =  Array.prototype.concat(...files);
  return allFiles;
};


