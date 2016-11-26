#!/usr/bin/env python
# $Id$
#------------------------------------------------------------------------
#	NAME:		veraview.py					-
#	HISTORY:							-
#		2016-11-26	leerw@ornl.gov				-
#	  Using Config.CanDragNDrop() as a gate for the "Window" menubar
#	  item.
#		2016-11-19	leerw@ornl.gov				-
#	  Added CreateWindow() and modified LoadDataModel() to have a
#	  widget_props param in support of widgets-to-window and dragging
#	  widgets to a different window.
#		2016-10-25	leerw@ornl.gov				-
#	  Using logging.
#		2016-10-02	leerw@ornl.gov				-
#	  Fixed bug where toolbar item event handlers were not removed
#	  in VeraViewFrame._UpdateToolBar(), resulting in double widgets
#	  after opening a new file.
#		2016-09-20	leerw@ornl.gov				-
#	  Added weights mode to the edit menu.
#		2016-09-03	leerw@ornl.gov				-
#	  Added TOOLBAR_ITEMS functions to enable core widgets only if
#	  core.nass gt 1, axial widgets if core.nax gt 1, and Time Plots
#	  only if data.GetStatesCount() gt 1.
#	  Only enable axial widgets if core.nax gt 1.
#		2016-08-20	leerw@ornl.gov				-
#	  Changing initial widgets to pin and plots only.
#	  Assigning last frame position and size on load.
#		2016-08-19	leerw@ornl.gov				-
#	  More messing with widget sizing in grids.
#		2016-08-16	leerw@ornl.gov				-
#	  Messing with widget sizing in grids.
#		2016-08-10	leerw@ornl.gov				-
#	  Added --skip-startup-session-check command-line arg.
#	  Turning off 3D widgets on config load.
#	  Using Environment3D.IsAvailable() as a test for enabling the
#	  3D widgets.
#		2016-07-07	leerw@ornl.gov				-
#	  Renaming "vanadium" to "fixed_detector".
#		2016-07-01	leerw@ornl.gov				-
#	  Adding load/save session menu items.
#		2016-06-27	leerw@ornl.gov				-
#	  Moved prompt for widget config.
#		2016-06-20	leerw@ornl.gov				-
#	  Putting in hooks for reading/writing widget configurations.
#		2016-06-04	leerw@ornl.gov				-
#	  Using new "ScalarPlot" replacement for TimePlot.		-
#		2016-05-25	leerw@ornl.gov				-
# 	  Special "vanadium" dataset.  Calling
#	  DataModel.CreateEmptyAxialValue()
#		2016-04-16	leerw@ornl.gov				-
#	  Added "Select Scale Mode" pullright on the Edit menu.
#		2016-03-16	leerw@ornl.gov				-
#	  Playing with grid sizing when adding widgets, might finally
#	  have a workable solution.
#	  Removed status bar since we're not using it and it eats
#	  vertical screen real estate.
#		2016-03-08	leerw@ornl.gov				-
#	  Added Volume3DView, separators in the toolbar, and the CASL
#	  logo.
#		2016-03-07	leerw@ornl.gov				-
#	  Added Slicer3DView.
#		2016-03-05	leerw@ornl.gov				-
#		2016-03-05	leerw@ornl.gov				-
#	  Replaced Core[XY]ZView with CoreAxial2DView.
#		2016-03-01	leerw@ornl.gov				-
#	  Added Core[XY]ZView widget.
#		2016-02-20	leerw@ornl.gov				-
#	  Added EVT_CHAR_HOOK to VeraViewFrame.
#		2016-01-22	leerw@ornl.gov				-
#	  Added Edit->Copy menu item.
#		2015-12-29	leerw@ornl.gov				-
#	  Added View menu with creation of Slicer3DFrame.
#		2015-12-07	leerw@ornl.gov				-
#	  Back to original icons.
#		2015-11-24	leerw@ornl.gov				-
#	  After change to GridSizerBean, checking for more than 16
#	  widget cells and prompting the user to confirm.
#		2015-11-12	leerw@ornl.gov				-
#	  Adding menu to create a pseudo dataset.
#		2015-09-17	leerw@ornl.gov				-
#	  Remove erroneous 'func' from the Time Plot toolbar item definition.
#	  Began addition of the "plot everything" function.
#		2015-08-25	leerw@ornl.gov				-
#	  Replacing various axial plots with AllAxialPlot and specific
#	  "selected" datasets enabled.
#		2015-07-27	leerw@ornl.gov				-
#	  Build 15 with fixes to dataset reference order.
#		2015-07-15	leerw@ornl.gov				-
#	  Build 14.
#		2015-07-11	leerw@ornl.gov				-
#	  New ChannelAssembly2DView.
#		2015-05-25	leerw@ornl.gov				-
#	  New menu for the global time dataset.
#		2015-05-11	leerw@ornl.gov				-
#	  New State.axialValue attribute.
#		2015-04-27	leerw@ornl.gov				-
#	  New detector view and plot.
#	  Added type to TOOLBAR_ITEMS with enable/disable of toolbar
#	  buttons based on available datasets by type/category.
#		2015-04-13	leerw@ornl.gov				-
#	  Added DataModel.Check() call in OpenFile().  Added call to
#	  frame _OnOpenFile() in OnEventLoopEnter().
#	  Doing OpenFile() as background task with _OpenFile{Begin,End}().
#		2015-04-11	leerw@ornl.gov				-
#		2015-04-10	leerw@ornl.gov				-
#	  Putting sliders on the frame.
#		2015-04-02	leerw@ornl.gov				-
#	  No longer enforcing aspect ratio on resize.
#		2015-02-14	leerw@ornl.gov				-
#	  Trying a grid editor.
#		2015-01-10	leerw@ornl.gov				-
#		2015-01-08	leerw@ornl.gov				-
#		2015-01-07	leerw@ornl.gov				-
#		2015-01-05	leerw@ornl.gov				-
#		2014-12-18	leerw@ornl.gov				-
#		2014-12-08	leerw@ornl.gov				-
#		2014-11-15	leerw@ornl.gov				-
#------------------------------------------------------------------------
import argparse, logging, os, sys, threading, traceback
import pdb  # set_trace()

try:
  import wx
  import wx.lib.delayedresult as wxlibdr
#except ImportException:
except Exception:
  raise ImportError( 'The wxPython module is required to run this program' )

#from bean.dataset_menu_item import *
#from bean.dataset_mgr import *
from bean.grid_sizer_dialog import *

from data.config import Config
from data.datamodel import *

from event.state import *

from view3d.env3d import *

from widget.image_ops import *
from widget.widget_config import *
from widget.widgetcontainer import *

from widget.bean.axial_slider import *
from widget.bean.dataset_menu import *
from widget.bean.exposure_slider import *


ID_REFIT_WINDOW = 1000

SCALE_MODES = \
  {
  'All State Points': 'all',
  'Current State Point': 'state'
  }

TITLE = 'VERAView Version 1.0.76'

TOOLBAR_ITEMS = \
  [
    {
    'widget': 'Core 2D View',
    'icon': 'Core2DView.1.32.png',
    'iconDisabled': 'Core2DView.disabled.1.32.png',
    'type': 'pin',
    'func': lambda d: d.core is not None and d.core.nass > 1
    },
    {
    'widget': 'Core Axial 2D View',
    'icon': 'CoreAxial2DView.1.32.png',
    'iconDisabled': 'CoreAxial2DView.disabled.1.32.png',
    'type': 'pin',
    'func': lambda d: d.core is not None and d.core.nax > 1
    },
    {
    'widget': 'Assembly 2D View',
    'icon': 'Assembly2DView.1.32.png',
    'iconDisabled': 'Assembly2DView.disabled.1.32.png',
    'type': 'pin'
    },
    { 'widget': 'separator' },
    {
    'widget': 'Channel Core 2D View',
    'icon': 'Channel2DView.1.32.png',
    'iconDisabled': 'Channel2DView.disabled.1.32.png',
    'type': 'channel',
    'func': lambda d: d.core is not None and d.core.nass > 1
    },
    {
    'widget': 'Channel Axial 2D View',
    'icon': 'ChannelAxial2DView.1.32.png',
    'iconDisabled': 'ChannelAxial2DView.disabled.1.32.png',
    'type': 'channel',
    'func': lambda d: d.core is not None and d.core.nax > 1
    },
    {
    'widget': 'Channel Assembly 2D View',
    'icon': 'ChannelAssembly2DView.1.32.png',
    'iconDisabled': 'ChannelAssembly2DView.disabled.1.32.png',
    'type': 'channel'
    },
    { 'widget': 'separator' },
    {
    'widget': 'Detector 2D Multi View',
    'icon': 'Detector2DView.1.32.png',
    'iconDisabled': 'Detector2DView.disabled.1.32.png',
    'type': 'detector'
    },
#    {
#    'widget': 'Detector 2D View', 'icon': 'Detector2DView.1.32.png',
#    'type': 'detector'
#    },
    { 'widget': 'separator' },
    {
    'widget': 'Volume Slicer 3D View',
    'icon': 'Slicer3DView.1.32.png',
    'iconDisabled': 'Slicer3DView.disabled.1.32.png',
    'type': 'pin',
    'func': lambda d: Environment3D.IsAvailable() and d.Is3DReady()
    },
    {
    'widget': 'Volume 3D View',
    'icon': 'Volume3DView.1.32.png',
    'iconDisabled': 'Volume3DView.disabled.1.32.png',
    'type': 'pin',
    'func': lambda d: Environment3D.IsAvailable() and d.Is3DReady()
    },
    { 'widget': 'separator' },
    {
    'widget': 'Axial Plots',
    'icon': 'AllAxialPlot.32.png',
    'iconDisabled': 'AllAxialPlot.disabled.32.png',
    'type': '',
    'func': lambda d: d.core is not None and d.core.nax > 1
#    'func': lambda d: 'exposure' in d.GetDataSetNames( 'scalar' )
    },
    {
    'widget': 'Time Plots',
    'icon': 'TimePlot.32.png',
    'iconDisabled': 'TimePlot.disabled.32.png',
    'type': '',
    'func': lambda d: d.GetStatesCount() > 1
    }
  ]

WEIGHTS_MODES = \
  {
  'Use Weights to Show/Hide Pins/Channels': 'on',
  'Show All Pins/Channels': 'off'
  }

WIDGET_MAP = \
  {
  'Assembly 2D View': 'widget.assembly_view.Assembly2DView',
  'Axial Plots': 'widget.axial_plot.AxialPlot',
  'Channel Core 2D View': 'widget.channel_view.Channel2DView',
  'Channel Assembly 2D View': 'widget.channel_assembly_view.ChannelAssembly2DView',
  'Channel Axial 2D View': 'widget.channel_axial_view.ChannelAxial2DView',
  'Core 2D View': 'widget.core_view.Core2DView',
  'Core Axial 2D View': 'widget.core_axial_view.CoreAxial2DView',
  'Detector 2D Multi View': 'widget.detector_multi_view.Detector2DMultiView',
#  'Detector 2D View': 'widget.detector_view.Detector2DView',
#  'Time Plot': 'widget.time_plot.TimePlot',
  'Time Plots': 'widget.time_plots.TimePlots',
  'Volume 3D View': 'view3d.volume_view.Volume3DView',
  'Volume Slicer 3D View': 'view3d.slicer_view.Slicer3DView'
  }


#------------------------------------------------------------------------
#	CLASS:		VeraViewApp					-
#------------------------------------------------------------------------
class VeraViewApp( wx.App ):
  """This will be the controller for now.
"""


#		-- Object Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.__init__()				-
  #----------------------------------------------------------------------
  def __init__( self, *args, **kwargs ):
    #super( VeraViewApp, self ).__init__( *args, **kwargs )
    super( VeraViewApp, self ).__init__( redirect = False )
    #super( VeraViewApp, self ).__init__( redirect = True, filename = 'run.log' )

    self.SetAppName( TITLE )

    #self.data = None
    #self.dataSetDefault = 'pin_powers'
    self.filepath = None
    self.firstLoop = True
    #self.frame = None
    self.frames = {}
    self.logger = logging.getLogger( 'root' )
    self.skipSession = False
    self.state = None

    wx.ToolTip.Enable( True )
    wx.ToolTip.SetAutoPop( 10000 )
    wx.ToolTip.SetDelay( 500 )
    wx.ToolTip.SetReshow( 100 )
  #end __init__


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.AddFrame()				-
  # These noworky
  #----------------------------------------------------------------------
  def AddFrame( self, frame ):
    """Adds a new VeraViewFrame.
"""
    if frame is not None:
#			-- Resolve Title
#			--
      n = 1
      while True:
        if n not in self.frames:
          break
        n += 1

      #cur_title = frame.GetTitle()
      #if not cur_title:
        #cur_title = TITLE
      #title = '%d: %s' % ( n, cur_title )
      frame.SetFrameId( n )
      frame.UpdateTitle()

      self.frames[ n ] = { 'frame': frame, 'n': n, 'title': frame.GetTitle() }
    #end if frame
  #end AddFrame


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.FindFrameByTitle()			-
  #----------------------------------------------------------------------
  def FindFrameByTitle( self, title ):
    """Finds the specified frame
@return			frame rec or None if not found
"""
    match = None
    title_n = 0
    if title:
      ndx = title.find( ':' )
      if ndx > 0:
        title_n = int( title[ 0 : ndx ] )

    if title_n > 0:
      for n, rec in self.frames.iteritems():
        #if rec[ 'title' ] == title:
	if n == title_n:
	  match = rec
	  break
      #end for n, rec
    #end if frame

    return  match
  #end FindFrameByTitle


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.GetFrames()				-
  #----------------------------------------------------------------------
  def GetFrames( self ):
    """Removes a new VeraViewFrame.
@return			frames dict
"""
    return  self.frames
  #end GetFrames


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.MacHideApp()			-
  # These noworky
  #----------------------------------------------------------------------
  def MacHideApp( self ):
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'entered' )
    pass
  #end MacHideApp


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.MacReopenApp()			-
  # These noworky
  #----------------------------------------------------------------------
  def MacReopenApp( self ):
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'entered' )
    self.BringWindowToFront()
  #end MacReopenApp


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.OnEventLoopEnter()			-
  #----------------------------------------------------------------------
  def OnEventLoopEnter( self, *args, **kwargs ):
    """It looks like this is called only once, so the firstLoop flag is
unnecessary.
"""
    #DEBUG,INFO,WARNING,ERROR,CRITICAL
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'entered' )

    frame_rec = self.frames.get( 1 )
    frame = frame_rec.get( 'frame' ) if frame_rec else None
    #if self.frame is None:
    if frame is None:
      self.logger.critical( '* No frame to show *' )
      self.ExitMainLoop()

    elif self.firstLoop:
      self.firstLoop = False
      #self.frame.GetStatusBar().SetStatusText( '' )

      opened = False
      session = WidgetConfig.ReadUserSession()
      #self.frame.SetConfig( session )
      frame.SetConfig( session )

      if self.filepath is None:
        #session = None if self.skipSession else WidgetConfig.ReadUserSession()
        if session is not None and not self.skipSession:
	  data_path = session.GetFilePath()
	  if os.path.exists( data_path ):
            ans = wx.MessageBox(
                'Load previous session?',
	        'Load Session',
	        wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL,
	        None
                )
            if ans == wx.YES:
	      opened = True
	      #self.frame.OpenFile( data_path, session )
	      frame.OpenFile( data_path, session )

      elif os.path.exists( self.filepath ):
	if self.filepath.lower().endswith( '.vview' ):
	  #data_path, session = self.frame._ResolveFile( self.filepath )
	  data_path, session = frame._ResolveFile( self.filepath )
	  if data_path is None:
	    wx.MessageBox(
		'Error reading session file: ' + self.filepath,
		'Open File', wx.OK | wx.CANCEL, None
	        )
	  else:
            opened = True
	    #self.frame.OpenFile( data_path, session )
	    frame.OpenFile( data_path, session )
	else:
	  opened = True
	  #self.frame.OpenFile( self.filepath )
	  frame.OpenFile( self.filepath )

      if not opened:
        #self.frame._OnOpenFile( None )
        frame._OnOpenFile( None )
    #end elif self.firstLoop:
  #end OnEventLoopEnter


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.OnInit()				-
  #----------------------------------------------------------------------
#  def OnInit( self ):
#    pass  # create and show frame here?
#  #end OnInit


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.RemoveFrame()			-
  #----------------------------------------------------------------------
  def RemoveFrame( self, frame ):
    """Removes a new VeraViewFrame.
"""
    rec = self.FindFrameByTitle( frame.GetTitle() )
    if rec:
      n = rec.get( 'n' )
      if n in self.frames:
        del self.frames[ n ]
    #end if
  #end RemoveFrame


#		-- Static Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewApp.main()				-
  #----------------------------------------------------------------------
  @staticmethod
  def main():
    try:
      parser = argparse.ArgumentParser()

#      parser.add_argument(
#	  '--assembly',
#	  default = 0,
#	  type = int,
#	  help = 'optional 1-based index of assembly to display'
#          )

#      parser.add_argument(
#	  '-a', '--axial',
#	  default = 0,
#	  type = int,
#	  help = 'optional 1-based index of core axial to display'
#          )

#      parser.add_argument(
#	  '-d', '--dataset',
#	  help = 'default dataset name, defaulting to "pin_powers"'
#          )

      parser.add_argument(
	  '-f', '--file-path',
	  help = 'path to HDF5 data file'
          )

      parser.add_argument(
	  '--skip-startup-session-check',
	  action = 'store_true',
	  help = 'skip the check for a session on startup when no file path is specified'
          )

#      parser.add_argument(
#	  '-s', '--state',
#	  default = 0,
#	  type = int,
#	  help = 'optional 1-based index of state to display' 
#          )

#      parser.add_argument(
#	  '--scale',
#	  type = int, default = 4,
#	  help = 'not being used right now',
#          )

      args = parser.parse_args()

      Config.SetRootDir( os.path.dirname( os.path.abspath( __file__ ) ) )
#      if args.dataset is not None:
#        Config.SetDefaultDataSet( args.dataset )

      data_model = None

#			-- Create State
#			--
      state = State()
#      if args.assembly is not None and args.assembly > 0:
#        state.assemblyIndex = ( args.assembly - 1, 0, 0 )
#      if args.axial is not None and args.axial > 0:
#        state.axialValue = DataModel.CreateEmptyAxialValue()
#      elif args.state is not None and args.state > 0:
#        state.stateIndex = args.state - 1

#			-- Create App
#			--
      #app = VeraViewApp( redirect = False )  # redirect = False
      app = VeraViewApp()
      app.filepath = args.file_path
      app.skipSession = args.skip_startup_session_check
      app.state = state

      #app.frame = VeraViewFrame( app, state )
      frame = VeraViewFrame( app, state )
      app.AddFrame( frame )
#			-- If MDI on Mac, don't show
      #app.frame.Show()
      frame.Show()
      app.MainLoop()

    except Exception, ex:
      msg = str( ex )
      print >> sys.stderr, str( ex )
      et, ev, tb = sys.exc_info()
      while tb:
	msg += \
	    os.linesep + 'File=' + str( tb.tb_frame.f_code ) + \
	    ', Line=' + str( traceback.tb_lineno( tb ) )
	print >> sys.stderr, \
            'File=' + str( tb.tb_frame.f_code ) + \
            ', Line=' + str( traceback.tb_lineno( tb ) )
        tb = tb.tb_next
      #end while
      logging.error( msg )
  #end main

#end VeraViewApp


#------------------------------------------------------------------------
#	CLASS:		VeraViewFrame					-
#------------------------------------------------------------------------
#class VeraViewFrame( wx.MDIParentFrame ):
class VeraViewFrame( wx.Frame ):
  """Top level viewer window.
"""


#		-- Object Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.__init__()			-
  #----------------------------------------------------------------------
  def __init__( self, app, state, file_path = '' ):
    super( VeraViewFrame, self ).__init__( None, -1 )

    self.app = app
    self.axialPlotTypes = set()
    self.config = None
#    self.dataSetDefault = ds_default
    self.eventLocks = State.CreateLocks()
    self.filepath = file_path
    self.frameId = 0
    self.logger = logging.getLogger( 'root' )
    self.state = state
    self.windowMenu = None

    self.axialBean = None
    self.dataSetMenu = None
    self.exposureBean = None
    self.grid = None
    self.scaleModeItems = {}
    self.timeDataSetMenu = None
    self.weightsModeItems = {}
    self.widgetToolBar = None

    self._InitUI()
  #end __init__


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.AddWidgetContainer()		-
  #----------------------------------------------------------------------
  def AddWidgetContainer( self, wc, refit_flag = True ):
    """Called by Create[23]DWidget() to add a grid with the container.
The hackit deal is pure ugliness but seems necessary given the weirdess
in GridSizer when adding grids.
@param  wc		WidgetContainer instance to add
@param  refit_flag	True to refit the window after adding
"""
#xxxxx check setting grow_flag *only* when a row is added on other platforms
    grow_flag = False
#    grow_flag = True
    grid_sizer = self.grid.GetSizer()
    widget_count = len( self.grid.GetChildren() )
    widget_space = grid_sizer.GetCols() * grid_sizer.GetRows()
    if widget_count > widget_space:
#      grow_flag = True
      if widget_space == 1:
        grid_sizer.SetCols( grid_sizer.GetCols() + 1 )
      elif grid_sizer.GetCols() > grid_sizer.GetRows():
	grid_sizer.SetRows( grid_sizer.GetRows() + 1 )
	grow_flag = True
      else:
	#grow_flag = grid_sizer.GetCols() >= 2
        grid_sizer.SetCols( grid_sizer.GetCols() + 1 )
    #end if

    frame_size = self.GetSize()
    self.grid._FreezeWidgets()
    grid_sizer.Add( wc, 0, wx.ALIGN_CENTER | wx.EXPAND, 0 )
    self.grid.Layout()
#		-- If you don't call Fit() here, the window will not grow
#		-- with the addition of the new widget
    if grow_flag:
      refit_flag = True
      #self.Fit()

    #self.grid._FreezeWidgets( False )
    if refit_flag:
      wx.CallAfter( self._Refit, False, self.grid._FreezeWidgets, False )
    else:
      self.grid._FreezeWidgets( False )
  #end AddWidgetContainer


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.CloseAllWidgets()			-
  #----------------------------------------------------------------------
  def CloseAllWidgets( self ):
    close_list = []
    for child in self.grid.GetChildren():
      if isinstance( child, WidgetContainer ):
        close_list.append( child )
    #end for

    for child in close_list:
      child.Destroy()
  #end CloseAllWidgets


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.Create2DWidget()			-
  #----------------------------------------------------------------------
  def Create2DWidget( self, widget_class, refit_flag = True ):
    """Must be called on the UI thread.
@return		widget container object
"""
    wc = WidgetContainer( self.grid, widget_class, self.state )
    self.AddWidgetContainer( wc, refit_flag )
    return  wc
  #end Create2DWidget


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.Create3DWidget()			-
  #----------------------------------------------------------------------
  def Create3DWidget( self, widget_class, refit_flag = True ):
    """Must be called on the UI thread.
"""
    def check_3d_env( loaded, errors ):
      if errors:
        msg = \
	    'Error loading 3D envrionment:' + os.linesep + \
	    os.linesep.join( errors )
        wx.MessageBox(
	    msg, 'Create 3D Widget',
	    wx.ICON_ERROR | wx.OK_DEFAULT
	    )
      elif loaded:
        wc = WidgetContainer( self.grid, widget_class, self.state )
        self.AddWidgetContainer( wc, refit_flag )
    #end check_and_show

    Environment3D.LoadAndCall( check_3d_env )
  #end Create3DWidget


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._CreateToolBarItem()		-
  #----------------------------------------------------------------------
  def _CreateToolBarItem( self, tbar, tool_id, tool_def, enabled = False ):
    """It seems necessary to re-create tool items to show a different icon.
@param  tbar		owning toolbar
@param  tool_id		tool id
@param  tool_def	definition from TOOLBAR_ITEMS
@return			ToolBarToolBase
"""
    widget_icon = tool_def.get( 'icon' if enabled else 'iconDisabled' )
    widget_name = tool_def[ 'widget' ]
    widget_im = wx.Image(
        os.path.join( Config.GetResDir(), widget_icon ),
	wx.BITMAP_TYPE_PNG
	)

    tip = widget_name
    if not enabled:
      tip += ' (disabled)'

    tb_item = tbar.AddTool(
        tool_id, widget_im.ConvertToBitmap(),
        shortHelpString = tip
	)
    tb_item.Enable( enabled )
    self.Bind( wx.EVT_TOOL, self._OnWidgetTool, id = tool_id )

    return  tb_item
  #end _CreateToolBarItem


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.CreateWidget()			-
  #----------------------------------------------------------------------
  def CreateWidget( self, widget_class, refit_flag = True ):
    """Must be called on the UI thread.  Note we are determining the need
to load the 3D viz environment based on "3D" being in the class name.
This is precarious but fast for now to avoid the double O(n) lookups in
WIDGET_MAP and TOOLBAR_ITEMS
@return		WidgetContainer object for 2D, None for a 3D widget
"""
    wc = None

    data = State.FindDataModel( self.state )
    if data is None:
      msg = 'A VERAOutput file must be opened'
      wx.MessageDialog( self, msg, 'Add Widget' ).ShowWindowModal()

    else:
      try:
        if widget_class.find( '3D' ) >= 0:
          self.Create3DWidget( widget_class, refit_flag )
        else:
          wc = self.Create2DWidget( widget_class, refit_flag )
#x	  title = wc.widget.GetTitle()
#x          if title == 'Axial Plots':
#x	    #wc.widget.InitDataSetSelections( self.axialPlotTypes )
#x	    wc.widget.InitDataSetSelections( [ 'channel', 'pin' ] )
#x          elif title == 'Detector 2D Multi View':
#x	    pass
#x	    wc.widget.InitDataSetSelections(
#x	        data.GetFirstDataSet( 'detector' ),
#x	        data.GetFirstDataSet( 'fixed_detector' )
#x		)
#x          elif title == 'Time Plots':
#x	    wc.widget.InitDataSetSelections(
#x	        [ 'channel', 'pin' ]
#x	        #[ 'detector', 'fixed_detector', 'pin', 'scalar' ]
#x		)
      except Exception, ex:
        wx.MessageDialog( self, str( ex ), 'Widget Error' ).ShowWindowModal()
    #end if-else

    return  wc
  #end CreateWidget


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.CreateWindow()			-
  #----------------------------------------------------------------------
  def CreateWindow( self, widget_props = None ):
    new_frame = VeraViewFrame( self.app, self.state, self.filepath )
    self.app.AddFrame( new_frame )
    new_frame.Show()

    if Config.CanDragNDrop():
      self._UpdateWindowMenus( add_frame = new_frame )

    if widget_props:
      wx.CallAfter(
          new_frame.LoadDataModel,
	  self.filepath, widget_props = widget_props
	  )
  #end CreateWindow


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.CreateWindow()			-
  #----------------------------------------------------------------------
#  def CreateWindow( self, wc = 'emtpy' ):
#    new_frame = VeraViewFrame( self.app, self.state, self.filepath )
#    self.app.AddFrame( new_frame )
#    new_frame.Show()
#
#    self._UpdateWindowMenus( add_frame = new_frame )
#    wx.CallAfter( new_frame.LoadDataModel, self.filepath, wc = wc )
#  #end CreateWindow


#  #----------------------------------------------------------------------
#  #	METHOD:		VeraViewFrame.FireStateChange()			-
#  #----------------------------------------------------------------------
#  def FireStateChange( self, reason ):
#    if reason != STATE_CHANGE_noop:
#      for child in self.GetChildren():
#        if isinstance( child, WidgetContainer ):
#	  child.HandleStateChange( reason )
#      #end for
#    #end if
#  #end FireStateChange


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.GetConfig()			-
  #----------------------------------------------------------------------
  def GetConfig( self ):
    """Accessor for the config property.
@return			WidgetConfig object
"""
    return  self.config
  #end GetConfig


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.GetDataModel()			-
  #----------------------------------------------------------------------
  def GetDataModel( self ):
    """Convenience accessor for the state.dataModel property.
@return			DataModel object
"""
    #return  None if self.state is None else self.state.GetDataModel()
    return  State.FindDataModel( self.state )
  #end GetDataModel


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.GetFrameId()			-
  #----------------------------------------------------------------------
  def GetFrameId( self ):
    """Accessor for the frameId property.
@return			1-based ordinal number
"""
    return  self.frameId
  #end GetFrameId


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.GetState()			-
  #----------------------------------------------------------------------
  def GetState( self ):
    """Accessor for the state property.
@return			State object
"""
    return  self.state
  #end GetState


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.HandleStateChange()		-
  #----------------------------------------------------------------------
  def HandleStateChange( self, reason ):
    if self.logger.isEnabledFor( logging.INFO ):
      self.logger.info( '[VeraViewFrame.HandleStateChange] reason=%d', reason )

    if (reason & STATE_CHANGE_axialValue) > 0:
      if self.state.axialValue[ 1 ] != self.axialBean.axialLevel:
        self.axialBean.axialLevel = self.state.axialValue[ 1 ]

    if (reason & STATE_CHANGE_stateIndex) > 0:
      if self.state.stateIndex != self.exposureBean.stateIndex:
        self.exposureBean.stateIndex = self.state.stateIndex
  #end HandleStateChange


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._InitUI()				-
  #----------------------------------------------------------------------
  def _InitUI( self ):
#		-- File Menu
#		--
    file_menu = wx.Menu()

#			-- File->New Submenu
    new_menu = wx.Menu()
    new_window_item = wx.MenuItem( new_menu, wx.ID_ANY, '&Window' )
    self.Bind( wx.EVT_MENU, self._OnNewWindow, new_window_item )
    new_menu.AppendItem( new_window_item )
    new_menu.AppendSeparator()

    widget_keys = WIDGET_MAP.keys()
    widget_keys.sort()
    #for k in WIDGET_MAP:
    for k in widget_keys:
      item = wx.MenuItem( new_menu, wx.ID_ANY, k )
      self.Bind( wx.EVT_MENU, self._OnNewWidget, item )
      new_menu.AppendItem( item )
    file_menu.AppendSubMenu( new_menu, '&New' )

#			-- Open item
    open_item = wx.MenuItem( file_menu, wx.ID_ANY, '&Open...\tCtrl+O' )
    self.Bind( wx.EVT_MENU, self._OnOpenFile, open_item )
    file_menu.AppendItem( open_item )

#    save_im_item = wx.MenuItem( file_menu, wx.ID_ANY, '&Save Image\tCtrl+S' )
#    self.Bind( wx.EVT_MENU, self._OnSaveWindow, save_im_item )
#    file_menu.AppendItem( save_im_item )

#			-- Session items
    file_menu.AppendSeparator()
    load_session_item = wx.MenuItem(
        file_menu, wx.ID_ANY,
	'Load Session...'
	)
    self.Bind( wx.EVT_MENU, self._OnLoadSession, load_session_item )
    file_menu.AppendItem( load_session_item )

    save_session_item = wx.MenuItem(
        file_menu, wx.ID_ANY,
	'Save Session...'
	)
    self.Bind( wx.EVT_MENU, self._OnSaveSession, save_session_item )
    file_menu.AppendItem( save_session_item )

#			-- Save images
    file_menu.AppendSeparator()
    save_item = wx.MenuItem(
        file_menu, wx.ID_ANY,
	'&Save Image of All Widgets...\tCtrl+Shift+S'
	)
    self.Bind( wx.EVT_MENU, self._OnSaveImageAllWidgets, save_item )
    file_menu.AppendItem( save_item )
    file_menu.AppendSeparator()

    min_item = wx.MenuItem( file_menu, wx.ID_ANY, '&Minimize Window\tCtrl+M' )
    self.Bind( wx.EVT_MENU, self._OnMinimizeWindow, min_item )
    file_menu.AppendItem( min_item )

    file_menu.AppendSeparator()
    quit_item = wx.MenuItem( file_menu, wx.ID_ANY, '&Quit\tCtrl+Q' )
    self.Bind( wx.EVT_MENU, self._OnQuit, quit_item )
    file_menu.AppendItem( quit_item )

#		-- Edit Menu
#		--
    edit_menu = wx.Menu()
    copy_item = wx.MenuItem( edit_menu, wx.ID_ANY, '&Copy\tCtrl+C' )
    self.Bind( wx.EVT_MENU, self._OnCopy, copy_item )
    edit_menu.AppendItem( copy_item )

    grid_item = wx.MenuItem( edit_menu, wx.ID_ANY, 'Resize &Grid\tCtrl+G' )
    self.Bind( wx.EVT_MENU, self._OnGridResize, grid_item )
    edit_menu.AppendItem( grid_item )

    edit_menu.AppendSeparator()

#    datasets_item = wx.MenuItem( edit_menu, wx.ID_ANY, 'Manage Extra DataSets...' )
#    self.Bind( wx.EVT_MENU, self._OnManageDataSets, datasets_item )
#    edit_menu.AppendItem( datasets_item )

#			-- Select dataset
#    self.dataSetMenu = DataSetMenu(
#        self, 'subsingle',
#	ds_types = [ 'channel', 'detector', 'fixed_detector', 'pin', 'scalar' ]
#	)
#    dataset_item = wx.MenuItem( edit_menu, wx.ID_ANY, 'Select Dataset...' )
#    self.Bind( wx.EVT_MENU, self._OnSelectDataSet, dataset_item )
    self.dataSetMenu = \
        DataSetMenu( self.state, binder = self, mode = 'subsingle' )
    dataset_item = wx.MenuItem(
        edit_menu, wx.ID_ANY, 'Select Dataset',
	subMenu = self.dataSetMenu
	)
    edit_menu.AppendItem( dataset_item )

#		 	-- Scale Mode
    scale_mode_menu = wx.Menu()
    check_item = None
    for label in sorted( SCALE_MODES.keys() ):
      item = wx.MenuItem( scale_mode_menu, wx.ID_ANY, label, kind = wx.ITEM_RADIO )
      scale_mode = SCALE_MODES.get( label )
      if scale_mode == 'all':
	check_item = item
      self.Bind( wx.EVT_MENU, self._OnScaleMode, item )
      scale_mode_menu.AppendItem( item )
      self.scaleModeItems[ scale_mode ] = item
    #end for
    if check_item:
      check_item.Check()
    scale_mode_item = wx.MenuItem(
        edit_menu, wx.ID_ANY, 'Select Scale Mode',
	subMenu = scale_mode_menu
	)
    edit_menu.AppendItem( scale_mode_item )

#		 	-- Time Dataset
    self.timeDataSetMenu = wx.Menu()
    time_item = wx.MenuItem(
        edit_menu, wx.ID_ANY, 'Select Time Dataset',
	subMenu = self.timeDataSetMenu
	)
    edit_menu.AppendItem( time_item )

#		 	-- Weights Mode
    weights_mode_menu = wx.Menu()
    check_item = None
    for label in sorted( WEIGHTS_MODES.keys() ):
      item = wx.MenuItem( weights_mode_menu, wx.ID_ANY, label, kind = wx.ITEM_RADIO )
      weights_mode = WEIGHTS_MODES.get( label )
      if weights_mode == 'on':
	check_item = item
      self.Bind( wx.EVT_MENU, self._OnWeightsMode, item )
      weights_mode_menu.AppendItem( item )
      self.weightsModeItems[ weights_mode ] = item
    #end for
    if check_item:
      check_item.Check()
    weights_mode_item = wx.MenuItem(
        edit_menu, wx.ID_ANY, 'Select Weights Mode',
	subMenu = weights_mode_menu
	)
    edit_menu.AppendItem( weights_mode_item )

#		-- View Menu
#		--
#    view_menu = wx.Menu()
#    view3d_item = wx.MenuItem( view_menu, wx.ID_ANY, '3D Volume Slicer' )
#    self.Bind( wx.EVT_MENU, self._OnView3D, view3d_item )
#    view_menu.AppendItem( view3d_item )

#		-- Window Menu
#		--
    if Config.CanDragNDrop():
      self.windowMenu = wx.Menu()
      tile_item = wx.MenuItem( self.windowMenu, wx.ID_ANY, 'Tile Windows' )
      self.Bind( wx.EVT_MENU, self._OnTileWindows, tile_item )
      self.windowMenu.AppendItem( tile_item )
      self.windowMenu.AppendSeparator()
#    raise_all_item = wx.MenuItem( self.windowMenu, wx.ID_ANY, 'Bring All To Front' )
#    self.Bind( wx.EVT_MENU, self.RaiseAllWidgets, raise_all_item )
#    self.windowMenu.AppendItem( raise_all_item )
#    self.windowMenu.AppendSeparator()

#		-- Menu Bar
#		--
    mbar = wx.MenuBar()
    mbar.Append( file_menu, '&File' )
    mbar.Append( edit_menu, '&Edit' )
#    mbar.Append( view_menu, '&View' )
    if self.windowMenu:
      mbar.Append( self.windowMenu, '&Window' )
    self.SetMenuBar( mbar )

#		-- Widget Tool Bar
#		--
    # wx.{NO,RAISED,SIMPLE,SUNKEN}_BORDER
    tbar_panel = wx.Panel( self )
    widget_tbar = wx.ToolBar(
        tbar_panel, -1,
	style = wx.TB_HORIZONTAL | wx.SIMPLE_BORDER
	)
    self.widgetToolBar = widget_tbar
    #self._UpdateToolBar( widget_tbar )

    tbar_sizer = wx.BoxSizer( wx.HORIZONTAL )
    tbar_sizer.Add( widget_tbar, 1, wx.ALL | wx.EXPAND )
    logo_im = wx.Image(
        os.path.join( Config.GetResDir(), 'casl-logo.32.png' ),
	wx.BITMAP_TYPE_PNG
	)
#    tbar_sizer.Add(
#	wx.StaticBitmap( tbar_panel, -1, logo_im.ConvertToBitmap() ),
#	0, wx.ALL | wx.ALIGN_RIGHT
#        )
    casl_icon = wx.StaticBitmap( tbar_panel, -1, logo_im.ConvertToBitmap() )
    casl_icon.SetDropTarget( VeraViewFrameDropTarget( self ) )
    tbar_sizer.Add( casl_icon, 0, wx.ALL | wx.ALIGN_RIGHT )
    tbar_panel.SetSizer( tbar_sizer )

#		-- Status Bar
#		--
    #status_bar = self.CreateStatusBar()
    #status_bar.SetStatusText( 'Creating...' )

#		-- Icons
#    icon_fname = os.path.join( os.path.dirname( __file__ ), 'reactor_icon.iconset', 'test128.gif' )
#    icon_img = wx.Image( icon_fname )
#    if 'wxMSW' in wx.PlatformInfo:
#      icon_img.Scale( 16, 16 )
#    elif 'wxGTK' in wx.PlatformInfo:
#      icon_img.Scale( 22, 22 )
#    self.SetIcon( wx.IconFromBitmap( icon_img.ConvertToBitmap() ) )

#		-- Axial slider
#		--
    inside_panel = wx.Panel( self )
    self.axialBean = AxialSliderBean( inside_panel )
    self.axialBean.Bind( EVT_AXIAL_LEVEL, self._OnAxial )
    self.axialBean.Enable()

#		-- Grid
#		--
    self.grid = VeraViewGrid( inside_panel, -1 )
#    self.grid.SetListener( self )

#		-- Exposure slider
#		--
    self.exposureBean = ExposureSliderBean( self )
    self.exposureBean.Bind( EVT_STATE_INDEX, self._OnExposure )
    self.exposureBean.Enable()

#		-- Lay Out
#		--
    inside_sizer = wx.BoxSizer( wx.HORIZONTAL )
    inside_sizer.Add( self.grid, 1, wx.ALL | wx.EXPAND )
    inside_sizer.Add( self.axialBean, 0, wx.ALL | wx.EXPAND, 1 )
    inside_panel.SetSizer( inside_sizer )

    vbox = wx.BoxSizer( wx.VERTICAL )
    #vbox.Add( widget_tbar, 0, wx.EXPAND, 0 )
    vbox.Add( tbar_panel, 0, wx.EXPAND, 0 )
    vbox.Add( inside_panel, 1, wx.EXPAND, 0 )
    vbox.Add( self.exposureBean, 0, wx.ALL | wx.EXPAND, 1 )
    self.SetSizer( vbox )
    vbox.Layout()
    self.Fit()
    self.SetTitle( TITLE )

#    self.Center()
    #pos = ( 5, 35 ) if 'wxMac' in wx.PlatformInfo else ( 5, 5 )
    #self.SetPosition( pos )
    client_rect = wx.GetClientDisplayRect()
    self.SetPosition( client_rect.GetPosition() )

    #display_size = wx.DisplaySize()
    display_size = client_rect.GetSize()
    #if display_size[ 0 ] >= 1200 and display_size[ 1 ] >= 800:
    if display_size[ 0 ] >= 1024 and display_size[ 1 ] >= 768:
      self.SetSize( ( 1024, 768 ) )
    elif display_size[ 0 ] >= 800 and display_size[ 1 ] >= 600:
      self.SetSize( ( 800, 600 ) )
    else:
      self.SetSize( ( 640, 480 ) )

#		-- Window Events
#		--
    self.state.AddListener( self )
    self.Bind( wx.EVT_CHAR_HOOK, self._OnCharHook )
    self.Bind( wx.EVT_CLOSE, self.OnCloseFrame )
  #end _InitUI


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.LoadDataModel()			-
  #----------------------------------------------------------------------
  def LoadDataModel( self, file_path, session = None, widget_props = None ):
    """Called when a data file is opened and set in the state.
Must be called from the UI thread.
@param  file_path	path to VERAOutput file
@param  session		optional WidgetConfig instance for session restoration
@param  widget_props	None = for default processing to load all applicable
			widgets;
			'empty' = no widgets
			widget = properties for widget to add
			#widget = single widget container to add
"""
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'file_path=%s', file_path )

    data = self.state.GetDataModel()
    self.filepath = file_path
    self.SetRepresentedFilename( file_path )

    #self.GetStatusBar().SetStatusText( 'Loading data model...' )

#		-- Update dataset selection menu
#		--
    self.dataSetMenu.Init()

#		-- Re-create time dataset menu
#		--
    while self.timeDataSetMenu.GetMenuItemCount() > 0:
      self.timeDataSetMenu.\
          DestroyItem( self.timeDataSetMenu.FindItemByPosition( 0 ) )

    check_item = None
    ds_names = data.GetDataSetNames( 'time' )
    for ds in ds_names:
      item = wx.MenuItem( self.timeDataSetMenu, wx.ID_ANY, ds, kind = wx.ITEM_RADIO )
      if ds == self.state.timeDataSet:
        check_item = item
      self.Bind( wx.EVT_MENU, self._OnTimeDataSet, item )
      self.timeDataSetMenu.AppendItem( item )
    #end for

    if check_item is not None:
      check_item.Check()

#		-- Update toolbar
#		--
# Merely enabling/disabling a tool by calling ToolBar.EnableTool() does
# not work!!  The same bitmap is used.  So, we re-create the tool.
    self._UpdateToolBar( self.widgetToolBar )

#    ti_count = 1
#    for ti in TOOLBAR_ITEMS:
#      item = self.widgetToolBar.FindById( ti_count )
#      if item is not None:
#        ds_names = data.GetDataSetNames()
#        ds_type = ti[ 'type' ]
#
#        enabled = \
#	    ( ds_type is None or ds_type == '' ) or \
#            ( ds_type in ds_names and ds_names[ ds_type ] is not None and \
#	      len( ds_names[ ds_type ] ) > 0 )
#	if enabled and 'func' in ti:
#	  enabled = ti[ 'func' ]( data )
#
#	if enabled:
#	  pos = self.widgetToolBar.GetToolPos( ti_count )
#	  self.widgetToolBar.RemoveTool( ti_count )
#	  self.widgetToolBar.InsertToolItem( pos, item )
#
##x        #noworky item.Enable( enabled )
##x	self.widgetToolBar.EnableTool( ti_count, enabled )
##x	tip = ti[ 'widget' ]
##x	if not enabled:
##x	  tip += ' (disabled)'
##x	item.SetShortHelp( tip )
##x	#item.Update()
#
#      ti_count += 1
#    #end for
#    self.widgetToolBar.Realize()

#		-- Update title
#		--
    #title = TITLE
    #if file_path is not None:
      #title += (': %s' % os.path.basename( file_path ))
    #self.SetTitle( title )
    self.UpdateTitle()

#		-- Determine axial plot types
#		--
    self.axialPlotTypes.clear()

    if len( data.GetDataSetNames( 'channel' ) ) > 0 and data.core.nax > 1:
      self.axialPlotTypes.add( 'channel' )

    if len( data.GetDataSetNames( 'detector' ) ) > 0 and data.core.ndetax > 1:
      self.axialPlotTypes.add( 'detector' )
      self.axialPlotTypes.add( 'pin' )

    if len( data.GetDataSetNames( 'pin' ) ) > 0 and data.core.nax > 1:
      self.axialPlotTypes.add( 'pin' )

    if len( data.GetDataSetNames( 'fixed_detector' ) ) > 0 and data.core.nfdetax > 1:
      self.axialPlotTypes.add( 'fixed_detector' )
    #if len( data.GetDataSetNames( 'vanadium' ) ) > 0 and data.core.nvanax > 1:
      #self.axialPlotTypes.add( 'vanadium' )

#		-- Initialize
#		--
    self.CloseAllWidgets()
    grid_sizer = self.grid.GetSizer()
    grid_sizer.SetRows( 1 )
    grid_sizer.SetCols( 1 )

#		-- Load Config
#		--
    if session is not None:
      self._LoadWidgetConfig( session )

#		-- Or determine default initial widgets
#		--
    elif widget_props is None:
#      self.CloseAllWidgets()
#      grid_sizer = self.grid.GetSizer()
#      grid_sizer.SetRows( 1 )
#      grid_sizer.SetCols( 1 )

      widget_list = []

      if data.core.nass > 1:
        widget_list.append( 'widget.core_view.Core2DView' )

#			-- Detector mode
      if len( data.GetDataSetNames( 'detector' ) ) > 0:
        widget_list.append( 'widget.detector_multi_view.Detector2DMultiView' )
        #widget_list.append( 'widget.detector_view.Detector2DView' )

      if len( data.GetDataSetNames( 'fixed_detector' ) ) > 0:
        if 'widget.detector_multi_view.Detector2DMultiView' not in widget_list:
          widget_list.append( 'widget.detector_multi_view.Detector2DMultiView' )
        #if 'widget.detector_view.Detector2DView' not in widget_list:
          #widget_list.append( 'widget.detector_view.Detector2DView' )

#			-- Pin mode
      if len( data.GetDataSetNames( 'pin' ) ) > 0:
        if data.core.nax > 1:
          widget_list.append( 'widget.core_axial_view.CoreAxial2DView' )
        widget_list.append( 'widget.assembly_view.Assembly2DView' )

#			-- Channel mode
#x      if len( data.GetDataSetNames( 'channel' ) ) > 0:
#x        if data.core.nass > 1:
#x          widget_list.append( 'widget.channel_view.Channel2DView' )
#x        widget_list.append( 'widget.channel_assembly_view.ChannelAssembly2DView' )
#x        if data.core.nax > 1:
#x          widget_list.append( 'widget.channel_axial_view.ChannelAxial2DView' )

#			-- Axial plot?
      if len( self.axialPlotTypes ) > 0 and data.core.nax > 1:
        widget_list.append( 'widget.axial_plot.AxialPlot' )

#			-- Time plot?
      if len( data.states ) > 1:
        widget_list.append( 'widget.time_plots.TimePlots' )

      if False:
        widget_list = [
            'widget.core_view.Core2DView',
            'widget.assembly_view.Assembly2DView',
            'widget.core_axial_view.CoreAxial2DView',
            'widget.detector_multi_view.Detector2DMultiView',
            'widget.axial_plot.AxialPlot',
            'widget.time_plots.TimePlots',
	    'widget.channel_view.Channel2DView',
	    'widget.channel_assembly_view.ChannelAssembly2DView',
	    'widget.channel_axial_view.ChannelAxial2DView',
            ]

      if self.config is None:
        if len( widget_list ) > 6:
          grid_sizer.SetCols( 4 )
          grid_sizer.SetRows( 2 )
        elif len( widget_list ) > 3:
          grid_sizer.SetCols( 3 )
          grid_sizer.SetRows( 2 )
        elif len( widget_list ) > 1:
          grid_sizer.SetCols( 2 )
          grid_sizer.SetRows( 1 )
      #end if config

#			-- Create widgets
#			--
      for w in widget_list:
        self.CreateWidget( w, False )
        if self.logger.isEnabledFor( logging.DEBUG ):
          self.logger.debug(
	      'widget added="%s", grid.size=%s',
	      w, str( self.grid.GetSize() )
	      )
      #end for

      fr_size = None if self.config is None else self.config.GetFrameSize()
      if fr_size is not None and fr_size[ 0 ] > 0 and fr_size[ 1 ] > 0:
	fr_pos = self.config.GetFramePosition()
	self.SetPosition( fr_pos )
        self.SetSize( fr_size )
      else:
        self._Refit( False )  # True

    elif widget_props == 'empty':
      pass

    elif 'classpath' in widget_props:
      wc = self.CreateWidget( widget_props[ 'classpath' ] )
      wc.LoadProps( widget_props )
#    else:
#      wc.Reparent( self.grid )
#      self.AddWidgetContainer( wc, True )
    #end if-elif-else session

#		-- Set bean ranges and values
#		--
    self.axialBean.SetRange( 1, data.core.nax )
    self.axialBean.axialLevel = self.state.axialValue[ 1 ]

    self.exposureBean.SetRange( 1, len( data.states ) )
    self.exposureBean.stateIndex = self.state.stateIndex

    ##self.GetStatusBar().SetStatusText( 'Data model loaded' )
  #end LoadDataModel


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._LoadWidgetConfig()		-
  #----------------------------------------------------------------------
  def _LoadWidgetConfig( self, widget_config, check_types = False ):
    """Updates based on a widget configuration.
Note this defines a new State as well as widgets in the grid.
@param  widget_config	WidgetConfig instance, cannot be None
@param  check_types	true to check widget dataset types
"""
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'entered' )
    #xxxxx recreate derived datasets

    self.state.LoadProps( widget_config.GetStateProps() )
    if check_types:
      data = self.state.GetDataModel()

    self.CloseAllWidgets()
    grid_sizer = self.grid.GetSizer()
    grid_sizer.SetRows( 1 )
    grid_sizer.SetCols( 1 )

    for props in widget_config.GetWidgetProps():
      if 'classpath' in props:
#			-- 3D widgets won't auto load
	if props[ 'classpath' ].find( '3D' ) < 0:
          con = self.CreateWidget( props[ 'classpath' ], False )
	  con.LoadProps( props )

	  #xxx we need a cheaper way to check for the types
	  if check_types:
	    must_remove = True
	    for t in con.widget.GetDataSetTypes():
	      if data.HasDataSetType( t ):
	        must_remove = False
	        addit = True
	    if must_remove:
	      con.OnClose( None )
	  #end if check_types
	#end if not 3D
      #end if classpath
    #end for props

    if self.state.scaleMode in self.scaleModeItems:
      self.scaleModeItems[ self.state.scaleMode ].Check()

    if self.state.weightsMode in self.weightsModeItems:
      self.weightsModeItems[ self.state.weightsMode ].Check()

    fr_pos = widget_config.GetFramePosition()
    fr_size = widget_config.GetFrameSize()
    if fr_size[ 0 ] > 0 and fr_size[ 1 ] > 0:
      self.SetPosition( fr_pos )
      self.SetSize( fr_size )

    self.dataSetMenu.Init()
  #end _LoadWidgetConfig


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnAxial()			-
  #----------------------------------------------------------------------
  def _OnAxial( self, ev ):
    """Handles events from the axial slider.  Called on the UI thread.
"""
    ev.Skip()
    #axial_value = self.state.dataModel.CreateAxialValue( core_ndx = ev.value )
    axial_value = \
        self.state.GetDataModel().CreateAxialValue( core_ndx = ev.value )
    reason = self.state.Change( self.eventLocks, axial_value = axial_value )
    if reason != STATE_CHANGE_noop:
      self.state.FireStateChange( reason )
      #self.grid.FireStateChange( reason )
  #end _OnAxial


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnCharHook()			-
  #----------------------------------------------------------------------
  def _OnCharHook( self, ev ):
    code = ev.GetKeyCode()
    if code == wx.WXK_DOWN:
      self.axialBean.Decrement()
    elif code == wx.WXK_LEFT:
      self.exposureBean.Decrement()
    elif code == wx.WXK_RIGHT:
      self.exposureBean.Increment()
    elif code == wx.WXK_UP:
      self.axialBean.Increment()
    else:
      ev.DoAllowNextEvent()
  #end _OnCharHook


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.OnCloseFrame()			-
  #----------------------------------------------------------------------
  def OnCloseFrame( self, ev ):
    if len( self.app.GetFrames() ) == 1:
#			-- Windows focus hack
      win = wx.Window_FindFocus()
      if win is not None:
        win.Disconnect( -1, -1, wx.wxEVT_KILL_FOCUS )

      self._OnQuit( None )

    else:
      frame = ev.GetEventObject()
      self.app.RemoveFrame( frame )
      frame.Bind( wx.EVT_CLOSE, None )
      frame.Close()
      if Config.CanDragNDrop():
        self._UpdateWindowMenus( remove_frame = frame )
  #end OnCloseFrame


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.OnCloseFrame_singleWindow()	-
  #----------------------------------------------------------------------
  def OnCloseFrame_singleWindow( self, ev ):
#	-- Windows focus hack
    win = wx.Window_FindFocus()
    if win is not None:
      win.Disconnect( -1, -1, wx.wxEVT_KILL_FOCUS )
#
    #self._OnQuit( None )
  #end OnCloseFrame_singleWindow


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnCloseWindow()			-
  #----------------------------------------------------------------------
#  def _OnCloseWindow( self, ev ):
#    ev.Skip()
#    for child in self.GetChildren():
#      if isinstance( child, wx.Frame ) and child.IsActive():
#	child.Close()
#	break
#    #end for
#  #end _OnCloseWindow


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnControlTool()			-
  #----------------------------------------------------------------------
  def _OnControlTool( self, ev ):
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'entered' )
    ev.Skip()

    tbar = ev.GetEventObject()
    if ev.GetId() == ID_REFIT_WINDOW:
      self._Refit( True )
  #end _OnControlTool


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnCopy()				-
  #----------------------------------------------------------------------
  def _OnCopy( self, ev ):
    ev.Skip()

    if not wx.TheClipboard.Open():
      wx.MessageDialog(
          self, 'Could not open the clipboard', 'Copy Data',
	  style = wx.ICON_WARNING | wx.OK
	  ).\
	  ShowWindowModal()

    else:
      try:
	wx.TheClipboard.SetData( wx.TextDataObject( "xxx" ) )

      except Exception, ex:
        wx.MessageDialog(
            self, 'Could not open the clipboard', 'Copy Data',
	    style = wx.ICON_WARNING | wx.OK
	    ).\
	    ShowWindowModal()

      finally:
	wx.TheClipboard.Close()
    #end if-else
  #end _OnCopy


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnExposure()			-
  #----------------------------------------------------------------------
  def _OnExposure( self, ev ):
    """Handles events from the exposure slider.  Called on the UI thread.
"""
    ev.Skip()
    reason = self.state.Change( self.eventLocks, state_index = ev.value )
    if reason != STATE_CHANGE_noop:
      self.state.FireStateChange( reason )
      #self.grid.FireStateChange( reason )
  #end _OnExposure


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnManageDataSets()		-
  #----------------------------------------------------------------------
#  def _OnManageDataSets( self, ev ):
#    ev.Skip()
#
#    msg = None
#    data_model = self.GetDataModel()
#
#    if data_model is None:
#      msg = 'No VERAOutput file has been read'
#
#    elif len( data_model.GetStates() ) == 0:
#      msg = 'No state points read from VERAOutput file'
#
#    if msg is not None:
#      wx.MessageDialog( self, msg, 'Manage Extra DataSets' ).ShowWindowModal()
#
#    else:
#      dialog = DataSetManagerDialog( self, data_model = data_model )
#      dialog.ShowModal()
#      data_model.ReadExtraDataSets()
#      dialog.Destroy()
#    #end if-else
#  #end _OnManageDataSets


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnGridResize()			-
  #----------------------------------------------------------------------
  def _OnGridResize( self, ev ):
    ev.Skip()

    grid_sizer = self.grid.GetSizer()
    cur_size = ( grid_sizer.GetRows(), grid_sizer.GetCols() )

    dialog = GridSizerDialog( None )
    dialog.ShowModal( cur_size )
    new_size = dialog.GetResult()
    if new_size is not None and new_size != cur_size:
      proceed = True
      cell_count = new_size[ 0 ] * new_size[ 1 ]
      widget_count = len( self.grid.GetChildren() )
      if widget_count > cell_count:
	message = \
	    'That would be too few grids for all your widgets.\n' + \
	    'Delete some widgets first.'
        wx.MessageDialog( self, message, 'Resize Grid' ).ShowWindowModal()
	proceed = False

      elif cell_count > 16:
	message = \
	    'You have defined more than 16 widget windows!\n' + \
	    'You must have a really big screen.  Are you sure?'
        choice = wx.MessageDialog(
	    self, message,
	    'Resize Grid',
	    style = wx.ICON_QUESTION | wx.YES_NO
	    ).\
	    ShowWindowModal()
	proceed = choice == wx.ID_YES
      #end if-else on widget_count

      if proceed:
        grid_sizer.SetRows( new_size[ 0 ] )
        grid_sizer.SetCols( new_size[ 1 ] )
	self._Refit( True )
    #end if different size
  #end _OnGridResize


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnLoadSession()			-
  #----------------------------------------------------------------------
  def _OnLoadSession( self, ev ):
    ev.Skip()

    path = None
    dialog = wx.FileDialog(
	self, 'Load Session', '', '',
	'VERAView session files (*.vview)|*.vview',
	wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR
        )
    if dialog.ShowModal() != wx.ID_CANCEL:
      path = dialog.GetPath()
      dialog.Destroy()

    if path is not None:
      try:
        config = WidgetConfig( path )
	self._LoadWidgetConfig( config, True )
      except Exception, ex:
        msg = 'Error loading session:' + os.linesep + str( ex )
        self.ShowMessageDialog( msg, 'Load Session' )
  #end _OnLoadSession


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnMinimizeWindow()		-
  #----------------------------------------------------------------------
  def _OnMinimizeWindow( self, ev ):
    ev.Skip()
    self.Iconize( True )
  #end _OnMinimizeWindow


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnNewWidget()			-
  #----------------------------------------------------------------------
  def _OnNewWidget( self, ev ):
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'entered' )
    ev.Skip()

    title = None
    menu = ev.GetEventObject()
    item = menu.FindItemById( ev.GetId() )
    if item is not None and item.GetLabel() in WIDGET_MAP:
      self.CreateWidget( WIDGET_MAP[ item.GetItemLabelText() ] )
  #end _OnNewWidget


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnNewWindow()			-
  #----------------------------------------------------------------------
  def _OnNewWindow( self, ev ):
    if ev:
      ev.Skip()
    self.CreateWindow()
  #end _OnNewWindow


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnOpenFile()			-
  #----------------------------------------------------------------------
  def _OnOpenFile( self, ev ):
    """
Must be called from the UI thread.
"""
    if ev is not None:
      ev.Skip()

    if self.state.GetDataModel() is not None:
      self._UpdateConfig()

    # 'HDF5 files (*.h5)|*.h5',
    # 'HDF5 files (*.h5,*.x)|*.h5;*.x',
    # 'HDF5 files (*.h5,*.x)|*.h5;*.x|Other files (*.vview)|*.vview',
    dialog = wx.FileDialog(
	self, 'Open File', '', '',
        'HDF5 files (*.h5)|*.h5|VERAView session files (*.vview)|*.vview',
	wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR
        )
    if dialog.ShowModal() != wx.ID_CANCEL:
      path = dialog.GetPath()
      dialog.Destroy()
      #self.OpenFile( path )

      path, session = self._ResolveFile( path )
      self.OpenFile( path, session )
  #end _OnOpenFile


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnOpenUserConfig()		-
  #----------------------------------------------------------------------
  def _OnOpenUserConfig( self, config_path ):
    """
Must be called from the UI thread.
"""
    pass
  #end _OnOpenUserConfig


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnSaveImageAllWidgets()		-
  #----------------------------------------------------------------------
  def _OnSaveImageAllWidgets( self, ev ):
    """
Must be called on the UI event thread.
"""
    self.SaveWidgetsImage()
  #end _OnSaveImageAllWidgets


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnSaveSession()			-
  #----------------------------------------------------------------------
  def _OnSaveSession( self, ev ):
    ev.Skip()

    dialog = wx.FileDialog(
        self, 'Save Session', '', '',
	'VERAView session files (*.vview)|*.vview',
	wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR
	)

    if dialog.ShowModal() != wx.ID_CANCEL:
      file_path = dialog.GetPath()
      dialog.Destroy()
      try:
        self.SaveSession( file_path )
      except Exception, ex:
        msg = 'Error saving session:' + os.linesep + str( ex )
        self.ShowMessageDialog( msg, 'Save Session' )
  #end _OnSaveSession


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnScaleMode()			-
  #----------------------------------------------------------------------
  def _OnScaleMode( self, ev ):
    ev.Skip()
    menu = ev.GetEventObject()
    item = menu.FindItemById( ev.GetId() )

    if item is not None:
      mode = SCALE_MODES.get( item.GetLabel(), 'all' )
      reason = self.state.Change( self.eventLocks, scale_mode = mode )
      self.state.FireStateChange( reason )
    #end if
  #end _OnScaleMode


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnSelectDataSet()		-
  #----------------------------------------------------------------------
#  def _OnSelectDataSet( self, ev ):
#    ev.Skip()
#    if self.dataSetMenu:
#      self.dataSetMenu._UpdateMenu( ev )
#      self.widgetToolBar.PopupMenu( self.dataSetMenu )
#  #end _OnSelectDataSet


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnTileWindows()			-
  #----------------------------------------------------------------------
  def _OnTileWindows( self, ev ):
    ev.Skip()

#		-- Determine number of tile rows
#		--
    #display_size = wx.DisplaySize()
    display_rect = wx.GetClientDisplayRect()
    display_left = display_rect.GetLeft()
    display_top = display_rect.GetTop()
    display_wd = display_rect.GetWidth()
    display_ht = display_rect.GetHeight()
#Not necessary
#    if 'wxMac' in wx.PlatformInfo:
#      display_ht -= 32
#      display_top += 32

    count = len( self.app.GetFrames() )
    frows = math.sqrt( count * display_ht / float( display_wd ) )
    rows100 = int( frows * 100.0 )
    rounder = rows100 % 100
    if rounder >= 50:
      rows100 += 100
    nrows = max( 1, rows100 / 100 )
    ncols = (count + nrows - 1) / nrows

#		-- Window size
#		--
    win_wd = int( display_wd / ncols )
    win_ht = int( display_ht / nrows )
    win_size = ( win_wd, win_ht )

    col = row = 0
    win_x = display_left
    win_y = display_top

    for frame_rec in self.app.GetFrames().values():
      fr = frame_rec.get( 'frame' )
      if fr:
        fr.SetPosition( ( win_x, win_y ) )
	fr.SetSize( win_size )
	fr.Iconize( False )
	fr.Raise()

	col += 1
	if col > ncols:
	  win_x = display_left
	  col = 0
	  row += 1
	  win_y += win_ht
	else:
	  win_x += win_wd
	#end if-else ncols exceeded
      #end if fr
    #end for
  #end _OnTileWindows


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnQuit()				-
  #----------------------------------------------------------------------
  def _OnQuit( self, ev ):
    data = self.state.GetDataModel()
    try:
      #if self.app.filepath is not None:
      if data is not None:
        self.SaveSession()
    except Exception, ex:
      msg = 'Error saving session:' + os.linesep + str( ex )
      # dialog flashes, not modal.
      #self.ShowMessageDialog( msg, 'Save Session' )
      if self.logger.isEnabledFor( logging.ERROR ):
        self.logger.error( msg )
      wx.MessageBox(
          msg, 'Save Configuration',
	  wx.ICON_WARNING | wx.OK_DEFAULT,
	  None
          )

    if data is not None:
      data.Close()
    #self.Close()
    wx.App.Get().ExitMainLoop()
  #end _OnQuit


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnQuit_0()			-
  #----------------------------------------------------------------------
  def _OnQuit_0( self, ev ):
    data = self.state.GetDataModel()

    ans = wx.MessageBox(
        'Save widget configuration?',
	'Save Configuration',
	wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL,
	self
        )
    if ans == wx.YES:
      widget_config = WidgetConfig()

      fr_size = self.GetSize()
      widget_config.SetFrameSize( fr_size.GetWidth(), fr_size.GetHeight() )
      widget_config.SetState( self.state )

      widget_list = []
      for wc in self.grid.GetChildren():
        if isinstance( wc, WidgetContainer ):
	  widget_list.append( wc.widget )

      widget_config.AddWidgets( *widget_list )
      widget_config.Write()

    if data is not None:
      data.Close()
    #self.Close()
    wx.App.Get().ExitMainLoop()
  #end _OnQuit_0


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnTimeDataSet()			-
  #----------------------------------------------------------------------
  def _OnTimeDataSet( self, ev ):
    ev.Skip()
    menu = ev.GetEventObject()
    item = menu.FindItemById( ev.GetId() )

    if item is not None:
      title = item.GetLabel()
      reason = self.state.Change( self.eventLocks, time_dataset = title )
      self.state.FireStateChange( reason )
      #self.grid.FireStateChange( reason )
    #end if
  #end _OnTimeDataSet


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnView3D()			-
  #----------------------------------------------------------------------
#  def _OnView3D( self, ev ):
#    #ev.Skip( False )
#
#    def check_and_show_volume_slicer( loaded, errors ):
#      if errors is not None and len( errors ) > 0:
#        msg = \
#	    'Error loading 3D envrionment:' + os.linesep + \
#	    os.linesep.join( errors )
#        wx.MessageBox(
#	    msg, 'View 3D Volume Slicer',
#	    wx.ICON_ERROR | wx.OK_DEFAULT
#	    )
#
#      elif loaded:
#        self._OnView3DImpl()
#    #end check_and_show
#
#    if State.FindDataModel( self.state ) is None:
#      wx.MessageBox(
#          'A VERAOutput file must be opened',
#	  'View 3D Volume Slicer',
#	  wx.OK_DEFAULT
#	  )
#    else:
#      Environment3D.LoadAndCall( check_and_show_volume_slicer )
#  #end _OnView3D


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnView3DImpl()			-
  #----------------------------------------------------------------------
#  def _OnView3DImpl( self ):
#    object_classpath = 'view3d.slicer_view_frame.Slicer3DFrame'
#    module_path, class_name = object_classpath.rsplit( '.', 1 )
#
#    error = None
#    module = None
#    cls = None
#
#    try:
#      module = __import__( module_path, fromlist = [ class_name ] )
#    except ImportError:
#      error = 'Error importing "%s"' % object_classpath
#
#    if error is None:
#      try:
#        cls = getattr( module, class_name )
#      except AttributeError:
#        error = 'Class "%s" not found in module "%s"' % \
#	    ( module_path, class_name )
#
#    if error is not None:
#      wx.MessageBox(
#	  error, 'View 3D Volume Slicer',
#	  wx.ICON_ERROR | wx.OK_DEFAULT
#	  )
#
#    else:
#      viz_frame = cls( self, -1, self.state )
#      #viz_frame.bind( wx.EVT_CLOSE, self._OnCloseChildFrame )
#      viz_frame.Show()
#  #end _OnView3DImpl


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnWeightsMode()			-
  #----------------------------------------------------------------------
  def _OnWeightsMode( self, ev ):
    ev.Skip()
    menu = ev.GetEventObject()
    item = menu.FindItemById( ev.GetId() )

    if item is not None:
      mode = WEIGHTS_MODES.get( item.GetLabel(), 'on' )
      reason = self.state.Change( self.eventLocks, weights_mode = mode )
      self.state.FireStateChange( reason )
    #end if
  #end _OnWeightsMode


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnWidgetTool()			-
  #----------------------------------------------------------------------
  def _OnWidgetTool( self, ev ):
    if self.logger.isEnabledFor( logging.DEBUG ):
      self.logger.debug( 'entered' )
    ev.Skip()

    tbar = ev.GetEventObject()
    item = tbar.FindById( ev.GetId() )
    if item is not None and item.GetShortHelp() in WIDGET_MAP:
      self.CreateWidget( WIDGET_MAP[ item.GetShortHelp() ] )
  #end _OnWidgetTool


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OnWindowMenuItem()		-
  #----------------------------------------------------------------------
  def _OnWindowMenuItem( self, ev ):
    ev.Skip()
    menu = ev.GetEventObject()
    item = menu.FindItemById( ev.GetId() )

    if item is not None:
      title = item.GetLabel()
      frame_rec = self.app.FindFrameByTitle( title )
      if frame_rec:
        frame = frame_rec.get( 'frame' )
	if frame:
	  frame.Iconize( False )
	  frame.Raise()
      #end if frame_rec
    #end if item

#      for child in self.GetChildren():
#        if isinstance( child, WidgetContainer ) and child.GetTitle() == title:
#	  child.Iconize( False )
#          child.Raise()
#	  break
#      #end for
    #end if
  #end _OnWindowMenuItem


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.OpenFile()			-
  #----------------------------------------------------------------------
  def OpenFile( self, file_path, session = None ):
    """
Must be called from the UI thread.
"""
    self.CloseAllWidgets()

    dialog = wx.ProgressDialog(
        'Open File',
	'Reading file "%s"' % file_path
	)
    dialog.Show()

    wxlibdr.startWorker(
	self._OpenFileEnd,
	self._OpenFileBegin,
	wargs = [ dialog, file_path, session ]
	#wkwargs = { 'config': config, 'session': session }
        )
  #end OpenFile


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OpenFileBegin()			-
  #----------------------------------------------------------------------
  def _OpenFileBegin( self, dialog, file_path, session = None ):
    """
"""
    dialog.Pulse()
    status = \
      {
      'dialog': dialog,
      'file_path': file_path,
      'session': session
      }

    try:
      data_model = DataModel( file_path )
      messages = data_model.Check()

      status[ 'data_model' ] = data_model
      status[ 'messages' ] = messages

    except Exception, ex:
      status[ 'messages' ] = \
        [ 'Error opening data file:' + os.linesep + str( ex ) ]

    return  status
  #end _OpenFileBegin


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._OpenFileEnd()			-
  #----------------------------------------------------------------------
  def _OpenFileEnd( self, result ):
    """
"""
    status = result.get()
    if status is not None:
      if 'dialog' in status:
	dlg = status[ 'dialog' ]
	#dlg.Lower()
	dlg.Hide()
	dlg.Destroy()

      if 'messages' in status and len( status[ 'messages' ] ) > 0:
	msg = \
	    'Data file cannot be processed:\n' + \
	    '\n  '.join( status[ 'messages' ] )
	self.ShowMessageDialog( msg, 'Open File' )
	#dlg = wx.MessageDialog( self, msg, 'Open File' )
	#wx.CallAfter( dlg, ShowModal )

      elif 'data_model' in status and 'file_path' in status:
	self.state.Load( status[ 'data_model' ] )
	wx.CallAfter(
	    self.LoadDataModel,
	    status[ 'file_path' ],
	    status.get( 'session' )
	    )
    #end if
  #end _OpenFileEnd


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._Refit()				-
  #----------------------------------------------------------------------
  def _Refit( self, apply_widget_ratio = False, *additionals ):
    display_size = wx.DisplaySize()
    frame_size = self.GetSize()
    if frame_size[ 0 ] > display_size[ 0 ] or \
        frame_size[ 1 ] > display_size[ 1 ]:
      if not self.IsMaximized():
        self.Maximize()
        frame_size = self.GetSize()

    #grid_size = self.grid.GetSize()
    #if grid_size[ 0 ] > new_size[ 0 ] or grid_size[ 1 ] > new_size[ 1 ] :
    self.grid.FitWidgets( apply_widget_ratio )
    self.Fit()

    if additionals:
      additionals[ 0 ]( *additionals[ 1 : ] )
  #end _Refit


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._ResolveFile()			-
  #----------------------------------------------------------------------
  def _ResolveFile( self, path ):
    """Checks the path for a session (.vview) file.
@param  path		file path
@return			datafile_path, session
"""
    session = None
    if path.endswith( '.vview' ):
      session = WidgetConfig( path )
      path = session.GetFilePath()

    return  path, session
  #end _ResolveFile


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._ResolveTitle()			-
  #----------------------------------------------------------------------
  def _ResolveTitle( self, title ):
    """
@deprecated from multi-window days.
"""
    result = title
#    last = 0
#    for item in self.windowMenu.GetMenuItems():
#      text = item.GetLabel()
#      colon_ndx = text.find( ':' )
#      if colon_ndx > 0:
#        number = int( text[ : colon_ndx ] )
#	last = max( number, last )
#      #end if
#    #end for
#
#    result = '%d: %s' % ( last + 1, title )
    return  result
  #end _ResolveTitle


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.SaveSession()			-
  #----------------------------------------------------------------------
  def SaveSession( self, file_path = None ):
    """
@param  file_path	path of VERAView (.vview) file or None to save the
			user session file
"""
    #xxxxx list derived datasets to be re-created
    config = WidgetConfig()

    fr_pos = self.GetPosition()
    fr_size = self.GetSize()
    config.SetFramePosition( fr_pos[ 0 ], fr_pos[ 1 ] )
    config.SetFrameSize( fr_size[ 0 ], fr_size[ 1 ] )
    #config.SetFrameSize( fr_size.GetWidth(), fr_size.GetHeight() )
    config.SetState( self.state )

    widget_list = []
    for wc in self.grid.GetChildren():
      if isinstance( wc, WidgetContainer ):
        widget_list.append( wc.widget )

    config.AddWidgets( *widget_list )

    data = self.state.GetDataModel()
    if data is not None:
      hfp = data.GetH5File()
      if hfp is not None:
        config.SetFilePath( hfp.filename )

    config.Write( file_path )
  #end SaveSession


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.SaveWidgetsImage()		-
  #----------------------------------------------------------------------
  def SaveWidgetsImage( self, file_path = None ):
    """
Must be called on the UI event thread.
"""
    if len( self.grid.GetChildren() ) == 0:
      self.ShowMessageDialog( 'No widgets to save', 'Save Image' )

    else:
      if file_path is None:
        dialog = wx.FileDialog(
	    self, 'Save Widgets Image', '', '',
	    'PNG files (*.png)|*.png',
	    wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR
	    )
        if dialog.ShowModal() != wx.ID_CANCEL:
	  file_path = dialog.GetPath()
      #end if

      if file_path is not None:
        try:
	  widgets = []
	  for wc in self.grid.GetChildren():
	    if isinstance( wc, WidgetContainer ):
	      widgets.append( wc.widget )

	  montager = WidgetImageMontager(
	      result_path = file_path,
	      widgets = widgets,
	      cols = self.grid.GetSizer().GetCols()
	      )
	  montager.Run( 'Save Widgets Image' )

	except Exception, ex:
	  msg = 'Error saving image:' + os.linesep + str( ex )
          self.ShowMessageDialog( msg, 'Save Image' )
      #end if
    #end else we have child widget containers
  #end SaveWidgetsImage


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.SetConfig()			-
  #----------------------------------------------------------------------
  def SetConfig( self, value ):
    """Accessor for the config property.
@param  value		WidgetConfig object
"""
    self.config = value
  #end SetConfig


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.SetFrameId()			-
  #----------------------------------------------------------------------
  def SetFrameId( self, value ):
    """Accessor for the frameId property.
@param  value		1-based ordinal number
"""
    self.frameId = value
  #end SetFrameId


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.ShowMessageDialog()		-
  #----------------------------------------------------------------------
  def ShowMessageDialog( self, message, title ):
    """Must be called on the UI thread.
"""
    wx.MessageDialog( self, message, title ).ShowWindowModal()
  #end ShowMessageDialog


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._UpdateConfig()			-
  #----------------------------------------------------------------------
  def _UpdateConfig( self ):
    """Updates with current frame properties.
"""
    fr_pos = self.GetPosition()
    fr_size = self.GetSize()
    if self.config is None:
      self.config = WidgetConfig()

    self.config.SetFramePosition( fr_pos[ 0 ], fr_pos[ 1 ] )
    self.config.SetFrameSize( fr_size[ 0 ], fr_size[ 1 ] )
  #end _UpdateConfig


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame.UpdateTitle()			-
  #----------------------------------------------------------------------
  def UpdateTitle( self ):
    """
"""
    title = '%d: %s' % ( self.frameId, TITLE )
    if self.filepath:
      title += ':: %s' % os.path.basename( self.filepath )
    self.SetTitle( title )
  #end UpdateTitle


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._UpdateToolBar()			-
  #----------------------------------------------------------------------
  def _UpdateToolBar( self, tbar, enable_all = False ):
    """
"""
    data = self.state.GetDataModel()

    for i in xrange( len( TOOLBAR_ITEMS ) ):
      item = tbar.FindById( i + 1 )
      if item is not None:
        self.Unbind( wx.EVT_TOOL, item )
        #self.Unbind( wx.EVT_TOOL, self._OnWidgetTool, id = i + 1 )
    tbar.ClearTools()
    #print >> sys.stderr, '\n[_UpdateToolBar] tbar.toolsCount=', tbar.GetToolsCount()

    if data is not None:
      ds_names = data.GetDataSetNames()

      ti_count = 1
      for ti in TOOLBAR_ITEMS:
        widget_icon = ti.get( 'icon' )
        if widget_icon is None:
          tbar.AddSeparator()

        else:
          ds_type = ti[ 'type' ]
	  ds_names = data.GetDataSetNames( ds_type )

          enabled = \
	      enable_all or ds_type == '' or \
	      (ds_names is not None and len( ds_names ) > 0)
	  if enabled and 'func' in ti:
	    enabled = ti[ 'func' ]( data )

          widget_icon = ti.get( 'icon' if enabled else 'iconDisabled' )
          widget_im = wx.Image(
              os.path.join( Config.GetResDir(), widget_icon ),
	      wx.BITMAP_TYPE_PNG
	      )

          tip = ti[ 'widget' ]
          if not enabled:
            tip += ' (disabled)'

          tb_item = tbar.AddTool(
              ti_count, widget_im.ConvertToBitmap(),
	      shortHelpString = tip
	      )
	  tb_item.Enable( enabled )
          self.Bind( wx.EVT_TOOL, self._OnWidgetTool, tb_item )
          #self.Bind( wx.EVT_TOOL, self._OnWidgetTool, id = ti_count )
	  #print >> sys.stderr, '[_UpdateToolBar] ti_count=%d, widget=%s' % ( ti_count, ti[ 'widget' ] )
        #end if-else separator

        ti_count += 1
      #end for ti
    #end if data

    tbar.Realize()
  #end _UpdateToolBar


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrame._UpdateWindowMenus()		-
  #----------------------------------------------------------------------
  def _UpdateWindowMenus( self, **kwargs ):
    """Assume this will only be called if the 'Window' menubar item has
been created.
"""
    titles = []
    frames = []
    for frame_rec in self.app.GetFrames().values():
      frame = frame_rec.get( 'frame' )
      if frame is not None:
	frames.append( frame )
        titles.append( frame.GetTitle() )
    #end for frame_rec

#		-- Process menu for each frame
#		--
    for frame in frames:
#			-- Find items to remove
#			--
      removes = []
      for i in xrange( frame.windowMenu.GetMenuItemCount() ):
        item = frame.windowMenu.FindItemByPosition( i )
	if item:
	  label = item.GetItemLabelText()
	  if label and label != 'Tile Windows':
	    removes.append( item )
      #end for i
#			-- Remove items
#			--
      for item in removes:
        frame.windowMenu.DestroyItem( item )

#			-- Add new items
#			--
      for title in titles:
        item = wx.MenuItem( frame.windowMenu, wx.ID_ANY, title )
	frame.Bind( wx.EVT_MENU, frame._OnWindowMenuItem, item )
	frame.windowMenu.AppendItem( item )
	#frame.windowMenu.UpdateUI()
      #end for title
    #end for frame
  #end _UpdateWindowMenus

#end VeraViewFrame


#------------------------------------------------------------------------
#	CLASS:		VeraViewFrameDropTarget				-
#------------------------------------------------------------------------
class VeraViewFrameDropTarget( wx.TextDropTarget ):
  """Processes widget drags."""


#		-- Object Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrameDropTarget.__init__()		-
  #----------------------------------------------------------------------
  def __init__( self, frame ):
    super( VeraViewFrameDropTarget, self ).__init__()

    self.frame = frame
  #end __init__


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewFrameDropTarget.OnDropText()		-
  #----------------------------------------------------------------------
  def OnDropText( self, x, y, data ):
    result = False
    #print >> sys.stderr, '[VeraViewFrameDropTarget] ', data, '\n[end]'
    if data:
      widget_props = WidgetConfig.Decode( data )
      if 'classpath' in widget_props:
        wc = self.frame.CreateWidget( widget_props[ 'classpath' ] )
	wc.LoadProps( widget_props )
	result = True
    #end if

    return  result
  #end OnDropText

#end VeraViewFrameDropTarget


#------------------------------------------------------------------------
#	CLASS:		VeraViewGrid					-
#------------------------------------------------------------------------
class VeraViewGrid( wx.Panel ):
  """Grid panel.
"""


#		-- Object Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid.__init__()				-
  #----------------------------------------------------------------------
  def __init__( self, *args, **kwargs ):
    super( VeraViewGrid, self ).__init__( *args, **kwargs )

    self.listener = None
    self.logger = logging.getLogger( 'root' )
    self._InitUI()
  #end __init__


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid.CalcWidgetSize()			-
  #----------------------------------------------------------------------
  def CalcWidgetSize( self, apply_widget_ratio = False ):
    sizer = self.GetSizer()
    size = self.GetClientSize()

#		-- Works b/c there's no border or margin
    item_wd = int( math.floor( size[ 0 ] / sizer.GetCols() ) )
    item_ht = int( math.floor( size[ 1 ] / sizer.GetRows() ) )

    if apply_widget_ratio:
      temp_wd = int( math.floor( item_ht * WIDGET_PREF_RATIO ) )

#			-- Constrained by width
      if temp_wd > item_wd:
        item_ht = int( math.floor( item_wd / WIDGET_PREF_RATIO ) )
      else:
        item_wd = temp_wd
    #end if apply_widget_ratio

    return  ( item_wd, item_ht )
  #end CalcWidgetSize


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid.FireStateChange()			-
  #----------------------------------------------------------------------
#  def FireStateChange( self, reason ):
#    if reason != STATE_CHANGE_noop:
#      for child in self.GetChildren():
#        if isinstance( child, WidgetContainer ):
#	  try:
#	    child.HandleStateChange( reason )
#          except Exception, ex:
#	    print >> sys.stderr, '[VeraViewGrid.FireStateChanged]', str( ex )
#      #end for
#
#      self.listener.HandleStateChange( reason )
#    #end if
#  #end FireStateChange


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid.FitWidgets()			-
  #----------------------------------------------------------------------
  def FitWidgets( self, apply_widget_ratio = False ):
    self._ResizeWidgets( self.CalcWidgetSize( apply_widget_ratio ) )
  #end FitWidgets


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid._FreezeWidgets()			-
  #----------------------------------------------------------------------
  def _FreezeWidgets( self, freeze_flag = True ):
    """
@param  freeze_flag	True to freeze, False to Thaw
"""
    if freeze_flag:
      for item in self.GetChildren():
	if not item.IsFrozen():
          item.Freeze()
    else:
      for item in self.GetChildren():
	if item.IsFrozen():
          item.Thaw()
  #end _FreezeWidgets


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid.GetListener()			-
  #----------------------------------------------------------------------
  def GetListener( self ):
    return  self.listener
  #end GetListener


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid._InitUI()				-
  #----------------------------------------------------------------------
  def _InitUI( self ):
    cols = 1
    rows = 1

    sizer = wx.GridSizer( cols, rows, 0, 0 )
    self.SetSizer( sizer )

#		-- Size this
#		--
#    display_size = wx.DisplaySize()
#    ht = display_size[ 1 ] - 64
#    wd = int( ht * WIDGET_PREF_RATIO )
#    self.SetSize( ( wd, ht ) )

#    display_size = wx.DisplaySize()
#    ht = display_size[ 1 ] - 64
#    if ht < WIDGET_PREF_SIZE[ 1 ]:
#      grid_size = ( int( ht * WIDGET_PREF_RATIO ), ht )
#    else:
#      grid_size = WIDGET_PREF_SIZE
#    #self.SetMinSize( grid_size )
#    self.SetSize( grid_size )
  #end _InitUI


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid._ResizeWidgets()			-
  #----------------------------------------------------------------------
  def _ResizeWidgets( self, new_size ):
    self._FreezeWidgets()
    grid = self.GetSizer()
    items = []
    for item in self.GetChildren():
      if isinstance( item, WidgetContainer ):
        items.append( item )
        grid.Detach( item )

    for item in self.GetChildren():
      item.SetMinSize( new_size )
      item.SetSize( new_size )
#      grid.Add( item, 0, wx.ALIGN_CENTER | wx.SHAPED, 0 )
      grid.Add( item, 0, wx.ALIGN_CENTER | wx.EXPAND, 0 )

    grid.Layout()
    self.Fit()

    self._FreezeWidgets( False )
  #end _ResizeWidgets


  #----------------------------------------------------------------------
  #	METHOD:		VeraViewGrid.SetListener()			-
  #----------------------------------------------------------------------
  def SetListener( self, l ):
    self.listener = l
  #end SetListener

#end VeraViewGrid


#------------------------------------------------------------------------
#	NAME:		main()						-
#------------------------------------------------------------------------
if __name__ == '__main__':
  VeraViewApp.main()
