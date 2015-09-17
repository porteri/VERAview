#!/usr/bin/env python
# $Id$
#------------------------------------------------------------------------
#	NAME:		channel_assembly_view.py			-
#	HISTORY:							-
#		2015-08-31	leerw@ornl.gov				-
#	  Added GetAnimationIndexes().
#		2015-07-27	leerw@ornl.gov				-
#	  Fixing order of dataset references to row, col, axial, assy
#	  instead of col, row, ...
#		2015-07-11	leerw@ornl.gov				-
#------------------------------------------------------------------------
import math, os, sys, threading, time, traceback
import numpy as np
import pdb  #pdb.set_trace()

try:
  import wx
  import wx.lib.delayedresult as wxlibdr
  #from wx.lib.scrolledpanel import ScrolledPanel
except Exception:
  raise ImportError( 'The wxPython module is required for this component' )

try:
  import PIL.Image, PIL.ImageDraw, PIL.ImageFont
  #from PIL import Image, ImageDraw
except Exception:
  raise ImportError, 'The Python Imaging Library (PIL) required for this component'

#from bean.axial_slider import *
#from bean.exposure_slider import *
from data.utils import DataUtils
from event.state import *
from legend import *
from raster_widget import *
from widget import *


#------------------------------------------------------------------------
#	CLASS:		ChannelAssembly2DView				-
#------------------------------------------------------------------------
class ChannelAssembly2DView( RasterWidget ):
  """Pin-by-pin assembly view across axials and exposure times or states.

Attrs/properties:
"""


#		-- Object Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.__init__()		-
  #----------------------------------------------------------------------
  def __init__( self, container, id = -1, **kwargs ):
    self.assemblyIndex = ( -1, -1, -1 )
    self.channelColRow = None
    self.channelDataSet = kwargs.get( 'dataset', 'channel_liquid_temps [C]' )
    self.showPins = True

    super( ChannelAssembly2DView, self ).__init__( container, id )

    self.menuDef = \
      [
	( 'Hide Labels', self._OnToggleLabels ),
	( 'Hide Legend', self._OnToggleLegend ),
        ( 'Unzoom', self._OnUnzoom )
      ]
  #end __init__


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._CreateDrawConfig()	-
  #----------------------------------------------------------------------
  def _CreateDrawConfig( self, **kwargs ):
    """Creates a draw configuration based on imposed 'size' (wd, ht ) or
'scale' (pixels per pin) from which a size is determined.
If neither are specified, a default 'scale' value of 24 is used.
@param  kwargs
    scale	pixels per pin
    size	( wd, ht ) against which to compute the scale
@return			config dict with keys:
    clientSize
    fontSize
    labelFont
    labelSize
    legendPilImage
    legendSize
    pilFont
    +
    assemblyRegion
    channelGap
    channelWidth
    lineWidth
    valueFont
    valueFontSize
"""
    config = self._CreateBaseDrawConfig(
        self.data.GetRange( self.channelDataSet ),
	**kwargs
	)

    font_size = config[ 'fontSize' ]
    label_size = config[ 'labelSize' ]
    legend_pil_im = config[ 'legendPilImage' ]
    legend_size = config[ 'legendSize' ]

#		-- Must calculate scale?
#		--
    if 'clientSize' in config:
      wd, ht = config[ 'clientSize' ]

      # label : core : font-sp : legend
      region_wd = wd - label_size[ 0 ] - 2 - (font_size << 1) - legend_size[ 0 ]
      #chan_adv_wd = region_wd / (self.data.core.npin + 1)
      chan_adv_wd = region_wd / self.cellRange[ -2 ]

      working_ht = max( ht, legend_size[ 1 ] )
      region_ht = working_ht - label_size[ 1 ] - 2 - (font_size * 3 / 2)
      #chan_adv_ht = region_ht / (self.data.core.npin + 1)
      chan_adv_ht = region_ht / self.cellRange[ -1 ]

      if chan_adv_ht < chan_adv_wd:
        chan_adv_wd = chan_adv_ht

      #chan_gap = chan_adv_wd >> 3
      chan_gap = 0
      chan_wd = max( 1, chan_adv_wd - chan_gap )

      assy_wd = self.cellRange[ -2 ] * (chan_wd + chan_gap)
      assy_ht = self.cellRange[ -1 ] * (chan_wd + chan_gap)

    else:
      chan_wd = kwargs[ 'scale' ] if 'scale' in kwargs else 24

      #chan_gap = chan_wd >> 3
      chan_gap = 0
      assy_wd = self.cellRange[ -2 ] * (chan_wd + chan_gap)
      assy_ht = self.cellRange[ -1 ] * (chan_wd + chan_gap)

      # label : core : font-sp : legend
      wd = label_size[ 0 ] + assy_wd + (font_size << 1) + legend_size[ 0 ]
      ht = max( assy_ht, legend_size[ 1 ] )
      ht += (font_size << 1) + font_size

      config[ 'clientSize' ] = ( wd, ht )
    #end if-else


    value_font_size = chan_wd >> 1
    value_font = \
        PIL.ImageFont.truetype( self.valueFontPath, value_font_size ) \
	if value_font_size >= 6 else None

    config[ 'assemblyRegion' ] = \
        [ label_size[ 0 ] + 2, label_size[ 1 ] + 2, assy_wd, assy_ht ]
    config[ 'channelGap' ] = chan_gap
    config[ 'channelWidth' ] = chan_wd
    config[ 'lineWidth' ] = max( 1, chan_gap )
    config[ 'valueFont' ] = value_font
    config[ 'valueFontSize' ] = value_font_size

    return  config
  #end _CreateDrawConfig


  #----------------------------------------------------------------------
  #     METHOD:         ChannelAssembly2DView.CreatePopupMenu()		-
  #----------------------------------------------------------------------
  def CreatePopupMenu( self ):
    """Lazily creates.  Must be called from the UI thread.
"""
    super( ChannelAssembly2DView, self ).CreatePopupMenu()
    if self.popupMenu != None:
      self._UpdateVisibilityMenuItems(
          self.popupMenu,
	  'Pins', self.showPins
	  )
    #end if must create menu

    return  self.popupMenu
  #end CreatePopupMenu


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._CreateRasterImage()	-
  #----------------------------------------------------------------------
  def _CreateRasterImage( self, tuple_in ):
    """Called in background task to create the PIL image for the state.
@param  tuple_in	0-based ( state_index, axial_level, assy_ndx )
"""
    state_ndx = tuple_in[ 0 ]
    assy_ndx = tuple_in[ 1 ]
    axial_level = tuple_in[ 2 ]
    print >> sys.stderr, \
        '[ChannelAssembly2DView._CreateRasterImage] tuple_in=%s' % str( tuple_in )
    im = None

    tuple_valid = DataModel.IsValidObj(
	self.data,
        assembly_index = assy_ndx,
	axial_level = axial_level,
	state_index = state_ndx
	)
    if self.config != None and tuple_valid:
      assy_region = self.config[ 'assemblyRegion' ]
      chan_gap = self.config[ 'channelGap' ]
      chan_wd = self.config[ 'channelWidth' ]
      im_wd, im_ht = self.config[ 'clientSize' ]
      font_size = self.config[ 'fontSize' ]
      label_font = self.config[ 'labelFont' ]
      legend_pil_im = self.config[ 'legendPilImage' ]
      pil_font = self.config[ 'pilFont' ]
      value_font = self.config[ 'valueFont' ]

      title_fmt = '%s: Assembly %%d, Axial %%.3f, %s %%.3g' % \
          ( self.channelDataSet, self.state.timeDataSet )
      title_size = pil_font.getsize( title_fmt % ( 99, 99.999, 99.999 ) )

      ds_value = \
          self.data.states[ state_ndx ].group[ self.channelDataSet ].value \
	  if self.channelDataSet in self.data.states[ state_ndx ].group \
	  else None
      ds_range = self.data.GetRange( self.channelDataSet )
      value_delta = ds_range[ 1 ] - ds_range[ 0 ]

      im = PIL.Image.new( "RGBA", ( im_wd, im_ht ) )
      #im_pix = im.load()
      im_draw = PIL.ImageDraw.Draw( im )

#			-- Loop on rows
#			--
      chan_y = assy_region[ 1 ]
      for chan_row in range( self.cellRange[ 1 ], self.cellRange[ 3 ], 1 ):

#				-- Row label
#				--
	if self.showLabels and chan_row < self.data.core.npin:
	  label = '%d' % (chan_row + 1)
	  label_size = label_font.getsize( label )
	  #label_y = chan_y + ((chan_wd - label_size[ 1 ]) >> 1)
	  label_y = chan_y + chan_wd + ((chan_gap - label_size[ 1 ]) >> 1)
	  im_draw.text(
	      ( 1, label_y ),
	      label, fill = ( 0, 0, 0, 255 ), font = label_font
	      )

#				-- Loop on col
#				--
	chan_x = assy_region[ 0 ]
	for chan_col in range( self.cellRange[ 0 ], self.cellRange[ 2 ], 1 ):
#					-- Column label
#					--
	  #if chan_row == self.cellRange[ 1 ] and self.showLabels:
	  if self.showLabels and chan_row == self.cellRange[ 1 ] and \
	      chan_col < self.data.core.npin:
	    label = '%d' % (chan_col + 1)
	    label_size = label_font.getsize( label )
	    #label_x = chan_x + ((chan_wd - label_size[ 0 ]) >> 1)
	    label_x = chan_x + chan_wd + ((chan_gap - label_size[ 0 ]) >> 1)
	    im_draw.text(
	        ( label_x, 1 ),
	        label, fill = ( 0, 0, 0, 255 ), font = label_font
	        )
	  #end if writing column label

	  value = 0.0
	  if ds_value != None:
	    value = ds_value[ chan_row, chan_col, axial_level, assy_ndx ]
	  if value > 0:
	    brush_color = Widget.GetColorTuple(
	        value - ds_range[ 0 ], value_delta, 255
	        )
	    pen_color = Widget.GetDarkerColor( brush_color, 255 )
	    #brush_color = ( pen_color[ 0 ], pen_color[ 1 ], pen_color[ 2 ], 255 )

	    im_draw.rectangle(
	        [ chan_x, chan_y, chan_x + chan_wd, chan_y + chan_wd ],
	        fill = brush_color, outline = pen_color
	        )

	    if value_font != None:
	      value_str = DataUtils.FormatFloat2( value )
	      e_ndx = value_str.lower().find( 'e' )
	      if e_ndx > 1:
	        value_str = value_str[ : e_ndx ]
	      value_size = value_font.getsize( value_str )
	      #if value_size[ 0 ] <= chan_wd:
	      if True:
		value_x = chan_x + ((chan_wd - value_size[ 0 ]) >> 1)
		value_y = chan_y + ((chan_wd - value_size[ 1 ]) >> 1) 
                im_draw.text(
		    ( value_x, value_y ), value_str,
		    fill = Widget.GetContrastColor( *brush_color ),
		    font = value_font
                    )
	    #end if value_font defined
	  #end if value > 0

	  chan_x += chan_wd + chan_gap
	#end for chan_col

	chan_y += chan_wd + chan_gap
      #end for chan_row

#			-- Draw pins
#			--
      if self.showPins:
        brush_color = ( 155, 155, 155, 128 )
        pen_color = Widget.GetDarkerColor( brush_color, 128 )
        pin_draw_wd = chan_wd >> 2

        pin_y = assy_region[ 1 ] + chan_wd + ((chan_gap - pin_draw_wd) >> 1)
        #for pin_row in range( self.data.core.npin ):
        #for pin_row in range( self.cellRange[ -1 ] - 1 ):
	for pin_row in range( self.cellRange[ 1 ], min( self.cellRange[ 3 ], self.data.core.npin ), 1 ):
	  pin_x = assy_region[ 0 ] + chan_wd + ((chan_gap - pin_draw_wd) >> 1)
	  #for pin_col in range( self.data.core.npin ):
	  #for pin_col in range( self.cellRange[ -2 ] - 1 ):
	  for pin_col in range( self.cellRange[ 0 ], min( self.cellRange[ 2 ], self.data.core.npin ), 1 ):
	    im_draw.ellipse(
	        [ pin_x, pin_y, pin_x + pin_draw_wd, pin_y + pin_draw_wd ],
	        fill = brush_color, outline = pen_color
	        )

	    pin_x += chan_wd + chan_gap
	  #end for pin_col

	  pin_y += chan_wd + chan_gap
        #end for pin_row
      #end if self.showPins

#			-- Draw Legend Image
#			--
#      im.paste( legend_pil_im, ( assy_region[ 2 ] + font_size, 0 ) )
      if legend_pil_im != None:
        im.paste(
	    legend_pil_im,
	    ( assy_region[ 2 ] + 2 + font_size, assy_region[ 1 ] )
	    )
	legend_size = legend_pil_im.size
      else:
	legend_size = ( 0, 0 )

#			-- Draw Title String
#			--
      chan_y = max( chan_y, legend_size[ 1 ] )
      chan_y += font_size >> 2

      title_str = title_fmt % ( \
	  assy_ndx + 1,
	  self.data.core.axialMeshCenters[ axial_level ],
	  self.data.GetTimeValue( state_ndx, self.state.timeDataSet )
	  )
      title_size = pil_font.getsize( title_str )
      title_x = max(
	  0,
          (assy_region[ 2 ] + font_size + legend_size[ 0 ] - title_size[ 0 ]) >> 1
	  )

      im_draw.text(
          ( title_x, chan_y ),
	  title_str, fill = ( 0, 0, 0, 255 ), font = pil_font
          )

      del im_draw
    #end if self.config exists

    return  im
  #end _CreateRasterImage


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._CreateStateTuple()	-
  #----------------------------------------------------------------------
  def _CreateStateTuple( self ):
    """
@return			( state_index, assy_ndx, axial_level )
"""
    return  ( self.stateIndex, self.assemblyIndex[ 0 ], self.axialValue[ 1 ] )
  #end _CreateStateTuple


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._CreateToolTipText()	-
  #----------------------------------------------------------------------
  def _CreateToolTipText( self, cell_info ):
    """Create a tool tip.
@param  cell_info	tuple returned from FindCell()
"""
    tip_str = ''
    valid = self.data.IsValid(
        assembly_index = self.assemblyIndex,
	axial_level = self.axialValue[ 1 ],
	dataset_name = self.channelDataSet,
	chan_colrow = cell_info[ 1 : 3 ],
	state_index = self.stateIndex
	)

    if valid:
      ds = self.data.states[ self.stateIndex ].group[ self.channelDataSet ]
      ds_value = ds[
          cell_info[ 2 ], cell_info[ 1 ],
	  self.axialValue[ 1 ], self.assemblyIndex[ 0 ]
	  ]

      if ds_value > 0.0:
        show_chan_addr = ( cell_info[ 1 ] + 1, cell_info[ 2 ] + 1 )
	tip_str = \
	    'Channel: %s\n%s: %g' % \
	    ( str( show_chan_addr ), self.channelDataSet, ds_value )
    #end if valid

    return  tip_str
  #end _CreateToolTipText


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.FindCell()		-
  #----------------------------------------------------------------------
  def FindCell( self, ev_x, ev_y ):
    """Calls FindChannel() and prepends -1 for an index value for
drag processing.
@return			None if no match, otherwise tuple of
			( -1, 0-based cell_col, cell_row )
"""
    chan_addr = self.FindChannel( ev_x, ev_y )
    return \
        None if chan_addr == None else \
	( -1, chan_addr[ 0 ], chan_addr[ 1 ] )
  #end FindCell


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.FindChannel()		-
  #----------------------------------------------------------------------
  def FindChannel( self, ev_x, ev_y ):
    """Finds the channel col and row.
@param  ev_x		event x coordinate (relative to this)
@param  ev_y		event y coordinate (relative to this)
@return			None if no match, otherwise tuple of
			( 0-based cell_col, cell_row )
"""
    result = None

    if self.config != None and self.data != None:
      if ev_x >= 0 and ev_y >= 0:
	assy_region = self.config[ 'assemblyRegion' ]
        chan_size = self.config[ 'channelWidth' ] + self.config[ 'channelGap' ]
        cell_x = min(
	    int( (ev_x - assy_region[ 0 ]) / chan_size ) + self.cellRange[ 0 ],
	    self.cellRange[ 2 ] - 1
	    )
	cell_x = max( self.cellRange[ 0 ], cell_x )
        cell_y = min(
	    int( (ev_y - assy_region[ 1 ]) / chan_size ) + self.cellRange[ 1 ],
	    self.cellRange[ 3 ] - 1
	    )
	cell_y = max( self.cellRange[ 1 ], cell_y )
	result = ( cell_x, cell_y )
      #end if event within display
    #end if we have data

    return  result
  #end FindChannel


  #----------------------------------------------------------------------
  #	METHOD:		GetAnimationIndexes()				-
  #----------------------------------------------------------------------
  def GetAnimationIndexes( self ):
    """Accessor for the list of indexes over which this widget can be
animated.  Possible values are 'axial:detector', 'axial:pin', 'statepoint'.
@return			list of indexes or None
"""
    return  ( 'axial:pin', 'statepoint' )
  #end GetAnimationIndexes


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.GetDataSetType()		-
  #----------------------------------------------------------------------
  def GetDataSetType( self ):
    return  'channel'
  #end GetDataSetType


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.GetEventLockSet()		-
  #----------------------------------------------------------------------
  def GetEventLockSet( self ):
    """By default, all locks are enabled except
"""
    locks = set([
        STATE_CHANGE_assemblyIndex, STATE_CHANGE_axialValue,
	STATE_CHANGE_channelColRow, STATE_CHANGE_channelDataSet,
	STATE_CHANGE_stateIndex, STATE_CHANGE_timeDataSet
	])
    return  locks
  #end GetEventLockSet


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.GetInitialCellRange()	-
  #----------------------------------------------------------------------
  def GetInitialCellRange( self ):
    """This implementation returns self.data.ExtractSymmetryExtent().
Subclasses should override as needed.
@return			intial range of raster cells
			( left, top, right, bottom, dx, dy )
"""
    result = None
    if self.data != None:
      result = [
          0, 0,
	  self.data.core.npin + 1, self.data.core.npin + 1,
	  self.data.core.npin + 1, self.data.core.npin + 1
          ]
    return  result
  #end GetInitialCellRange


  #----------------------------------------------------------------------
  #	METHOD:		RasterWidget.GetMenuDef()			-
  #----------------------------------------------------------------------
  def GetMenuDef( self, data_model ):
    """
"""
    menu_def = super( ChannelAssembly2DView, self ).GetMenuDef( data_model )
    menu_def.insert( 0, ( 'Hide Pins', self._OnTogglePins ) )
    return  menu_def
  #end GetMenuDef


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.GetTitle()		-
  #----------------------------------------------------------------------
  def GetTitle( self ):
    return  'Channel Assembly 2D View'
  #end GetTitle


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._HiliteBitmap()		-
  #----------------------------------------------------------------------
  def _HiliteBitmap( self, bmap ):
    result = bmap

    if self.config != None:
      rel_col = self.channelColRow[ 0 ] - self.cellRange[ 0 ]
      rel_row = self.channelColRow[ 1 ] - self.cellRange[ 1 ]

      if rel_col >= 0 and rel_col < self.cellRange[ -2 ] and \
          rel_row >= 0 and rel_row < self.cellRange[ -1 ]:
	assy_region = self.config[ 'assemblyRegion' ]
        chan_gap = self.config[ 'channelGap' ]
        chan_wd = self.config[ 'channelWidth' ]
	chan_adv = chan_gap + chan_wd
        line_wd = self.config[ 'lineWidth' ]

	rect = \
	  [
	    rel_col * chan_adv + assy_region[ 0 ],
	    rel_row * chan_adv + assy_region[ 1 ],
	    chan_wd + 1, chan_wd + 1
	  ]

	new_bmap = self._CopyBitmap( bmap )

        dc = wx.MemoryDC( new_bmap )
	gc = wx.GraphicsContext.Create( dc )
	gc.SetPen(
	    wx.ThePenList.FindOrCreatePen(
	        wx.Colour( 255, 0, 0, 255 ), line_wd, wx.PENSTYLE_SOLID
		)
	    )
	path = gc.CreatePath()
	path.AddRectangle( *rect )
	gc.StrokePath( path )
# This doesn't work on MSWIN
#	dc.SetBrush( wx.TRANSPARENT_BRUSH )
#        dc.SetPen(
#	    wx.ThePenList.FindOrCreatePen(
#	        wx.Colour( 255, 0, 0 ), line_wd, wx.PENSTYLE_SOLID
#		)
#	    )
#        dc.DrawRectangle( *rect )
	dc.SelectObject( wx.NullBitmap )

	result = new_bmap
      #end if within range
    #end if self.config != None:

    return  result
  #end _HiliteBitmap


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.IsTupleCurrent()		-
  #----------------------------------------------------------------------
  def IsTupleCurrent( self, tpl ):
    """
@param  tpl		tuple of state values
@return			True if it matches the current state, false otherwise
"""
    result = \
        tpl != None and len( tpl ) >= 3 and \
	tpl[ 0 ] == self.stateIndex and \
	tpl[ 1 ] == self.assemblyIndex[ 0 ] and \
	tpl[ 2 ] == self.axialValue[ 1 ]
    return  result
  #end IsTupleCurrent


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._LoadDataModelValues()	-
  #----------------------------------------------------------------------
  def _LoadDataModelValues( self ):
    """This noop version should be implemented in subclasses to initialize
attributes/properties that aren't already set in _LoadDataModel():
  axialValue
  stateIndex
"""
    self.assemblyIndex = self.state.assemblyIndex
    self.channelDataSet = self.state.channelDataSet
    self.channelColRow = self.state.channelColRow
  #end _LoadDataModelValues


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._OnClick()		-
  #----------------------------------------------------------------------
  def _OnClick( self, ev ):
    """
"""
    #ev.Skip()

#		-- Validate
#		--
    valid = False
    chan_addr = self.FindChannel( *ev.GetPosition() )
    if chan_addr != None and chan_addr != self.channelColRow:
      valid = self.data.IsValid(
          assembly_index = self.assemblyIndex[ 0 ],
	  axial_level = self.axialValue[ 1 ],
	  channel_colrow = chan_addr,
	  state_index = self.stateIndex
	  )

    if valid:
      ds = self.data.states[ self.stateIndex ].group[ self.channelDataSet ]
      ds_value = ds[ \
          chan_addr[ 1 ], chan_addr[ 0 ], self.axialValue[ 1 ], self.assemblyIndex[ 0 ] \
	  ]
      if ds_value > 0.0:
        self.FireStateChange( channel_colrow = chan_addr )
    #end if valid
  #end _OnClick


  #----------------------------------------------------------------------
  #	METHOD:		RasterWidget._OnTogglePins()			-
  #----------------------------------------------------------------------
  def _OnTogglePins( self, ev ):
    """Must be called on the UI thread.
"""
    ev.Skip()
    menu = ev.GetEventObject()
    item = menu.FindItemById( ev.GetId() )
    label = item.GetItemLabel()

#		-- Change Label for Toggle Items
#		--
    if label.startswith( 'Show' ):
      item.SetItemLabel( label.replace( 'Show', 'Hide' ) )
      self.showPins = True
    else:
      item.SetItemLabel( label.replace( 'Hide', 'Show' ) )
      self.showPins = False

#		-- Change Toggle Pins for Other Menu
#		--
    other_menu = \
        self.popupMenu \
	if menu == self.container.widgetMenu else \
	self.container.widgetMenu
    if other_menu != None:
      self._UpdateVisibilityMenuItems(
          other_menu,
	  'Pins', self.showPins
	  )

#		-- Redraw
#		--
    self.UpdateState( resized = True )
  #end _OnTogglePins


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView.SetDataSet()		-
  #----------------------------------------------------------------------
  def SetDataSet( self, ds_name ):
    """May be called from any thread.
"""
    if ds_name != self.channelDataSet:
      wx.CallAfter( self.UpdateState, channel_dataset = ds_name )
      self.FireStateChange( channel_dataset = ds_name )
  #end SetDataSet


  #----------------------------------------------------------------------
  #	METHOD:		ChannelAssembly2DView._UpdateStateValues()	-
  #----------------------------------------------------------------------
  def _UpdateStateValues( self, **kwargs ):
    """
@return			kwargs with 'changed' and/or 'resized'
"""
    kwargs = super( ChannelAssembly2DView, self )._UpdateStateValues( **kwargs )
    changed = kwargs.get( 'changed', False )
    resized = kwargs.get( 'resized', False )

    if 'assembly_index' in kwargs and kwargs[ 'assembly_index' ] != self.assemblyIndex:
      changed = True
      self.assemblyIndex = kwargs[ 'assembly_index' ]

    if 'channel_colrow' in kwargs and kwargs[ 'channel_colrow' ] != self.channelColRow:
      changed = True
      self.channelColRow = self.data.NormalizeChannelColRow( kwargs[ 'channel_colrow' ] )

    if 'channel_dataset' in kwargs and kwargs[ 'channel_dataset' ] != self.channelDataSet:
      resized = True
      self.channelDataSet = kwargs[ 'channel_dataset' ]

    if changed:
      kwargs[ 'changed' ] = True
    if resized:
      kwargs[ 'resized' ] = True

    return  kwargs
  #end _UpdateStateValues

#end ChannelAssembly2DView