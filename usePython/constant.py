SRC_DIR = 'psd_files'
OUT_DIR = 'outs'

FULLPAGE_FILE = '0_fullpage.png'
OUTLINE_FILE = 'MAPPING_OUTLINE.png'
LAYOUT_FILE = 'LAYOUT.png'
TEXTS_FILE = '1_texts.txt'
EXCEL_FILE = 'texts.xlsx'

CLEAR_OUTPUT_BEFORE_RERUN = True
MAX_GROUP_SCAN_LEVEL = 5
EXTRACT_MAX_COLOR_KIND_TYPE = 3

FONT_DICT = {
  "HiraKakuStd-W3": "ヒラギノ角ゴW3",
  "HiraKakuStd-W4": "ヒラギノ角ゴW4",
  "HiraKakuStd-W5": "ヒラギノ角ゴW5",
  "HiraKakuStd-W6": "ヒラギノ角ゴW6",
  "HiraKakuStd-W7": "ヒラギノ角ゴW7",
  "HiraKakuStd-W8": "ヒラギノ角ゴW8",
  "MaruFoPro-Bold": "丸フォークB",
  "MaruFoPro-Heavy": "丸フォークH",
  "MaruFoPro-Medium": "丸フォークM",
  "RyuminPro-Bold": "リュウミンB",  
  "RyuminPro-ExBold": "リュウミンExB",
  "RyuminPro-ExHeavy": "リュウミンExH",
  "RyuminPro-Heavy": "リュウミンH",
  "RyuminPro-Ultra": "RyuminPro-Ultra",
  "APJapanesefont": "あんずもじ",
  "HuiFont": "ふい字",
  "RiiTN_R": "りいてがきN",
}

GROUP_EXPORT_TYPE = {
  "Normal": 1,
  "TextHighlight": 2,
}
SKIP_SOLID_TYPE_COLOR = [
  '#fff000',
  '#fff100',
]
GROUP_TEXT_HIGHLIGHT_KINDS = ['type', 'solidcolorfill']
SKIP_LAYER_NAMES = [
  's_logo'
]

MIXED_HIDDEN_KINDS = [
  'solidcolorfill',
  # 'group',
]