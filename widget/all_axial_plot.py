#!/usr/bin/env python
# $Id$
#------------------------------------------------------------------------
#	NAME:		all_axial_plot.py				-
#	HISTORY:							-
#		2015-07-08	leerw@ornl.gov				-
#	  Extending PlotWidget.
#		2015-06-15	leerw@ornl.gov				-
#	  Refactoring.
#		2015-05-26	leerw@ornl.gov				-
#	  Migrating to global state.timeDataSet.
#		2015-05-23	leerw@ornl.gov				-
#	  New channel processing.
#		2015-05-12	leerw@ornl.gov				-
#		2015-05-11	leerw@ornl.gov				-
#	  Changed State.axialLevel to axialValue.
#		2015-04-22	leerw@ornl.gov				-
#	  Showing currently selected assembly.
#		2015-04-04	leerw@ornl.gov				-
#		2015-04-02	leerw@ornl.gov				-
#		2015-03-20	leerw@ornl.gov				-
# 	  Added tooltip.
#		2015-02-11	leerw@ornl.gov				-
#------------------------------------------------------------------------
import math, os, sys, time, traceback
import numpy as np
import pdb  # pdb.set_trace()

try:
  import matplotlib
  matplotlib.use( 'WXAgg' )
#  import matplotlib.pyplot as plt
except Exception:
  raise ImportError( 'The matplotlib module is required for this component' )

try:
  from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
  from matplotlib.backends.backend_wx import NavigationToolbar2Wx
  from matplotlib.figure import Figure
except Exception:
  raise ImportError, 'The wxPython matplotlib backend modules are required for this component'

try:
  import wx
#  import wx.lib.delayedresult as wxlibdr
#  from wx.lib.scrolledpanel import ScrolledPanel
except Exception:
  raise ImportError, 'The wxPython module is required for this component'

from bean.dataset_chooser import *
from event.state import *

from legend import *
from plot_widget import *
from widget import *
from widgetcontainer import *


PLOT_COLORS = [ 'b', 'r', 'g', 'm', 'c' ]
#        b: blue
#        g: green
#        r: red
#        c: cyan
#        m: magenta
#        y: yellow
#        k: black
#        w: white


#------------------------------------------------------------------------
#	CLASS:		AllAxialPlot					-
#------------------------------------------------------------------------
class AllAxialPlot( PlotWidget ):
  """Pin axial plot.

Properties:
"""


#		-- Object Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		__del__()					-
  #----------------------------------------------------------------------
  def __del__( self ):
    if self.dataSetDialog != None:
      self.dataSetDialog.Destroy()

    super( AllAxialPlot, self ).__del__()
  #end __del__


  #----------------------------------------------------------------------
  #	METHOD:		__init__()					-
  #----------------------------------------------------------------------
  def __init__( self, container, id = -1, **kwargs ):
    self.assemblyIndex = ( -1, -1, -1 )
#    self.ax = None
#    self.axialLine = None
    self.axialValue = ( 0.0, -1, -1 )
    #self.axialValues = []
#    self.canvas = None
    self.channelColRow = ( -1, -1 )
    self.channelDataSet = None
#    self.cursor = None
#    self.data = None
    self.dataSetDialog = None
    self.dataSetSelections = {}
    self.dataSetTypes = set()
    self.dataSetValues = {}  # keyed by dataset name
    self.detectorDataSet = None
    self.detectorIndex = ( -1, -1, -1 )
#    self.fig = None

#    self.lx = None
    self.menuDefs = [ ( 'Select Datasets', self._OnSelectDataSets ) ]
    self.pinColRow = ( -1, -1 )
    self.pinDataSet = kwargs.get( 'dataset', 'pin_powers' )
#    self.stateIndex = -1
#    self.titleFontSize = 16

    super( AllAxialPlot, self ).__init__( container, id, ref_axis = 'y' )
  #end __init__


  #----------------------------------------------------------------------
  #	METHOD:		_CreateToolTipText()				-
  #----------------------------------------------------------------------
  def _CreateToolTipText( self, ev ):
    """Create a tool tip.  This implementation returns a blank string.
@param  ev		mouse motion event
"""
    tip_str = ''
    ds_values = self._FindDataSetValues( ev.ydata )
    if ds_values != None:
      tip_str = 'Axial=%.3g' % ev.ydata
      ds_keys = ds_values.keys()
      ds_keys.sort()
      for k in ds_keys:
        tip_str += '\n%s=%.3g' % ( k, ds_values[ k ] )

    return  tip_str
  #end _CreateToolTipText


  #----------------------------------------------------------------------
  #	METHOD:		_DoUpdatePlot()					-
  #----------------------------------------------------------------------
  def _DoUpdatePlot( self, wd, ht ):
    """Do the work of creating the plot, setting titles and labels,
configuring the grid, plotting, and creating self.axline.  This implementation
calls self.ax.grid() and can be called by subclasses.
"""
    super( AllAxialPlot, self )._DoUpdatePlot( wd, ht )

    self.fig.suptitle(
        'Axial Plot',
	fontsize = 'medium', fontweight = 'bold'
	)

    label_font_size = 14
    tick_font_size = 12
    self.titleFontSize = 16
    if 'wxMac' not in wx.PlatformInfo and wd < 800:
      decr = (800 - wd) / 50.0
      label_font_size -= decr
      tick_font_size -= decr
      self.titleFontSize -= decr

#		-- Something to plot?
#		--
    if len( self.dataSetValues ) > 0:
#			-- Determine axis datasets
#			--
      bottom_ds_name = top_ds_name = None
      for k in self.dataSetValues:
        rec = self.dataSetSelections[ k ]
        if rec[ 'axis' ] == 'bottom':
	  bottom_ds_name = k
        elif rec[ 'axis' ] == 'top':
	  top_ds_name = k
      #end for
      if bottom_ds_name == None:
        for k in self.dataSetValues:
	  if top_ds_name != k:
	    bottom_ds_name = k
	    break

#			-- Configure axes
#			--
      if top_ds_name != None:
        #self.ax2 = self.ax.twiny()
        self.ax2.set_xlabel( top_ds_name, fontsize = label_font_size )
        self.ax2.set_xlim( *self.data.GetRange( top_ds_name ) )
	self.ax2.xaxis.get_major_formatter().set_powerlimits( ( -3, 3 ) )

      self.ax.set_xlabel( bottom_ds_name, fontsize = label_font_size )
      self.ax.set_xlim( *self.data.GetRange( bottom_ds_name ) )
      self.ax.set_ylabel( 'Axial (cm)', fontsize = label_font_size )
      self.ax.xaxis.get_major_formatter().set_powerlimits( ( -3, 3 ) )

#			-- Set title
#			--
      show_assy_addr = \
          self.data.core.CreateAssyLabel( *self.assemblyIndex[ 1 : 3 ] )

      title_str = 'Assy %d %s, %s %.3g' % \
          ( self.assemblyIndex[ 0 ] + 1, show_assy_addr,
	    self.state.timeDataSet,
	    self.data.GetTimeValue( self.stateIndex, self.state.timeDataSet )
	    )

      title_line2 = ''
      if 'channel' in self.dataSetTypes:
	chan_rc = ( self.channelColRow[ 0 ] + 1, self.channelColRow[ 1 ] + 1 )
        title_line2 += 'Chan %s' % str( chan_rc )

      if 'detector' in self.dataSetTypes: # and self.detectorIndex[ 0 ] >= 0
        if len( title_line2 ) > 0: title_line2 += ', '
	title_line2 += 'Det %d %s' % \
	    ( self.detectorIndex[ 0 ] + 1,
	      self.data.core.CreateAssyLabel( *self.detectorIndex[ 1 : 3 ] ) )

      if 'pin' in self.dataSetTypes: # and self.detectorIndex[ 0 ] >= 0
        pin_rc = ( self.pinColRow[ 0 ] + 1, self.pinColRow[ 1 ] + 1 )
        if len( title_line2 ) > 0: title_line2 += ', '
	title_line2 += 'Pin %s' % str( pin_rc )

      if len( title_line2 ) > 0:
        title_str += '\n' + title_line2

#			-- Plot each selected dataset
#			--
      count = 0
      for k in self.dataSetValues:
	rec = self.dataSetSelections[ k ]
	scale = rec[ 'scale' ] if rec[ 'axis' ] == '' else 1.0
	legend_label = k
	if scale != 1.0:
	  legend_label += '*%.3g' % scale

	if k in self.data.GetDataSetNames( 'detector' ):
	  axial_values = self.data.core.detectorMeshCenters
	  plot_type = '.'
	else:
	  axial_values = self.data.core.axialMeshCenters
	  plot_type = '-'

	plot_mode = PLOT_COLORS[ count % len( PLOT_COLORS ) ] + plot_type
	cur_axis = self.ax2 if rec[ 'axis' ] == 'top' else self.ax
	cur_axis.plot(
	    self.dataSetValues[ k ] * scale, axial_values, plot_mode,
	    label = legend_label, linewidth = 2
	    )

	count += 1
      #end for

#			-- Create legend
#			--
      handles, labels = self.ax.get_legend_handles_labels()
      if self.ax2 != None:
        handles2, labels2 = self.ax2.get_legend_handles_labels()
	handles += handles2
	labels += labels2

      self.fig.legend(
          handles, labels,
	  loc = 'upper right',
	  prop = { 'size': 'small' }
	  )
#      self.ax.legend(
#	  handles, labels,
#	  bbox_to_anchor = ( 1.05, 1 ), borderaxespad = 0., loc = 2
#	  )

      self.fig.text(
          0.1, 0.925, title_str,
	  horizontalalignment = 'left', verticalalignment = 'top'
	  )

#			-- Axial value line
#			--
      self.axline = \
          self.ax.axhline( color = 'r', linestyle = '-', linewidth = 1 )
      self.axline.set_ydata( self.axialValue[ 0 ] )
    #end if we have something to plot
  #end _DoUpdatePlot


  #----------------------------------------------------------------------
  #	METHOD:		_FindDataSetValues()				-
  #----------------------------------------------------------------------
  def _FindDataSetValues( self, axial_cm ):
    """Find matching dataset values for the axial.
@param  axial_cm	axial value
@return			dict by name of dataset values or None if no matches
"""

    values = {}
    for k in self.dataSetValues:
      ndx = -1

      if k in self.data.GetDataSetNames( 'detector' ):
        if self.data.core.detectorMeshCenters != None:
	  ndx = self.data.FindListIndex( self.data.core.detectorMeshCenters, axial_cm )
      else:
        ndx = self.data.FindListIndex( self.data.core.axialMeshCenters, axial_cm )
      if ndx >= 0:
        values[ k ] = self.dataSetValues[ k ][ ndx ]
    #end for

    return  values
  #end _FindDataSetValues


  #----------------------------------------------------------------------
  #	METHOD:		GetAxialValue()					-
  #----------------------------------------------------------------------
  def GetAxialValue( self ):
    """@return		( value, 0-based core index, 0-based detector index )
"""
    return  self.axialValue
  #end GetAxialValue


  #----------------------------------------------------------------------
  #	METHOD:		GetDataSetType()				-
  #----------------------------------------------------------------------
#  def GetDataSetType( self ):
#    return  'pin'
#  #end GetDataSetType


  #----------------------------------------------------------------------
  #	METHOD:		GetEventLockSet()				-
  #----------------------------------------------------------------------
  def GetEventLockSet( self ):
    """By default, all locks are enabled except
"""
    locks = set([
        STATE_CHANGE_assemblyIndex, STATE_CHANGE_axialValue,
	STATE_CHANGE_channelColRow, STATE_CHANGE_detectorIndex,
	STATE_CHANGE_pinColRow, STATE_CHANGE_stateIndex,
	STATE_CHANGE_timeDataSet
	])
    return  locks
  #end GetEventLockSet


  #----------------------------------------------------------------------
  #	METHOD:		GetMenuDef()					-
  #----------------------------------------------------------------------
  def GetMenuDef( self, data_model ):
    return  self.menuDefs
  #end GetMenuDef


  #----------------------------------------------------------------------
  #	METHOD:		GetTitle()					-
  #----------------------------------------------------------------------
  def GetTitle( self ):
    return  'Axial Plots'
  #end GetTitle


  #----------------------------------------------------------------------
  #	METHOD:		_InitAxes()					-
  #----------------------------------------------------------------------
  def _InitAxes( self ):
    """Initialize axes, 'ax', and 'ax2'.
"""
    self.ax = self.fig.add_axes([ 0.1, 0.1, 0.85, 0.65 ])
    self.ax2 = self.ax.twiny() if len( self.dataSetValues ) > 1 else None
  #end _InitAxes


  #----------------------------------------------------------------------
  #	METHOD:		_InitUI()					-
  #----------------------------------------------------------------------
#  def _InitUI( self ):
#    """Builds this UI component.  Obviously, must be called in the UI thread.
#"""
#    super( AllAxialPlot, self )._InitUI()
#    self.ax2 = None
#  #end _InitUI


  #----------------------------------------------------------------------
  #	METHOD:		_LoadDataModelValues()				-
  #----------------------------------------------------------------------
  def _LoadDataModelValues( self ):
    """This noop version should be implemented in subclasses to create a dict
to be passed to _UpdateState().  Assume self.data is valid.
@return			dict to be passed to _UpdateState()
"""
    if self.data != None and self.data.HasData():
      assy_ndx = self.data.NormalizeAssemblyIndex( self.state.assemblyIndex )
      axial_value = self.data.NormalizeAxialValue( self.state.axialValue )
      chan_colrow = self.data.NormalizeChannelColRow( self.state.channelColRow )
      detector_ndx = self.data.NormalizeDetectorIndex( self.state.detectorIndex )
      pin_colrow = self.data.NormalizePinColRow( self.state.pinColRow )
      state_ndx = self.data.NormalizeStateIndex( self.state.stateIndex )
      update_args = \
        {
	'assy_index': assy_ndx,
	'axial_value': axial_value,
	'channel_colrow': chan_colrow,
	'channel_dataset': self.channelDataSet,
	'detector_dataset': self.detectorDataSet,
	'detector_index': detector_ndx,
	'pin_colrow': pin_colrow,
	'pin_dataset': self.pinDataSet,
	'state_index': state_ndx,
	'time_dataset': self.state.timeDataSet
	}

    else:
      update_args = {}

    return  update_args
  #end _LoadDataModelValues


  #----------------------------------------------------------------------
  #	METHOD:		_OnMplMouseRelease()				-
  #----------------------------------------------------------------------
  def _OnMplMouseRelease( self, ev ):
    """
"""
    button = ev.button or 1
    if button == 1 and self.cursor != None:
      axial_value = self.data.CreateAxialValue( value = self.cursor[ 1 ] )
      self._UpdateState( axial_value = axial_value )
      self.FireStateChange( axial_value = axial_value )
  #end _OnMplMouseRelease


  #----------------------------------------------------------------------
  #	METHOD:		_OnSelectDataSets()				-
  #----------------------------------------------------------------------
  def _OnSelectDataSets( self, ev ):
    """Must be called from the UI thread.
"""
    if self.dataSetDialog == None:
      if self.data == None:
        wx.MessageBox( self, 'No data model', 'Select Datasets' ).ShowModal()
      else:
        ds_names = self.data.GetDataSetNames( 'axial' )
	self.dataSetDialog = DataSetChooserDialog( self, ds_names = ds_names )
    #end if

    if self.dataSetDialog != None:
      self.dataSetDialog.ShowModal( self.dataSetSelections )
      selections = self.dataSetDialog.GetResult()
      if selections != None:
        self.dataSetSelections = selections
	self._UpdateState( replot = True )
    #end if
  #end _OnSelectDataSets


  #----------------------------------------------------------------------
  #	METHOD:		SetDataSet()					-
  #----------------------------------------------------------------------
  def SetDataSet( self, ds_name ):
    """May be called from any thread.
"""
    wx.CallAfter( self._UpdateState, pin_dataset = ds_name )
    self.FireStateChange( pin_dataset = ds_name )
  #end SetDataSet


  #----------------------------------------------------------------------
  #	METHOD:		_UpdateDataSetValues()				-
  #----------------------------------------------------------------------
  def _UpdateDataSetValues( self ):
    """Rebuild dataset arrays to plot.
This noop version must be overridden by subclasses.
"""
    self.dataSetTypes.clear()
    self.dataSetValues.clear()

    if self.data != None and \
        self.data.IsValid( state_index = self.stateIndex ):
#      if self.data.core.axialMeshCenters != None:
#        self.refAxisValues = self.data.core.axialMeshCenters.tolist()
#      elif self.data.core.detectorMeshCenters != None:
#        self.refAxisValues = self.data.core.detectorMeshCenters.tolist()

      state_group = self.data.states[ self.stateIndex ].group

      for k in self.dataSetSelections:
        ds_rec = self.dataSetSelections[ k ]
        if ds_rec[ 'visible' ] and k in state_group:
	  ds = state_group[ k ]

	  if k in self.data.GetDataSetNames( 'channel' ):
	    valid = self.data.IsValid(
	        assembly_index = self.assemblyIndex,
		channel_colrow = self.channelColRow
	        )
	    if valid:
	      new_values = []
	      for i in range( self.data.core.nax ):
	        new_values.append(
		    ds[ self.channelColRow[ 0 ], self.channelColRow[ 1 ],
		        i, self.assemblyIndex[ 0 ] ]
		    )
              self.dataSetValues[ k ] = np.array( new_values )
              self.dataSetTypes.add( 'channel' )

	  elif k in self.data.GetDataSetNames( 'detector' ):
	    if self.data.IsValid( detector_index = self.detectorIndex[ 0 ] ):
	      self.dataSetValues[ k ] = ds[ :, self.detectorIndex[ 0 ] ]
              self.dataSetTypes.add( 'detector' )

	  elif k in self.data.GetDataSetNames( 'pin' ):
	    valid = self.data.IsValid(
	        assembly_index = self.assemblyIndex,
		pin_colrow = self.pinColRow
	        )
	    if valid:
	      new_values = []
	      for i in range( self.data.core.nax ):
	        new_values.append(
		    ds[ self.pinColRow[ 0 ], self.pinColRow[ 1 ],
		        i, self.assemblyIndex[ 0 ] ]
		    )
	      self.dataSetValues[ k ] = np.array( new_values )
              self.dataSetTypes.add( 'pin' )
	  #end if category match
        #end if visible
      #end for each dataset
    #end if valid state
  #end _UpdateDataSetValues


  #----------------------------------------------------------------------
  #	METHOD:		_UpdateStateValues()				-
  # Must be called from the UI thread.
  #----------------------------------------------------------------------
  def _UpdateStateValues( self, **kwargs ):
    """
Must be called from the UI thread.
@return			kwargs with 'redraw' and/or 'replot'
"""
    kwargs = super( AllAxialPlot, self )._UpdateStateValues( **kwargs )
    replot = kwargs.get( 'replot', False )
    redraw = kwargs.get( 'redraw', False )

    if 'assembly_index' in kwargs and kwargs[ 'assembly_index' ] != self.assemblyIndex:
      replot = True
      self.assemblyIndex = kwargs[ 'assembly_index' ]
    #end if

    if 'axial_value' in kwargs and kwargs[ 'axial_value' ] != self.axialValue:
      replot = True
      self.axialValue = kwargs[ 'axial_value' ]
    #end if

    if 'channel_colrow' in kwargs and kwargs[ 'channel_colrow' ] != self.channelColRow:
      replot = True
      self.channelColRow = kwargs[ 'channel_colrow' ]
    #end if

    if 'detector_index' in kwargs and kwargs[ 'detector_index' ] != self.detectorIndex:
      replot = True
      self.detectorIndex = kwargs[ 'detector_index' ]
    #end if

    if 'pin_colrow' in kwargs and kwargs[ 'pin_colrow' ] != self.pinColRow:
      replot = True
      self.pinColRow = kwargs[ 'pin_colrow' ]
    #end if

#    if 'pin_dataset' in kwargs and kwargs[ 'pin_dataset' ] != self.dataSetName:
#      replot = True
#      self.dataSetName = kwargs[ 'pin_dataset' ]
#    #end if

    if 'time_dataset' in kwargs:
      replot = True

    if redraw:
      kwargs[ 'redraw' ] = True
    if replot:
      kwargs[ 'replot' ] = True

    return  kwargs
  #end _UpdateStateValues

#end AllAxialPlot
