from mod.colz import Colz

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

def convert_solid_color_to_hex(solid_data):
  if not solid_data:
    return

  i = 0
  for d in solid_data:
    if i == 0:
      r = solid_data.get(d)
    if i == 1:
      g = solid_data.get(d)
    if i == 2:
      b = solid_data.get(d)
    i += 1

  # print(r,g,b)
  h = '#%02x%02x%02x' % (int(r), int(g), int(b))
  
  # print( 'color hex: %s -' % h )
  return h


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