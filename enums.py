"""
Enumerated types common to gimp formats
"""
import typing
from enum import Enum


COLOR_MODES=Enum('COLOR_MODES',start=0,names=(
    'RGB','Grayscale','Indexed'
    ))

UNITS=Enum('UNITS',start=0,names=(
    'Inches','Millimeters','Points','Picas'
    ))
UNITS_TO_MM:typing.Tuple[float,float,float,float]=\
    (25.4,1,127/360.0,127/30.0)

COMPOSITE_MODES=Enum('UNITS',start=-3,names=(
    '(auto) Intersection','(auto) Clip to layer','(auto) Clip to backdrop',
    'Union','Clip to backdrop','Clip to layer','Intersection'
    ))

COMPOSITE_SPACES=Enum('COMPOSITE_SPACES',start=-3,names=(
    '(Auto) LAB','(Auto) RGB (perceptual)','(Auto) RGB (linear)',
    'RGB (linear)','RGB (perceptual)','LAB'
    ))

TAG_COLORS=Enum('TAG_COLORS',start=0,names=(
    'None','Blue','Green','Yellow','Orange','Brown','Red','Violet','Gray'
    ))
COMPRESSION_MODES=Enum('COMPRESSION_MODES',start=0,names=(
    'None','RLE','Zlib','Fractal'
    ))

BLEND_MODES=Enum('BLEND_MODES',start=0,names=(
    'Normal (legacy)',
    'Dissolve (legacy)',
    'Behind (legacy)',
    'Multiply (legacy)',
    'Screen (legacy)',
    'Old broken Overlay',
    'Difference (legacy)',
    'Addition (legacy)',
    'Subtract (legacy)',
    'Darken only (legacy)',
    'Lighten only (legacy)',
    'Hue (HSV) (legacy)',
    'Saturation (HSV) (legacy)',
    'Color (HSL) (legacy)',
    'Value (HSV) (legacy)',
    'Divide (legacy)',
    'Dodge (legacy)',
    'Burn (legacy)',
    'Hard Light (legacy)',
    'Soft light (legacy)',
    'Grain extract (legacy)',
    'Grain merge (legacy)',
    'Color erase (legacy)',
    'Overlay',
    'Hue (LCH)',
    'Chroma (LCH)',
    'Color (LCH)',
    'Lightness (LCH)',
    'Normal',
    'Behind',
    'Multiply',
    'Screen',
    'Difference',
    'Addition',
    'Substract',
    'Darken only',
    'Lighten only',
    'Hue (HSV)',
    'Saturation (HSV)',
    'Color (HSL)',
    'Value (HSV)',
    'Divide',
    'Dodge',
    'Burn',
    'Hard light',
    'Soft light',
    'Grain extract',
    'Grain merge',
    'Vivid light',
    'Pin light',
    'Linear light',
    'Hard mix',
    'Exclusion',
    'Linear burn',
    'Luma/Luminance darken only',
    'Luma/Luminance lighten only',
    'Luminance',
    'Color erase',
    'Erase',
    'Merge',
    'Split',
    'Pass through'))

PROPS=Enum('PROPS',start=0,names=(
    'END',
    'COLORMAP',
    'ACTIVE_LAYER',
    'ACTIVE_CHANNEL',
    'SELECTION',
    'FLOATING_SELECTION',
    'OPACITY',
    'MODE',
    'VISIBLE',
    'LINKED',
    'LOCK_ALPHA',
    'APPLY_MASK',
    'EDIT_MASK',
    'SHOW_MASK',
    'SHOW_MASKED',
    'OFFSETS',
    'COLOR',
    'COMPRESSION',
    'GUIDES',
    'RESOLUTION',
    'TATTOO',
    'PARASITES',
    'UNIT',
    'PATHS',
    'USER_UNIT',
    'VECTORS',
    'TEXT_LAYER_FLAGS',
    'OLD_SAMPLE_POINTS',
    'LOCK_CONTENT',
    'GROUP_ITEM',
    'ITEM_PATH',
    'GROUP_ITEM_FLAGS',
    'LOCK_POSITION',
    'FLOAT_OPACITY',
    'COLOR_TAG',
    'COMPOSITE_MODE',
    'COMPOSITE_SPACE',
    'BLEND_SPACE',
    'FLOAT_COLOR',
    'SAMPLE_POINTS',
    'NUM_PROPS'
    ))
