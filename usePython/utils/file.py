
import sys
sys.path.insert(0,'..')
import constant
import shutil
import os


def create_root_path_from_src_file(src_file):
  return src_file.replace('.psd', '').replace(constant.SRC_DIR, constant.OUT_DIR)

def create_dir(path):
  if not os.path.exists(path):
    os.makedirs(path)

def clear_out_dir_before_rerun(root_path):
  if constant.CLEAR_OUTPUT_BEFORE_RERUN and os.path.exists(root_path):
    shutil.rmtree(root_path)

def get_fullpath_for_layer(layer, dir, suffix=''):
  filename = get_filename_for_layer(layer, suffix)
  final_filename = dir + '/' + filename
  return final_filename

def get_filename_for_layer(layer, suffix=''):
  if suffix:
    return '%s-%s-%s.png' % (layer.name, layer.layer_id, suffix)
  

  return '%s-%s.png' % (layer.name, layer.layer_id)