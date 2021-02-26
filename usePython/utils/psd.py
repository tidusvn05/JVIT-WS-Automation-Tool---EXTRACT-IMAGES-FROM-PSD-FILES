import json
import coloredlogs, logging
coloredlogs.install()


def export_psd(image_path):
  print('aaa')

# hide all type layers
def export_layout(psd, image_path):
  image = psd.composite(
    layer_filter=lambda layer: layer.is_visible() and layer.kind != 'type')
  image.save(image_path)


def debug_layer(layer):
  logging.warn('==============================')
  if layer.is_group():
    logging.warn('==============================')
    logging.warn('==============================')
  
  # name
  if layer.parent:
    logging.info('Parent Paths: %s > %s' % (layer.parent.name, layer.name))
  else:
    logging.info('LayerName: ' + layer.name)

  logging.error('Kind: ' + layer.kind)
  
  if (layer.kind == 'type'):
    # logging.error('>> skip layer!')
    pass

  if (layer.kind == 'solidcolorfill'):
    # logging.info('>> skip layer!')
    pass

def debug_layer_info(layer):
  logging.info('name: %s kind: %s' % (layer.name, layer.kind))


# sort layers or groups
def sorted_from_top_to_bottom(layers):
  try:
    print("[sorted_from_top_to_bottom]")
    list = []
    for layer in layers:
      # print("----")
      # print('%d %d' % (layer.top, layer.left))
      list.append(layer)

    layer_sorted = sorted(list, key=lambda i: (i.top, i.right) )

    print("====")
    for l in layer_sorted:
      
      print('%d %d' % (l.top, l.left))

    return layer_sorted
  except Exception as e:
    return layers

def get_effect_of_layer(layer):
  ret = []
  if layer.has_effects():
    for effect in layer.effects:
      eff = effect.present()
      ret.append(eff)
  
  return ret

def parseEffectToDict(effect):
  for i in effect:
    print(i)
    print(effect[i])
    print(effect.get(i))