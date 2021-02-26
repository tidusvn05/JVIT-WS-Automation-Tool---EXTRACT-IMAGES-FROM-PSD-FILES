from psd_tools import PSDImage, compose
from psd_tools.api.layers import Group

import glob, os
import pathlib
import copy 
import numpy as np
import logging
import cv2
import xlsxwriter
import re
from mod.colz import Colz
from sklearn.cluster import KMeans
from collections import Counter

from utils.file import *
from utils.common import *
from utils.color import *
import utils.psd as psd_util

import constant

logger = logging.Logger('catch_all')

def main():
  scan_path = "%s/test" % constant.SRC_DIR;
  # scan_path = "%s/04.cleansing" % constant.SRC_DIR;
  for file in pathlib.Path(scan_path).glob('**/*.psd'):
    src_file = str(file)
    # ori_filename = str(file.stem)
    global rootPath
    rootPath = create_root_path_from_src_file(src_file)
    # export_image_for_filename(src_file, root_path, file)
    process_psd_file(src_file, rootPath, file)


def process_psd_file(src_file, rootPath, file):
  global infos
  global currentTypeMappingID
  infos = []
  currentTypeMappingID = 0

  psd = PSDImage.open(src_file)

  # run some task before
  clear_out_dir_before_rerun(rootPath)
  create_dir(rootPath)

  # export fullsize
  psd.composite().save(rootPath + '/' + constant.FULLPAGE_FILE)
  psd.composite().save(rootPath + '/' + constant.OUTLINE_FILE)

  # return
  layers = psd_util.sorted_from_top_to_bottom(psd)
  for layer in layers:
    if layer.is_group():
      group = layer
      group_level = 1
      # layer is group has sub layers, groups
      process_group(group, group_level, group)
      # return
    else:
      # layer is single layer
      process_single_layer(layer)

  # psd_util.export_layout(psd, rootPath + '/' + constant.LAYOUT_FILE)

  # call hook
  process_psd_file_after(file)


def process_psd_file_after(file):
  # write all infos to excel
  write_infos_to_excel_file(file)
  pass


# ===== PROCESS SINGLE LAYER =====
# process a single layer
def process_single_layer(layer):
  global infos
  print('== process_single_layer')
  psd_util.debug_layer(layer)

  # collect info for type kind
  if layer.kind == 'type':
    layer.visible = 1
    export_layer_to_image(layer, 'extracted_texts')
    layer.visible = 0
    # logging.warning('hide this layer')
    info = get_text_info(layer)
    infos.append(info)
  else:
    export_layer_to_image(layer)
  # else:
  #   # logging.info('single layer not is type')
  #   pass


# ===== PROCESS GROUP =====
# process a group
def process_group(group, group_level=0, root_group=None):
  psd_util.debug_layer(group)
  logging.error('--------------------------------------')
  logging.error('---- process group %s - level %d' % (group.name, group_level))
  
  if not can_scan_next(group_level):

    logging.warning(" >>>> Group %s stop at level %d" % (root_group.name, group_level-1 ))
    return
  
  # hide all unuse layers & calculate kinds
  filtered = group_filtered(group)
  print('filtered final result:::')
  print(filtered)
  
  # export group first
  if is_can_export(filtered, group):
    logging.warning("%s exporting..." % (group.name))
    process_group_export_by_type(filtered, group)
    # process_group_export_mixed(filtered, group)
  else:
    logging.warning("%s not visible" % (group.name))

  logging.info('checking sublayers....')
  for layer in filtered['childs']:
    logging.info('- checking layer %s' % layer.name)
    if layer.is_group():
      subgroup = layer
      group_level += 1
      # layer is group has sub layers, groups
      process_group(subgroup, group_level, root_group)
    else:
      # continue process single layer
      process_single_layer(layer)
    
    # mixed export for layer


  # export group based export type
  
def is_can_export(filtered, group):
  if filtered['is_visible']:
    # return True
    if filtered['len'] == 1 and filtered['kinds'][0] == 'group':
      return False
    else:
      return True
  else:
    return False

def process_group_export_mixed(filtered, group):
  logging.info('>> process_group_export_mixed')
  kinds = filtered['kinds']
  layers = filtered['childs']
  # ori_layers = copy.deepcopy(filtered['childs'])

  # export every kind
  for kind in constant.MIXED_HIDDEN_KINDS:
    is_visible = False
    for layer in layers:
      if (layer.kind == 'type'):
        continue
      if layer.kind == kind:
        layer.visible = 0
      if layer.visible == 1:
        is_visible = True
    
    # export for kind
    if is_visible:
      export_group_to_image(group, 'removed-%s' % kind)



# hide unuse sub layers
# get sub kinds
# check has subgroup
def group_filtered(group):
  logging.warning('>> group_filtering %s' % group.name)
  has_subgroup = False
  kinds = []
  filtered_childs = []
  is_visible = False

  layers = psd_util.sorted_from_top_to_bottom(group)
  # logging.warning('layer len %d' % len(layers))
  # return
  for layer in layers:
    print('------ child name %s' % layer.name)
    psd_util.debug_layer_info(layer)
    kind = layer.kind
    name = layer.name
    kinds.append(kind)
    
    if layer.is_group():
      print('> child id group')
      print('>  group len %d' % len(layer._layers))
      has_subgroup = True
      # layer is group has sub layers, groups
     
      filtered_childs.append(layer)
      # print('filtered_childs:')
      # print(filtered_childs)

      ret = group_filtered(layer)
      print('> subgroup :')
      print(ret)
      kinds = kinds + ret['kinds']
      # print('kinds:')
      # print(kinds)
      if ret['is_visible']:
        is_visible = True
    else:
      print('> child is layer')
      # else will add to filtered
      filtered_childs.append(layer)

      # check kind
      if layer.kind == 'type':
        layer.visible = 0
        continue
      
      # check solid field, highlight backgroup
      if layer.kind == 'solidcolorfill':
        color = layer.data
        hex_color = convert_solid_color_to_hex(color)
        logging.info(hex_color)
        if hex_color in constant.SKIP_SOLID_TYPE_COLOR:
          layer.visible = 0
          continue
      
      # check layer name
      if is_layer_name_skipped(name):
        layer.visible = 0
        continue

      # check visible
      if (layer.visible == 1):
        is_visible = True

      print('filtered_childs:')
      print(filtered_childs)

      
  return dict(
    childs=filtered_childs,
    len=len(filtered_childs),
    kinds=list(np.unique(kinds)),
    has_subgroup=has_subgroup,
    is_visible=is_visible,
  )

  return dict(
    childs=filtered_childs,
    kinds=list(np.unique(kinds)),
    has_subgroup=has_subgroup,
    is_visible=is_visible,
  )


def process_group_export_by_type(filtered, group):
  layers = filtered['childs']
  has_subgroup = filtered['has_subgroup']
  kinds = filtered['kinds']
  export_type = detect_group_export_type(has_subgroup, kinds)
  logging.info('export_type: %s' % export_type)
  if export_type == constant.GROUP_EXPORT_TYPE['Normal']:
    export_group_to_image(group)
  if export_type == constant.GROUP_EXPORT_TYPE['TextHighlight']:
    
    # if guess_group_be_highlight(group):
    #   logging.info('+ TextHighlight Only, Skip Export! %s' % group.name)
    #   pass 
    # else:
    export_group_to_image(group)



def guess_group_be_highlight(group):
  layers = group._layers
  print('layuers count : %d' % len(layers))
  ret = dict()
  for layer in group:
    if layer.kind not in ret:
      ret[layer.kind] = 0
    ret[layer.kind] += 1
  
  print(ret)




def can_scan_next(group_level):
  if group_level <= constant.MAX_GROUP_SCAN_LEVEL:
    return True
  return False

# export group to image
def export_group_to_image(group, suffix=''):
  global rootPath
  img_path = get_fullpath_for_layer(group, rootPath, suffix)
  image = group.composite(force=True)
  image.save(img_path)
  logging.info('+ exported group to %s' % img_path)


def export_layer_to_image(layer, subdir = '', suffix=''):
  global rootPath
  dir = rootPath
  if subdir:
    dir += '/' + subdir
  
  create_dir(dir)
  
  img_path = get_fullpath_for_layer(layer, dir, suffix)

  # print("export_layer_to_image")
  # print(layer.vector_mask)
  # print(layer.bbox)
  # ex_bbox =  Group.extract_bbox(layer, include_invisible=True)

  image = layer.composite(force=True)
  image.save(img_path)
  logging.info('+ exported layer to %s' % img_path)



def get_text_info(layer):
  if layer.is_group() == False and layer.kind == 'type':
    global currentTypeMappingID
    # // increase id
    currentTypeMappingID += 1

    print('xxxxxxxxxxxyy: get_text_info' )
    
    # dump(layer)
    # print(layer.text)
    # print(layer.engine_dict['StyleRun'])
    yy = layer.transform[3]

    text = layer.engine_dict['Editor']['Text'].value
    rawRext = text.rstrip().replace('\r', '<br />')
    fontset = layer.resource_dict['FontSet']
    runlength = layer.engine_dict['StyleRun']['RunLengthArray']
    rundata = layer.engine_dict['StyleRun']['RunArray']
    index = 0

    # print('>>> fontset:')
    # # print(text)
    # print(fontset)
    # print('>>> rundata:')
    # print(rundata)
    # print('runlength ')
    # print(runlength)  

    aparts = []
    # fill_colors = []
    # stroke_colors = []
    for length, style in zip(runlength, rundata):
      substring = text[index:index + length]
      stylesheet = style['StyleSheet']['StyleSheetData']
      font = fontset[stylesheet['Font']]
      fontSize = round(stylesheet['FontSize'] * yy, 2)
      print(stylesheet)
      fillColor = convertPSDColorToHex(stylesheet.get('FillColor'))
      stokeColor = convertPSDColorToHex(stylesheet.get('StrokeColor'))
      # if fillColor:
      #   fill_colors.append(fillColor)
      # if stokeColor:
      #   stroke_colors.append(stokeColor)
      
      print('%r gets %s - size %s - style %s' % (substring, font, fontSize, stylesheet))

      apart_item = dict(
        text=substring,
        fontCode=font['Name'],
        fontName=constant.FONT_DICT.get(font['Name'], font['Name']),
        fontSize=fontSize,
        fillColor=fillColor,
        stokeColor=stokeColor,
      )
      aparts.append(apart_item)

      index += length

    # only get unique list
    # fill_colors = list(np.unique(fill_colors))
    # stroke_colors = list(np.unique(stroke_colors))
    # fontSize = stylesheet['FontSize']
    # textSpacing = stylesheet['Tracking']
    print(">> listtttt:")
    # print (list)
    # if len(stroke_colors) > 1:
    #   logging.warning(">> WARNING: STROKE COLORS_MANY")
    #   logging.warning(stroke_colors)
    # if len(fill_colors) > 1:
    #   logging.warning(">> WARNING: FILL COLORS_MANY")
    #   logging.warning(fill_colors)

    # for apart_item in list:
    # get effects data
    # effect_infos = psd_util.get_effect_of_layer(layer)
    # print('effect_infos:')
    # print(effect_infos)

    # if len(effect_infos) > 0:
    #   aaa

    # extract colors in image
    colors = extract_color_in_image(layer, 'extracted_texts')
        
    ret = dict(
      mappingId=currentTypeMappingID,
      text=rawRext,
      aparts_text=aparts,
      fontCode=font['Name'],
      fontName=constant.FONT_DICT.get(font['Name'], font['Name']),
      fontSize=fontSize,
      # textSpacing=textSpacing,
      fillColor=fillColor,
      stokeColor=stokeColor,
      colors=colors,
    )

    if layer.has_effects():
      ret['effects'] = layer.effects;
      print(ret['effects'][0].__class__.__name__)

    print(ret)
    print('./xxxxxxxxxxx: get_text_info' )

    # draw outline for type
    draw_highlight_mapping_for_type(layer, ret)

    return ret
    # 
    # print('%r with style %s fontsize: $s' % (rawRext, font, fontSize))

def draw_highlight_mapping_for_type(layer, info):
  print ('draw_highlight_mapping_for_type --')
  size = layer.size
  offset = layer.offset
  bbox = layer.bbox
  # print("size & offset: ")
  # print(size)
  # print(offset)
  # print(bbox)
  path = rootPath + '/' + constant.OUTLINE_FILE
  image = cv2.imread(path, cv2.COLOR_BGR2RGB)
  start_point = (bbox[0], bbox[1])
  end_point = (bbox[2], bbox[3])
  rectangle_color=(255, 0, 0) 
  # print(start_point)
  # print(end_point)
  image = cv2.rectangle(image, start_point, end_point, rectangle_color, 3)

  # write mapping id
  text = str(info.get('mappingId'))
  # font 
  font = cv2.FONT_HERSHEY_SIMPLEX 
  # fontScale 
  fontScale = 1
  # Blue color in BGR 
  color = (0, 0, 255) 
  # Line thickness of 2 px 
  thickness = 2
  print ('draw text mapping id %s' % text)
  # org: bottom left position
  size = cv2.getTextSize(text, font, fontScale, thickness)[0]
  org_x = round(layer.left - size[0])
  org_y = round(layer.top + size[1])
  print ('org org_x %d' % org_x)
  print ('org org_y %d' % org_y)
  org = (
    org_x, 
    org_y
  ) 
  
  # draw background rectangle for mapping ID
  _x1 = org_x -1  # x topleft
  _y1 = org_y - size[1] - 1#+int(labelSize[0][1]/2) # y topleft
  _x2 = org_x + size[0] + 1
  _y2 = org_y + 1
  cv2.rectangle(image,(_x1,_y1),(_x2,_y2),(195,236,247),cv2.FILLED)

  print('write mapdping id %s' % text)
  # Using cv2.putText() method 
  image = cv2.putText(image, text, org, font,  
                    fontScale, color, thickness, cv2.LINE_AA) 

  cv2.imwrite(path, image)



def extract_color_in_image(layer, subdir='', suffix=''):
  global rootPath
  dir = rootPath
  if subdir:
    dir += '/' + subdir
  
  image_path = get_fullpath_for_layer(layer, dir, suffix)

  number_of_colors = constant.EXTRACT_MAX_COLOR_KIND_TYPE
  print(image_path)
  if not image_path:
    return 

  try:
    # image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    modified_image = cv2.resize(image, (600, 400), interpolation = cv2.INTER_AREA)
    modified_image = modified_image.reshape(modified_image.shape[0]*modified_image.shape[1], 3)

    clf = KMeans(n_clusters = number_of_colors)
    labels = clf.fit_predict(modified_image)

    counts = Counter(labels)

    center_colors = clf.cluster_centers_
    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()]
    rgb_colors = [ordered_colors[i] for i in counts.keys()]

    print(">> rgb_colors:: ")
    print(hex_colors)
    return hex_colors
  except Exception as e:
    print("ERR: cannot extract_color_in_image %s" % image_path)
    return []


def RGB2HEX(color):
  return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def convertPSDColorToHex(psd_color):
  if not psd_color:
    return

  if 'Values' in psd_color:
    cv = psd_color['Values']

    c1 = Colz()
    c1.setRgba(float(cv[0]), float(cv[1]), float(cv[2]), float(cv[3]))
    
    print( c1.hex )
    return '#' +c1.hex
  return ''



def write_infos_to_excel_file(file):
  global infos
  print('write_infos_to_excel_file >>')
  print(infos)

  ori_filename = str(file.stem)
  filename = rootPath + '/' + ori_filename + '-' + constant.EXCEL_FILE;
  workbook = xlsxwriter.Workbook(filename)
  worksheet = workbook.add_worksheet()

  #setting
  worksheet.set_column('A:A', 10)
  worksheet.set_column('B:B', 60)
  worksheet.set_column('C:C', 20)
  worksheet.set_column('E:E', 10)
  worksheet.set_column('F:F', 10)

  # header
  format_header = workbook.add_format({'bold': True, 'font_color': 'red'})
  worksheet.write('A1', 'MappingID', format_header)
  worksheet.write('B1', 'JA Text', format_header)
  worksheet.write('C1', 'Font Name', format_header)
  worksheet.write('D1', 'Font Size', format_header)

  worksheet.write('E1', 'Color 1', format_header)
  worksheet.write('F1', 'Color 2', format_header)
  worksheet.write('G1', 'Color 3', format_header)

  i = 1
  for info in infos:
    i += 1
    # print('---')
    # print(str(info.get('text')))
    # print(str(info.get('font')))
    # print(str(info.get('fontSize')))
    # print(str(info.get('fillColor')))
    # print(str(info.get('stokeColor')))
    format_id = workbook.add_format({'bold': True, 'align': 'center'})
    worksheet.write('A%s' % i, str(info.get('mappingId')), format_id)
    worksheet.write('B%s' % i, str(info.get('text')))
    worksheet.write('C%s' % i, str(info.get('fontName')))
    worksheet.write('D%s' % i, str(info.get('fontSize')))
    
    # set color
    j = 1
    char_ord = ord('E')
    for color in info.get('colors'):
      invcolor = invert_color(color)
      fill_cell_format = workbook.add_format({ 'font_color': invcolor})
      fill_cell_format.set_pattern(1)  # This is optional when using a solid fill.
      fill_cell_format.set_bg_color(color)
      worksheet.write(chr(char_ord) + '%s' % i, color, fill_cell_format)

      char_ord += 1
      j += 1
      

    # effects
    # if info.get('effects'):
    #   for effect in info.get('effects'):


  workbook.close()





# call main function
main()
