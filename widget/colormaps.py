#!/usr/bin/env python
# $Id$
#------------------------------------------------------------------------
#	NAME:		colormaps.py					-
#	HISTORY:							-
#		2018-04-02	leerw@ornl.gov				-
#------------------------------------------------------------------------
import os, sys

try:
  from matplotlib import cm, colors
except Exception:
  raise ImportError( 'The matplotlib module is required for this component' )


#------------------------------------------------------------------------
#	GLOBAL:		COLORMAP_DEFS					-
#------------------------------------------------------------------------
COLORMAP_DEFS = \
  {
#  'Perceptually Uniform':
#    [ 'inferno', 'magma', 'plasma', 'viridis' ],
  'Sequential':
    [
      'Blues', 'BuGn', 'BuPu',
      'GnBu', 'Greens', 'Greys',
      'Oranges', 'OrRd',
      'PuBu', 'PuBuGn', 'PuRd', 'Purples',
      'RdPu', 'Reds', 'Wistia',
      'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd',
      'afmhot', 'autumn',
      'binary', 'bone',
      'cool', 'copper',
      'gist_gray', 'gist_heat', 'gist_yarg', 'gray',
      'hot', 'pink', 'spring', 'summer', 'winter',
    ],
  'Qualitative':
    [
      'Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2',
      'Set1', 'Set2', 'Set3',
      'tab10', 'tab20', 'tab20b', 'tab20c',
    ],
  'Miscellaneous':
    [
      'brg', 'CMRmap', 'cubehelix', 'flag',
      'gist_earth', 'gist_ncar', 'gist_rainbow', 'gist_stern',
      'gnuplot', 'gnuplot2', 'hsv', 'jet',
      'nipy_spectral', 'ocean', 'prism', 'rainbow', 'terrain',
    ],
  }


#------------------------------------------------------------------------
#	WRAPPER:	 run_once()					-
#------------------------------------------------------------------------
def run_once( f ):
  def wrapper( *args, **kwargs ):
    if not wrapper.has_run:
      wrapper.has_run = True
      return  f( *args, **kwargs )
  #end wrapper

  wrapper.has_run = False
  return  wrapper
#end run_once


#------------------------------------------------------------------------
#	FUNCTION:	register_colormaps()				-
#------------------------------------------------------------------------
@run_once
def register_colormaps():
  cm.register_cmap( cmap = colors.ListedColormap(
      ( (0.4980392156862745, 0.788235294117647, 0.4980392156862745),
        (0.7450980392156863, 0.6823529411764706, 0.8313725490196079),
        (0.9921568627450981, 0.7529411764705882, 0.5254901960784314),
        (1.0, 1.0, 0.6),
        (0.2196078431372549, 0.4235294117647059, 0.6901960784313725),
        (0.9411764705882353, 0.00784313725490196, 0.4980392156862745),
        (0.7490196078431373, 0.3568627450980392, 0.09019607843137253),
        (0.4, 0.4, 0.4) ),
      'Accent'
      ) )

  cm.register_cmap( cmap = colors.ListedColormap(
      ( (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
        (1.0, 0.4980392156862745, 0.054901960784313725),
        (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
        (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),
        (0.5803921568627451, 0.403921568627451, 0.7411764705882353),
        (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),
        (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),
        (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),
        (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),
        (0.09019607843137255, 0.7450980392156863, 0.8117647058823529) ),
      'tab10'
      ) )

  cm.register_cmap( cmap = colors.ListedColormap(
      ( (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
        (0.6823529411764706, 0.7803921568627451, 0.9098039215686274),
        (1.0, 0.4980392156862745, 0.054901960784313725),
        (1.0, 0.7333333333333333, 0.47058823529411764),
        (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
        (0.596078431372549, 0.8745098039215686, 0.5411764705882353),
        (0.8392156862745098, 0.15294117647058825, 0.1568627450980392),
        (1.0, 0.596078431372549, 0.5882352941176471),
        (0.5803921568627451, 0.403921568627451, 0.7411764705882353),
        (0.7725490196078432, 0.6901960784313725, 0.8352941176470589),
        (0.5490196078431373, 0.33725490196078434, 0.29411764705882354),
        (0.7686274509803922, 0.611764705882353, 0.5803921568627451),
        (0.8901960784313725, 0.4666666666666667, 0.7607843137254902),
        (0.9686274509803922, 0.7137254901960784, 0.8235294117647058),
        (0.4980392156862745, 0.4980392156862745, 0.4980392156862745),
        (0.7803921568627451, 0.7803921568627451, 0.7803921568627451),
        (0.7372549019607844, 0.7411764705882353, 0.13333333333333333),
        (0.8588235294117647, 0.8588235294117647, 0.5529411764705883),
        (0.09019607843137255, 0.7450980392156863, 0.8117647058823529),
        (0.6196078431372549, 0.8549019607843137, 0.8980392156862745) ),
      'tab20'
      ) )

  cm.register_cmap( cmap = colors.ListedColormap(
      ( (0.2235294117647059, 0.23137254901960785, 0.4745098039215686),
        (0.3215686274509804, 0.32941176470588235, 0.6392156862745098),
        (0.4196078431372549, 0.43137254901960786, 0.8117647058823529),
        (0.611764705882353, 0.6196078431372549, 0.8705882352941177),
        (0.38823529411764707, 0.4745098039215686, 0.2235294117647059),
        (0.5490196078431373, 0.6352941176470588, 0.3215686274509804),
        (0.7098039215686275, 0.8117647058823529, 0.4196078431372549),
        (0.807843137254902, 0.8588235294117647, 0.611764705882353),
        (0.5490196078431373, 0.42745098039215684, 0.19215686274509805),
        (0.7411764705882353, 0.6196078431372549, 0.2235294117647059),
        (0.9058823529411765, 0.7294117647058823, 0.3215686274509804),
        (0.9058823529411765, 0.796078431372549, 0.5803921568627451),
        (0.5176470588235295, 0.23529411764705882, 0.2235294117647059),
        (0.6784313725490196, 0.28627450980392155, 0.2901960784313726),
        (0.8392156862745098, 0.3803921568627451, 0.4196078431372549),
        (0.9058823529411765, 0.5882352941176471, 0.611764705882353),
        (0.4823529411764706, 0.2549019607843137, 0.45098039215686275),
        (0.6470588235294118, 0.3176470588235294, 0.5803921568627451),
        (0.807843137254902, 0.42745098039215684, 0.7411764705882353),
        (0.8705882352941177, 0.6196078431372549, 0.8392156862745098) ),
      'tab20b'
      ) )

  cm.register_cmap( cmap = colors.ListedColormap(
      ( (0.19215686274509805, 0.5098039215686274, 0.7411764705882353),
        (0.4196078431372549, 0.6823529411764706, 0.8392156862745098),
        (0.6196078431372549, 0.792156862745098, 0.8823529411764706),
        (0.7764705882352941, 0.8588235294117647, 0.9372549019607843),
        (0.9019607843137255, 0.3333333333333333, 0.050980392156862744),
        (0.9921568627450981, 0.5529411764705883, 0.23529411764705882),
        (0.9921568627450981, 0.6823529411764706, 0.4196078431372549),
        (0.9921568627450981, 0.8156862745098039, 0.6352941176470588),
        (0.19215686274509805, 0.6392156862745098, 0.32941176470588235),
        (0.4549019607843137, 0.7686274509803922, 0.4627450980392157),
        (0.6313725490196078, 0.8509803921568627, 0.6078431372549019),
        (0.7803921568627451, 0.9137254901960784, 0.7529411764705882),
        (0.4588235294117647, 0.4196078431372549, 0.6941176470588235),
        (0.6196078431372549, 0.6039215686274509, 0.7843137254901961),
        (0.7372549019607844, 0.7411764705882353, 0.8627450980392157),
        (0.8549019607843137, 0.8549019607843137, 0.9215686274509803),
        (0.38823529411764707, 0.38823529411764707, 0.38823529411764707),
        (0.5882352941176471, 0.5882352941176471, 0.5882352941176471),
        (0.7411764705882353, 0.7411764705882353, 0.7411764705882353),
        (0.8509803921568627, 0.8509803921568627, 0.8509803921568627) ),
      'tab20c'
      ) )
#end register_colormaps
