
import sys
sys.path.insert(0,'..')
import constant
import shutil
import os
import logging
import numpy as np

def detect_group_export_type(has_subgroup, all_kinds):

  if not has_subgroup and np.array_equal(sorted(np.unique(all_kinds)), sorted(constant.GROUP_TEXT_HIGHLIGHT_KINDS)):
    return constant.GROUP_EXPORT_TYPE['TextHighlight']
  
  return constant.GROUP_EXPORT_TYPE['Normal']



def dump(obj):
  for attr in dir(obj):
    if hasattr( obj, attr ):
      print( "obj.%s = %s" % (attr, getattr(obj, attr)))

def is_layer_name_skipped(name):
  for skip_name in constant.SKIP_LAYER_NAMES:
    if skip_name in name:
      return True
  return False