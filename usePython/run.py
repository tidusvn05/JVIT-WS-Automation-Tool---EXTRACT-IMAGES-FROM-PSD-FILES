from psd_tools import PSDImage, compose
from PIL import Image
import glob, os
import pathlib
import shutil
import json
import matplotlib
import matplotlib.pyplot as plt
import logging
import numpy as np
import imutils
import cv2
import xlsxwriter
import re
from mod.colz import Colz
from sklearn.cluster import KMeans
from collections import Counter

import constant

logger = logging.Logger('catch_all')
infos = []

# os.mkdir('./out') 

def main():
  # scan_path = "%s/Task3281PC" % constant.SRC_DIR;
  # scan_path = "%s/test" % constant.SRC_DIR;
  # scan_path = "%s/02.dogfood" % constant.SRC_DIR;
  # scan_path = "%s/04.cleansing" % constant.SRC_DIR;
  # scan_path = "%s/03.diet" % constant.SRC_DIR;
  # scan_path = "%s/05.protein" % constant.SRC_DIR;
  # scan_path = "%s/06.hair tonic" % constant.SRC_DIR;
  # scan_path = "%s/07.all-in-one" % constant.SRC_DIR;
  # scan_path = "%s/08.wine" % constant.SRC_DIR;
  
  scan_path = "%s/demo1" % constant.SRC_DIR;
  # scan_path = "%s/demo2" % constant.SRC_DIR;

  # print(scan_path)
  for file in pathlib.Path(scan_path).glob('**/*.psd'):
    src_file = str(file)
    ori_filename = str(file.stem)
    # print(ori_filename)
    root_path = create_root_path_from_src_file(src_file)
    export_image_for_filename(src_file, root_path, file)
    # export_image_a_file(src_file, root_path, file)
    # return


  # export_image_for_filename('s2_c1.psd')
  print("SUCCESS!!!!")

def export_image_a_file(src_file, rootPath, file):
  pass

  psd = PSDImage.open(src_file)
  # run some task before
  clear_out_dir_before_rerun(rootPath)
  create_dir(rootPath)

  # layers = sort_layers(psd)

  layers = []
  i = 0
  for layer in psd:
    print("layer.name %s" % layer.name)
    layer.visible = 0
    layers.append(layer)
    
    if i >= 3:
      break
    i += 1
  

  # image = compose(layers)
  # image.save(rootPath + '/' + 'a.png')
  psd.composite(layers).save(rootPath + '/' + constant.LAYOUT_FILE)


def export_image_for_filename(src_file, rootPath, file):
  print("")
  print("")
  print("==============================")
  print("==============================")
  print("==============================")
  # rootPath = filename.replace('.psd', '')
  print(src_file)
  # print(rootPath)
  psd = PSDImage.open(src_file)

  # run some task before
  clear_out_dir_before_rerun(rootPath)
  create_dir(rootPath)


  # export fullsize
  psd.composite().save(rootPath + '/' + constant.FULLPAGE_FILE)
  psd.composite().save(rootPath + '/' + constant.OUTLINE_FILE)

  # clear old data
  print('clear old data')
  global currentRootPath
  global infos
  global currentTypeMappingID
  infos = []
  currentRootPath = rootPath
  currentTypeMappingID = 0

  clear_text_info(rootPath)
  layers = sort_layers(psd)

  for layer in layers:
    # level 1
    print("========== lEVEL 1")
    print(layer.name)
    paths = [rootPath]

    if layer.is_group():
      # sub_path = rootPath + '/' + layer.name;
      paths.append(layer.name)
      deep_scan_layers_in_group(layer, paths)
      # for child in sort_layers(layer):
      #   print("----- lEVEL 2")
      #   print(child.name)
      #   deep_scan_layers_in_group(child, paths)
        # level 2
        # if child.is_group():
        #   # Export layers in group to images
        #   deep_scan_layers_in_group(child, paths)

        # # export group image
        # process_single_layer(child, paths)
        

    else:
      process_single_layer(layer, paths)

  # write all infos to excel
  write_infos_to_excel_file(rootPath, file)

  # psd.composite().save(rootPath + '/' + constant.LAYOUT_FILE)


def clear_text_info(path):
  filename = path + '/' + constant.TEXTS_FILE;
  if os.path.exists(filename):
    os.remove(filename)

def process_single_layer(layer, paths):
  if layer.is_group() == False:
    if layer.kind == 'type':
      visible = 1
      print("EXPORT: type layer %s" % layer.name)
      # export to image
      export_text_to_png(layer, paths)
      # get info for type layer
      info = get_text_info(layer)
      # print('process_single_layer')

      global infos
      infos.append(info)

      layer.visible = 0
    else:
      print("EXPORT: single layer %s" % layer.name)
      export_to_png(layer, paths)

    
def write_info_to_txt_file(rootPath, info):
  filename = rootPath + '/' + constant.TEXTS_FILE;
  f = open(filename, "a")
  f.write("\n")
  f.write("------------------------------\n")
  f.write(str(info) + "\n")

  f.close()


def write_infos_to_excel_file(rootPath, file):
  global infos
  print('write_infos_to_excel_file >>')
  # print(infos)
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
      
    # stroke_cell_format = workbook.add_format()
    # stroke_cell_format.set_pattern(1) 
    # stokeColor = str(info.get('stokeColor'))
    # stroke_cell_format.set_bg_color(stokeColor)
    # worksheet.write('F%s' % i, str(info.get('stokeColor')), stroke_cell_format)
  

  workbook.close()

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

    list = []
    for length, style in zip(runlength, rundata):
      substring = text[index:index + length]
      stylesheet = style['StyleSheet']['StyleSheetData']
      font = fontset[stylesheet['Font']]
      fontSize = round(stylesheet['FontSize'] * yy, 2)
      fillColor = convertPSDColorToHex(stylesheet.get('FillColor'))
      stokeColor = convertPSDColorToHex(stylesheet.get('StrokeColor'))
      
      print('%r gets %s - size %s' % (substring, font, fontSize))

      apart_item = dict(
        text=substring,
        fontCode=font['Name'],
        fontName=constant.FONT_DICT.get(font['Name'], font['Name']),
        fontSize=fontSize,
        fillColor=fillColor,
        stokeColor=stokeColor,
      )
      list.append(apart_item)

      index += length

    # fontSize = stylesheet['FontSize']
    # textSpacing = stylesheet['Tracking']
    print(">> listtttt:")
    print (list)

    # for apart_item in list:

    # extract colors in image
    colors = extract_color_in_image(layer)
        
    ret = dict(
      mappingId=currentTypeMappingID,
      text=rawRext,
      fontCode=font['Name'],
      fontName=constant.FONT_DICT.get(font['Name'], font['Name']),
      fontSize=fontSize,
      # textSpacing=textSpacing,
      fillColor=fillColor,
      stokeColor=stokeColor,
      colors=colors,
    )

    print(ret)
    print('./xxxxxxxxxxx: get_text_info' )

    # draw outline for type
    draw_highlight_mapping_for_type(layer, ret)


    return ret
    # 
    # print('%r with style %s fontsize: $s' % (rawRext, font, fontSize))

def draw_highlight_mapping_for_type(layer, info):
  global currentRootPath
  print ('draw_highlight_mapping_for_type --')
  size = layer.size
  offset = layer.offset
  bbox = layer.bbox
  # print("size & offset: ")
  # print(size)
  # print(offset)
  # print(bbox)
  path = currentRootPath + '/' + constant.OUTLINE_FILE
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



def extract_color_in_image(layer):
  global currentRootPath
  text_path = currentRootPath + '/extracted_texts'
  number_of_colors = 3
  image_path = get_fullpath_for_layer(layer, text_path)
  print('extract_color_in_image:')
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

# Remove child as text in group
# export to image
def deep_scan_layers_in_group(group, paths):
  print('-- deep_scan_layers_in_group: ' + group.name)
  
  # if has_include_text_layer(group) == False:
  #   # export to image
  #   # export_to_png(group, sub_path)
  #   # print ("no contain text: " + group.name)
  #   return;

  layer_len = 0
  text_type_len = 0;
  paths.append(group.name)

  # return;
  for child in sort_layers(group):
    print("++++ lEVEL 3")
    print(group.name)
    # level 3
    layer_len += 1

    
    if child.is_group():
      print("checking group: " + child.name)
      # export group to image
      

      # extract colors if group have include type layer
      # if has_include_text_layer(child) == False:
      #   print("EXPORT: has_include_text_layer %s" % child.name)
      #   export_to_png(child, paths)
      #   # print ("extract colors if group have include type layer: ")
      #   # extract_color_in_image(child)        
        

      # Export layers in group to images
      deep_scan_layers_in_group(child, paths)
    else:
      process_single_layer(child, paths)

    ## for export group image with no text
    if (child.kind == 'type'):
      print("checking node type: " + child.name)
      text_type_len += 1
      child.visible = 0

  
  # export group image with no text
  if (layer_len == text_type_len):
    # print('layer_len: %d'  % layer_len)
    # print('text_type_len %d' % text_type_len)
    print("EXPORT: all is texts, skip %s" % group.name)
  else:
    # sub_path = path + '/' + group.name;
    paths.append(group.name);
    print("EXPORT: group rt %s" % group.name)
    # print('export exclude text layer: %s' % group.name)
    export_to_png(group, paths, 'rt')
  


def has_include_text_layer(layer):
  if layer.is_group():
    return has_include_text_group(layer)

  classname = get_layer_classname(layer)
  if (classname == 'TypeLayer'):
    layer.visible = 0
    return bool(True)
  
  return False;

def has_include_text_group(group):
  for layer in group:
    classname = get_layer_classname(layer)
    if (classname == 'TypeLayer'):
      return bool(True)
  
  return False;

def get_layer_classname(layer):
  return type(layer).__name__;

def dump(obj):
  for attr in dir(obj):
    if hasattr( obj, attr ):
      print( "obj.%s = %s" % (attr, getattr(obj, attr)))

# 
def create_dir(path):
  # print('create path: %s' % path)
  if not os.path.exists(path):
    os.makedirs(path)
  # try:
  #   os.makedirs(path)
  # except OSError:
  #   return;
  #   # print ("Creation of the directory %s failed" % path)
  # else:
  #   print ("Successfully created the directory %s" % path)

def clear_out_dir_before_rerun(root_path):
  if constant.CLEAR_OUTPUT_BEFORE_RERUN and os.path.exists(root_path):
    shutil.rmtree(root_path)

def export_to_png(layer, paths, prefix=''):
  # path2 = filename.replace('.psd', '')
  try:
    dir = paths[0]
    create_dir(dir)
    layer_image = layer.composite()
    img_path = get_fullpath_for_layer(layer, dir, prefix)
    layer_image.save(img_path)
    print("exported to file %s" % img_path)

    remove_boudary_transperant_from_img_path(layer, dir)
  except Exception as e:
    logger.error('ERROR path: '+ paths[0]);
    logger.error('ERROR export_to_png: '+ str(e))
  # print('ok')

def export_text_to_png(layer, paths, prefix=''):
  # path2 = filename.replace('.psd', '')
  try:
    dir = paths[0] + '/extracted_texts'
    create_dir(dir)
    layer_image = layer.composite()
    img_path = get_fullpath_for_layer(layer, dir, prefix)
    layer_image.save(img_path)
    print("exported to file %s" % img_path)

    # remove_boudary_transperant_from_img_path(layer, dir)
  except Exception as e:
    logger.error('ERROR path: '+ paths[0]);
    logger.error('ERROR export_to_png: '+ str(e))
  # print('ok') 

def get_filename_for_layer(layer, prefix=''):
  filename = '%s-%s.png' % (layer.name, layer.layer_id)
  if prefix:
    filename = prefix + '-' + filename

  return filename

def get_fullpath_for_layer(layer, dir, prefix=''):
  filename = get_filename_for_layer(layer, prefix)
  final_filename = dir + '/' + filename
  return final_filename

# def remove_boudary_transperant_from_img_path_remove(path):
#   try:
#     img = Image.open(path)

#     if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
#       orig_image = img.convert('RGBA')
#       background = Image.new('RGBA', img.size)
#       img = Image.alpha_composite(background, img)
#       img = img.convert("RGB")
#       new_path = path.replace('.png', '-rt.png')
#       img.save(new_path, "PNG")
#       print("*** remove_boudary_transperant_from_img_path %s" % path)
#     # else:
#     #   img.save(path, "PNG")
#   except Exception as e:
#     logger.error('ERROR path: '+ path);
#     logger.error('ERROR remove_boudary_transperant_from_img_path: '+ str(e))


def remove_boudary_transperant_from_img_path(layer, dir):
  path = get_fullpath_for_layer(layer, dir)
  new_dir = dir + '/removed_transparent_boundary'
  filename = get_filename_for_layer(layer)
  create_dir(new_dir)
  new_path =  new_dir + '/' + filename
  try:

    # Load image, convert to grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    
    original = image.copy()
    # height, width, number of channels in image
    ori_height = original.shape[0]
    ori_width = original.shape[1]

    # gray = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    # thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,21,2)

  
    # Obtain bounding rectangle and extract ROI
    x,y,w,h = cv2.boundingRect(thresh)
    # cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
    ROI = original[y:y+h, x:x+w]
    # height = ROI.shape[0]
    # width = ROI.shape[1]

    print (ori_height, h, ori_width, w)
    
    # if ori_height == h and ori_width == w:
    #   return

    # Add alpha channel
    # b,g,r = cv2.split(ROI)
    # alpha = np.ones(b.shape, dtype=b.dtype) * 50
    # ROI = cv2.merge([b,g,r,alpha])

    # cv2.imshow('thresh', thresh)
    # cv2.imshow('image', image)
    # cv2.imshow('ROI', ROI)
    cv2.imwrite(new_path, ROI)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

  except Exception as e:
    logger.error('ERROR path: '+ path);
    logger.error('ERROR remove_boudary_transperant_from_img_path: '+ str(e))

def create_root_path_from_src_file(src_file):
  return src_file.replace('.psd', '').replace(constant.SRC_DIR, constant.OUT_DIR)


def rgb_to_hex(rgb_color):
  rgb_color = re.search('\(.*\)', rgb_color).group(0).replace(' ', '').lstrip('(').rstrip(')')
  [r, g, b] = [int(x) for x in rgb_color.split(',')]
  # check if in range 0~255
  assert 0 <= r <= 255
  assert 0 <= g <= 255
  assert 0 <= b <= 255

  r = hex(r).lstrip('0x')
  g = hex(g).lstrip('0x')
  b = hex(b).lstrip('0x')
  # re-write '7' to '07'
  r = (2 - len(r)) * '0' + r
  g = (2 - len(g)) * '0' + g
  b = (2 - len(b)) * '0' + b

  hex_color = '#' + r + g + b
  return hex_color

def invert_color(color):
  # strip the # from the beginning
  color = color[1:]

  # convert the string into hex
  color = int(color, 16)

  # invert the three bytes
  # as good as substracting each of RGB component by 255(FF)
  comp_color = 0xFFFFFF ^ color

  # convert the color back to hex by prefixing a #
  comp_color = "#%06X" % comp_color

  # return the result
  return comp_color

# sort layers or groups
def sort_layers(layers):
  try:
    # print("layer len %d" % len(layers))
    list = []
    for layer in layers:
      # print("----")
      # print('%d %d' % (layer.top, layer.left))
      list.append(layer)

    layer_sorted = sorted(list, key=lambda i: (i.top, i.left) )

    # print("====")
    # for l in layer_sorted:
      
    #   print('%d %d' % (l.top, l.left))

    return layer_sorted
  except Exception as e:
    return layers

main()