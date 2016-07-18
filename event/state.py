#!/usr/bin/env python
# $Id$
#------------------------------------------------------------------------
#	NAME:		state.py					-
#	HISTORY:							-
#		2016-07-18	leerw@ornl.gov				-
#	  Added {Get,Set}DataSetByType().
#		2016-07-07	leerw@ornl.gov				-
#	  Renaming "vanadium" to "fixed_detector".
#		2016-06-30	leerw@ornl.gov				-
#	  Added {Load,Save}Props().
#		2016-06-27	leerw@ornl.gov				-
#	  Moved EVENT_ID_NAMES here for better encapsulation.
#		2016-05-25	leerw@ornl.gov				-
#	  Special "vanadium" dataset type.
#		2016-04-25	leerw@ornl.gov				-
#	  Added aux{Channel,Pin}ColRows attributes and associated
#	  STATE_CHANGE_ mask bits.
#		2016-04-23	leerw@ornl.gov				-
#	  Calling DataModel.GetDefaultScalarDataSet() in Load().
#		2016-04-16	leerw@ornl.gov				-
#	  Added scaleMode.
#		2015-12-08	leerw@ornl.gov				-
#	  Managing events and changes on the State object.
#		2015-06-15	leerw@ornl.gov				-
#	  Refactoring.  Added State.CreateUpdateArgs().
#		2015-05-25	leerw@ornl.gov				-
#		2015-05-23	leerw@ornl.gov				-
#	  Added channelColRow property and event.
#		2015-05-21	leerw@ornl.gov				-
#	  Added channelDataSet property and event.
#		2015-05-18	leerw@ornl.gov				-
#	  Wiring together detectorIndex and assemblyIndex state changes.
#		2015-05-11	leerw@ornl.gov				-
#	  Changed axialLevel to axialValue.
#		2015-04-27	leerw@ornl.gov				-
#	  Added STATE_CHANGE_detector{DataSet,Index}.
#		2015-04-22	leerw@ornl.gov				-
#	  Changed assemblyIndex to be a ( index, col, row ) tuple.
#		2015-04-11	leerw@ornl.gov				-
#	  Added {pin,scalar}DataSet as a state event.
#		2015-04-04	leerw@ornl.gov				-
#	  Reversing pinRowCol to pinColRow.
#		2015-02-18	leerw@ornl.gov				-
#	  Looping in ResolveLocks().
#		2015-02-11	leerw@ornl.gov				-
#	  Removed scale and added pinRowCol.
#		2014-12-30	leerw@ornl.gov				-
#	  New data model.
#		2014-12-08	leerw@ornl.gov				-
#		2014-11-15	leerw@ornl.gov				-
#------------------------------------------------------------------------
import h5py, os, sys, traceback
import numpy as np
import pdb

from data.datamodel import *


# These are in the order of being added
STATE_CHANGE_noop = 0
STATE_CHANGE_init = 0x1 << 0
STATE_CHANGE_dataModel = 0x1 << 1
STATE_CHANGE_assemblyIndex = 0x1 << 2
#STATE_CHANGE_axialLevel = 0x1 << 3
STATE_CHANGE_axialValue = 0x1 << 3
STATE_CHANGE_stateIndex = 0x1 << 4
STATE_CHANGE_pinColRow = 0x1 << 5
STATE_CHANGE_pinDataSet = 0x1 << 6
STATE_CHANGE_scalarDataSet = 0x1 << 7
STATE_CHANGE_detectorDataSet = 0x1 << 8
STATE_CHANGE_detectorIndex = 0x1 << 9
STATE_CHANGE_channelDataSet = 0x1 << 10
STATE_CHANGE_channelColRow = 0x1 << 11
STATE_CHANGE_timeDataSet = 0x1 << 12
STATE_CHANGE_scaleMode = 0x1 << 13
STATE_CHANGE_auxChannelColRows = 0x1 << 14
STATE_CHANGE_auxPinColRows = 0x1 << 15
STATE_CHANGE_fixedDetectorDataSet = 0x1 << 16
#STATE_CHANGE_ALL = 0x1fff


LOCKABLE_STATES = \
  (
  STATE_CHANGE_assemblyIndex,
  STATE_CHANGE_auxChannelColRows,
  STATE_CHANGE_auxPinColRows,
  STATE_CHANGE_axialValue,
  STATE_CHANGE_channelColRow,
  STATE_CHANGE_channelDataSet,
  STATE_CHANGE_detectorDataSet,
  STATE_CHANGE_detectorIndex,
  STATE_CHANGE_pinColRow,
  STATE_CHANGE_pinDataSet,
  STATE_CHANGE_scalarDataSet,
  STATE_CHANGE_scaleMode,
  STATE_CHANGE_stateIndex,
  STATE_CHANGE_timeDataSet,
  STATE_CHANGE_fixedDetectorDataSet
  )


EVENT_ID_NAMES = \
  [
    ( STATE_CHANGE_assemblyIndex, 'Assembly Index' ),
    ( STATE_CHANGE_axialValue, 'Axial Value' ),
    ( STATE_CHANGE_channelColRow, 'Channel Column and Row' ),
    ( STATE_CHANGE_auxChannelColRows, '2ndary Channel Column and Row' ),
    ( STATE_CHANGE_channelDataSet, 'Channel Dataset' ),
    ( STATE_CHANGE_detectorDataSet, 'Detector Dataset' ),
    ( STATE_CHANGE_detectorIndex, 'Detector Index' ),
    ( STATE_CHANGE_pinColRow, 'Pin Column and Row' ),
    ( STATE_CHANGE_auxPinColRows, '2ndary Pin Column and Row' ),
    ( STATE_CHANGE_pinDataSet, 'Pin Dataset' ),
    ( STATE_CHANGE_scalarDataSet, 'Scalar Dataset' ),
    ( STATE_CHANGE_stateIndex, 'State Point Index' ),
    ( STATE_CHANGE_fixedDetectorDataSet, 'Fixed Detector Dataset' )
  ]


#------------------------------------------------------------------------
#	CLASS:		State						-
#------------------------------------------------------------------------
class State( object ):
  """Event state object.  State attributes currently in use are as follows.
All indices are 0-based.

+----------------------+---------------------------+---------------------------+
| Attribute/Prop       | Description               | Parameter                 |
+===================+==============================+===========================+
| assemblyIndex        | ( int index, int column,  | assembly_index            |
|                      |   int row )               |                           |
+----------------------+---------------------------+---------------------------+
| auxChannelColRows    | list of ( col, row        | aux_channel_colrows       |
|                      |   assy_ndx, assy_col      |                           |
|                      |   assy_row )              |                           |
+----------------------+---------------------------+---------------------------+
| auxPinColRows        | list of ( col, row        | aux_pin_colrows           |
|                      |   assy_ndx, assy_col      |                           |
|                      |   assy_row )              |                           |
+----------------------+---------------------------+---------------------------+
| axialValue           | ( value(cm), core-index,  | axial_value               |
|                      |   detector-index,         |                           |
|                      |   fixed-det-index )       |                           |
+----------------------+---------------------------+---------------------------+
| channelColRow        | ( int column, int row )   | channel_colrow            |
+----------------------+---------------------------+---------------------------+
| channelDataSet       | str name                  | channel_dataset           |
+----------------------+---------------------------+---------------------------+
| dataModel            | DataModel object          | data_model                |
+----------------------+---------------------------+---------------------------+
| detectorDataSet      | str name                  | detector_dataset          |
+----------------------+---------------------------+---------------------------+
| detectorIndex        | ( int index, int column   | detector_index            |
|                      |   int row )               |                           |
+----------------------+---------------------------+---------------------------+
| fixedDetectorDataSet | str name                  | fixed_detector_dataset    |
+----------------------+---------------------------+---------------------------+
| listeners            | list of objects to notify on change events            |
+----------------------+---------------------------+---------------------------+
| pinColRow            | ( int column, int row )   | pin_colrow                |
+----------------------+---------------------------+---------------------------+
| pinDataSet           | str name                  | pin_dataset               |
+----------------------+---------------------------+---------------------------+
| scalarDataSet        | str name                  | scalar_dataset            |
+----------------------+---------------------------+---------------------------+
| scaleMode            | 'all' or 'state'          | scale_mode                |
+----------------------+---------------------------+---------------------------+
| stateIndex           | int statept-index         | state_index               |
+----------------------+---------------------------+---------------------------+
| timeDataSet          | state dataset name used   | time_dataset              |
|                      | for "time"                |                           |
+----------------------+---------------------------+---------------------------+

We need to change to a single "coordinate" specifying the assembly/detector
index and col,row, pin/channel col,row, and axial value.  Big change!!
"""

#		-- Class Attributes
#		--

  DS_ATTR_BY_TYPE = \
    {
    'channel':
      { 'attr': 'channelDataSet', 'mask': STATE_CHANGE_channelDataSet,
        'param': 'channel_dataset' },
    'detector':
      { 'attr': 'detectorDataSet', 'mask': STATE_CHANGE_detectorDataSet,
        'param': 'detector_dataset' },
    'fixed_detector':
      { 'attr': 'fixedDetectorDataSet',
        'mask': STATE_CHANGE_fixedDetectorDataSet,
        'param': 'fixed_detector_dataset' },
    'pin':
      { 'attr': 'pinDataSet', 'mask': STATE_CHANGE_pinDataSet,
        'param': 'pin_dataset' },
    'scalar':
      { 'attr': 'scalarDataSet', 'mask': STATE_CHANGE_scalarDataSet,
        'param': 'scalar_dataset' },
    'time':
      { 'attr': 'timeDataSet', 'mask': STATE_CHANGE_timeDataSet,
        'param': 'time_dataset' }
    }

#		-- Object Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		__init__()					-
  #----------------------------------------------------------------------
  def __init__( self, *args, **kwargs ):
    self.assemblyIndex = ( -1, -1, -1 )
    #self.axialLevel = -1
    self.auxChannelColRows = []
    self.auxPinColRows = []
    self.axialValue = DataModel.CreateEmptyAxialValue()
    #self.axialValue = ( 0.0, -1, -1, -1 )
    self.channelColRow = ( -1, -1 )
    self.channelDataSet = 'channel_liquid_temps [C]'
    self.dataModel = None
    self.detectorDataSet = 'detector_response'
    self.detectorIndex = ( -1, -1, -1 )
    self.fixedDetectorDataSet = 'fixed_detector_response'
    self.listeners = []
    self.pinColRow = ( -1, -1 )
    self.pinDataSet = 'pin_powers'
    self.scalarDataSet = 'keff'
    self.scaleMode = 'all'
    self.stateIndex = -1
    self.timeDataSet = 'state'

    if 'assembly_index' in kwargs:
      self.assemblyIndex = kwargs[ 'assembly_index' ]
    if 'aux_channel_colrows' in kwargs:
      self.auxChannelColRows = kwargs[ 'aux_channel_colrows' ]
    if 'aux_pin_colrows' in kwargs:
      self.auxPinColRows = kwargs[ 'aux_pin_colrows' ]
    if 'axial_value' in kwargs:
      self.axialValue = kwargs[ 'axial_value' ]
    if 'channel_colrow' in kwargs:
      self.channelColRow = kwargs[ 'channel_colrow' ]
    if 'channel_dataset' in kwargs:
      self.channelDataSet = kwargs[ 'channel_dataset' ]
    if 'data_model' in kwargs:
      self.dataModel = kwargs[ 'data_model' ]
    if 'detector_dataset' in kwargs:
      self.detectorDataSet = kwargs[ 'detector_dataset' ]
    if 'detector_index' in kwargs:
      self.detectorIndex = kwargs[ 'detector_index' ]
    if 'fixed_detector_dataset' in kwargs:
      self.fixedDetectorDataSet = kwargs[ 'fixed_detector_dataset' ]
    if 'pin_colrow' in kwargs:
      self.pinColRow = kwargs[ 'pin_colrow' ]
    if 'pin_dataset' in kwargs:
      self.pinDataSet = kwargs[ 'pin_dataset' ]
    if 'scalar_dataset' in kwargs:
      self.scalarDataSet = kwargs[ 'scalar_dataset' ]
    if 'scale_mode' in kwargs:
      self.scaleMode = kwargs[ 'scale_mode' ]
    if 'state_index' in kwargs:
      self.stateIndex = kwargs[ 'state_index' ]
    if 'time_dataset' in kwargs:
      self.timeDataSet = kwargs[ 'time_dataset' ]
  #end __init__


  #----------------------------------------------------------------------
  #	METHOD:		__str__()					-
  #----------------------------------------------------------------------
  def __str__( self ):
    """This needs to be updated.  Perhaps dump the JSON sans dataModel.
"""
    result = \
        'assembly=%s,axial=%s,datasets=(%s,%s),pin=%d,%d,state=%d' % ( \
	    str( self.assemblyIndex ), str( self.axialValue ), \
	    self.pinDataSet, self.scalarDataSet, \
	    self.pinColRow[ 1 ], self.pinColRow[ 0 ], self.stateIndex \
	    )
    return  result
  #end __str__


  #----------------------------------------------------------------------
  #	METHOD:		AddListener()					-
  #----------------------------------------------------------------------
  def AddListener( self, listener ):
    """Adds the listener if not already added.  Listeners must implement
a HandleStateChange( self, reason ) method.
"""
    if listener not in self.listeners:
      self.listeners.append( listener )
  #end AddListener


  #----------------------------------------------------------------------
  #	METHOD:		Change()					-
  #----------------------------------------------------------------------
  def Change( self, locks, **kwargs ):
    """Applies the property changes specified in kwargs that are allowed
by locks.
@param  locks		dictionary of True/False values for each of the
			STATE_CHANGE_xxx indexes
@param  kwargs		name, value pairs with which to update this

Keys passed and the corresponding state bit are:
  assembly_index	STATE_CHANGE_assemblyIndex
  aux_channel_colrows	STATE_CHANGE_auxChannelColRows
  aux_pin_colrows	STATE_CHANGE_auxPinColRows
  axial_value		STATE_CHANGE_axialValue
  data_model		STATE_CHANGE_dataModel
  channel_colrow	STATE_CHANGE_channelColRow
  channel_dataset	STATE_CHANGE_channelDataSet
  detector_dataset	STATE_CHANGE_detectorDataSet
  detector_index	STATE_CHANGE_detectorIndex
  fixed_detector_dataset	STATE_CHANGE_fixedDetectorDataSet
  pin_colrow		STATE_CHANGE_pinColRow
  pin_dataset		STATE_CHANGE_pinDataSet
  scalar_dataset	STATE_CHANGE_scalarDataSet
  scale_mode		STATE_CHANGE_scaleMode
  state_index		STATE_CHANGE_stateIndex
  time_dataset		STATE_CHANGE_timeDataSet
@return			change reason mask
"""
    reason = STATE_CHANGE_noop

    if 'assembly_index' in kwargs and locks[ STATE_CHANGE_assemblyIndex ]:
      self.assemblyIndex = kwargs[ 'assembly_index' ]
      reason |= STATE_CHANGE_assemblyIndex

    if 'aux_channel_colrows' in kwargs and locks[ STATE_CHANGE_auxChannelColRows ]:
      self.auxChannelColRows = kwargs[ 'aux_channel_colrows' ]
      reason |= STATE_CHANGE_auxChannelColRows

    if 'aux_pin_colrows' in kwargs and locks[ STATE_CHANGE_auxPinColRows ]:
      self.auxPinColRows = kwargs[ 'aux_pin_colrows' ]
      reason |= STATE_CHANGE_auxPinColRows

    if 'axial_value' in kwargs and locks[ STATE_CHANGE_axialValue ]:
      self.axialValue = kwargs[ 'axial_value' ]
      reason |= STATE_CHANGE_axialValue
#    if 'axial_level' in kwargs and locks[ STATE_CHANGE_axialLevel ]:
#      self.axialLevel = kwargs[ 'axial_level' ]
#      reason |= STATE_CHANGE_axialLevel

    if 'channel_colrow' in kwargs and locks[ STATE_CHANGE_channelColRow ]:
      self.channelColRow = kwargs[ 'channel_colrow' ]
      reason |= STATE_CHANGE_channelColRow

    if 'channel_dataset' in kwargs and locks[ STATE_CHANGE_channelDataSet ]:
      self.channelDataSet = kwargs[ 'channel_dataset' ]
      reason |= STATE_CHANGE_channelDataSet

    if 'data_model' in kwargs:
      self.dataModel = kwargs[ 'data_model' ]
      reason |= STATE_CHANGE_dataModel

    if 'detector_dataset' in kwargs and locks[ STATE_CHANGE_detectorDataSet ]:
      self.detectorDataSet = kwargs[ 'detector_dataset' ]
      reason |= STATE_CHANGE_detectorDataSet

    if 'detector_index' in kwargs and locks[ STATE_CHANGE_detectorIndex ]:
      self.detectorIndex = kwargs[ 'detector_index' ]
      reason |= STATE_CHANGE_detectorIndex

    if 'fixed_detector_dataset' in kwargs and \
        locks[ STATE_CHANGE_fixedDetectorDataSet ]:
      self.fixedDetectorDataSet = kwargs[ 'fixed_detector_dataset' ]
      reason |= STATE_CHANGE_fixedDetectorDataSet

    if 'pin_colrow' in kwargs and locks[ STATE_CHANGE_pinColRow ]:
      self.pinColRow = kwargs[ 'pin_colrow' ]
      reason |= STATE_CHANGE_pinColRow

    if 'pin_dataset' in kwargs and locks[ STATE_CHANGE_pinDataSet ]:
      self.pinDataSet = kwargs[ 'pin_dataset' ]
      reason |= STATE_CHANGE_pinDataSet

    if 'scalar_dataset' in kwargs and locks[ STATE_CHANGE_scalarDataSet ]:
      self.scalarDataSet = kwargs[ 'scalar_dataset' ]
      reason |= STATE_CHANGE_scalarDataSet

    if 'scale_mode' in kwargs and locks[ STATE_CHANGE_scaleMode ]:
      self.scaleMode = kwargs[ 'scale_mode' ]
      reason |= STATE_CHANGE_scaleMode

    if 'state_index' in kwargs and locks[ STATE_CHANGE_stateIndex ]:
      self.stateIndex = kwargs[ 'state_index' ]
      reason |= STATE_CHANGE_stateIndex

    if 'time_dataset' in kwargs and locks[ STATE_CHANGE_timeDataSet ]:
      if self.timeDataSet != kwargs[ 'time_dataset' ]:
        self.timeDataSet = kwargs[ 'time_dataset' ]
        reason |= STATE_CHANGE_timeDataSet

#		-- Wire assembly_index and detector_index together
#		--
    if (reason & STATE_CHANGE_assemblyIndex) > 0:
      if (reason & STATE_CHANGE_detectorIndex) == 0 and \
          self.dataModel.core.detectorMap is not None:
	col = self.assemblyIndex[ 1 ]
	row = self.assemblyIndex[ 2 ]
	det_ndx = self.dataModel.core.detectorMap[ row, col ] - 1
	reason |= STATE_CHANGE_detectorIndex
	self.detectorIndex = ( det_ndx, col, row )

    elif (reason & STATE_CHANGE_detectorIndex) > 0:
      if (reason & STATE_CHANGE_assemblyIndex) == 0:
          #self.dataModel.core.coreMap is not None:
	col = self.detectorIndex[ 1 ]
	row = self.detectorIndex[ 2 ]
	assy_ndx = self.dataModel.core.coreMap[ row, col ] - 1
	reason |= STATE_CHANGE_assemblyIndex
	self.assemblyIndex = ( assy_ndx, col, row )
    #end if

    return  reason
  #end Change


  #----------------------------------------------------------------------
  #	METHOD:		CreateUpdateArgs()				-
  #----------------------------------------------------------------------
  def CreateUpdateArgs( self, reason ):
    """
@return			dict with updated values based on reason
"""
    update_args = {}
    if (reason & STATE_CHANGE_assemblyIndex) > 0:
      update_args[ 'assembly_index' ] = self.assemblyIndex
#      if hasattr( self, 'assemblyIndex' ) and \
#          self.state.assemblyIndex != self.assemblyIndex:

    if (reason & STATE_CHANGE_auxChannelColRows) > 0:
      update_args[ 'aux_channel_colrows' ] = self.auxChannelColRows

    if (reason & STATE_CHANGE_auxPinColRows) > 0:
      update_args[ 'aux_pin_colrows' ] = self.auxPinColRows

    if (reason & STATE_CHANGE_axialValue) > 0:
      update_args[ 'axial_value' ] = self.axialValue

    if (reason & STATE_CHANGE_channelColRow) > 0:
      update_args[ 'channel_colrow' ] = self.channelColRow

    if (reason & STATE_CHANGE_channelDataSet) > 0:
      update_args[ 'channel_dataset' ] = self.channelDataSet

    if (reason & STATE_CHANGE_dataModel) > 0:
      update_args[ 'data_model' ] = self.dataModel

    if (reason & STATE_CHANGE_detectorDataSet) > 0:
      update_args[ 'detector_dataset' ] = self.detectorDataSet

    if (reason & STATE_CHANGE_detectorIndex) > 0:
      update_args[ 'detector_index' ] = self.detectorIndex

    if (reason & STATE_CHANGE_fixedDetectorDataSet) > 0:
      update_args[ 'fixed_detector_dataset' ] = self.fixedDetectorDataSet

    if (reason & STATE_CHANGE_pinColRow) > 0:
      update_args[ 'pin_colrow' ] = self.pinColRow

    if (reason & STATE_CHANGE_pinDataSet) > 0:
      update_args[ 'pin_dataset' ] = self.pinDataSet

    if (reason & STATE_CHANGE_scalarDataSet) > 0:
      update_args[ 'scalar_dataset' ] = self.scalarDataSet

    if (reason & STATE_CHANGE_scaleMode) > 0:
      update_args[ 'scale_mode' ] = self.scaleMode

    if (reason & STATE_CHANGE_stateIndex) > 0:
      update_args[ 'state_index' ] = self.stateIndex

    if (reason & STATE_CHANGE_timeDataSet) > 0:
      update_args[ 'time_dataset' ] = self.timeDataSet

    return  update_args
  #end CreateUpdateArgs


  #----------------------------------------------------------------------
  #	METHOD:		FireStateChange()				-
  #----------------------------------------------------------------------
  def FireStateChange( self, reason ):
    """Notifies all listeners of the change if not noop.
@param  reason		reason mask
"""
    if reason != STATE_CHANGE_noop:
      for listener in self.listeners:
	try:
          listener.HandleStateChange( reason )
          #listener.HandleStateChange( reason, self )
	except Exception, ex:
	  print >> sys.stderr, '[State.FireStateChange] ' + str( ex )
      #end for listeners
    #end if not noop
  #end FireStateChange


  #----------------------------------------------------------------------
  #	METHOD:		GetDataModel()					-
  #----------------------------------------------------------------------
  def GetDataModel( self ):
    """Accessor for the dataModel property.
@return			DataModel object
"""
    return  self.dataModel
  #end GetDataModel


  #----------------------------------------------------------------------
  #	METHOD:		GetDataSetByType()				-
  #----------------------------------------------------------------------
  def GetDataSetByType( self, ds_type ):
    """Returns the current dataset for the type.
@param  ds_type		one of the categories/types defined in DataModel
@return			current dataset or None
"""
    result = None
    attr_rec = State.DS_ATTR_BY_TYPE.get( ds_type )
    if attr_rec and hasattr( self, attr_rec[ 'attr' ] ):
      result = getattr( self, attr_rec[ 'attr' ] )
    return  result
  #end GetDataSetByType


  #----------------------------------------------------------------------
  #	METHOD:		Load()						-
  #----------------------------------------------------------------------
  def Load( self, data_model = None ):
    """
@param  data_model	if None, use the current dataModel
"""
    undefined_ax = DataModel.CreateEmptyAxialValue()
    #undefined_ax = ( 0.0, -1, -1 )
    undefined2 = ( -1, -1 )
    undefined3 = ( -1, -1, -1 )
    self.dataModel = data_model
    self.scaleMode = 'all'

    if data_model is not None:
      self.assemblyIndex = data_model.NormalizeAssemblyIndex( undefined3 )
      self.axialValue = data_model.NormalizeAxialValue( undefined_ax )
      self.channelDataSet = data_model.GetFirstDataSet( 'channel' )
      self.channelColRow = data_model.NormalizePinColRow( undefined2 )
      self.detectorDataSet = data_model.GetFirstDataSet( 'detector' )
      self.detectorIndex = data_model.NormalizeDetectorIndex( undefined3 )
      self.fixedDetectorDataSet = data_model.GetFirstDataSet( 'fixed_detector' )
      self.pinColRow = data_model.NormalizePinColRow( undefined2 )
      self.pinDataSet = 'pin_powers' \
	  if 'pin_powers' in data_model.GetDataSetNames( 'pin' ) else \
	  data_model.GetFirstDataSet( 'pin' )
      #self.scalarDataSet = data_model.GetFirstDataSet( 'scalar' )
      self.scalarDataSet = data_model.GetDefaultScalarDataSet()
      self.stateIndex = data_model.NormalizeStateIndex( -1 )
      self.timeDataSet = 'exposure' \
          if 'exposure' in data_model.GetDataSetNames( 'time' ) else \
	  'state'
      #self.timeDataSet = data_model.ResolveTimeDataSetName()

    else:
      self.assemblyIndex = undefined3
      self.axialValue = undefined_ax
      self.channelColRow = undefined2
      self.channelDataSet = None
      self.detectorDataSet = None
      self.detectorIndex = undefined3
      self.fixedDetectorDataSet = None
      self.pinColRow = undefined2
      self.pinDataSet = None
      self.scalarDataSet = None
      self.stateIndex = -1
      self.timeDataSet = 'state'

    self.auxChannelColRows = []
    self.auxPinColRows = []
  #end Load


  #----------------------------------------------------------------------
  #	METHOD:		LoadProps()					-
  #----------------------------------------------------------------------
  def LoadProps( self, props_dict ):
    """Deserializes.
@param  props_dict	dict containing property values
"""
    for k in (
        'assemblyIndex', 'auxChannelColRows', 'auxPinColRows', 'axialValue', 
        'channelColRow', 'channelDataSet',
        'detectorDataSet', 'detectorIndex', 'fixedDetectorDataSet',
        'pinColRow', 'pinDataSet', 
        'scalarDataSet', 'scaleMode', 
        'stateIndex', 'timeDataSet',
        ):
      if k in props_dict:
        setattr( self, k, props_dict[ k ] )
  #end LoadProps


  #----------------------------------------------------------------------
  #	METHOD:		RemoveListener()				-
  #----------------------------------------------------------------------
  def RemoveListener( self, listener ):
    """Removes the listener.
"""
    if listener in self.listeners:
      self.listeners.remove( listener )
  #end RemoveListener


  #----------------------------------------------------------------------
  #	METHOD:		ResolveLocks()					-
  #----------------------------------------------------------------------
  def ResolveLocks( self, reason, locks ):
    """
@return		resolved reason
"""
    if reason is None:
      reason = STATE_CHANGE_noop

    else:
      for mask in LOCKABLE_STATES:
        if not locks[ mask ]:
	  reason &= ~mask
      #end for
    #end if-else

    return  reason
  #end ResolveLocks


  #----------------------------------------------------------------------
  #	METHOD:		SaveProps()					-
  #----------------------------------------------------------------------
  def SaveProps( self, props_dict ):
    """Serializes.
@param  props_dict	dict to which to write property values
"""
    for k in (
        'assemblyIndex', 'auxChannelColRows', 'auxPinColRows', 'axialValue', 
        'channelColRow', 'channelDataSet',
        'detectorDataSet', 'detectorIndex', 'fixedDetectorDataSet',
        'pinColRow', 'pinDataSet', 
        'scalarDataSet', 'scaleMode', 
        'stateIndex', 'timeDataSet',
        ):
      props_dict[ k ] = getattr( self, k )
  #end SaveProps


  #----------------------------------------------------------------------
  #	METHOD:		SetDataSetByType()				-
  #----------------------------------------------------------------------
  def SetDataSetByType( self, *ds_type_name_pairs ):
    """Returns the current dataset for the type.
@param  ds_type_name_pairs  category/type, name pairs to assign
@return			reason mask
"""
    mask = STATE_CHANGE_noop
    if ds_type_name_pairs:
      for i in range( 0, len( ds_type_name_pairs ) - 1, 2 ):
        ds_type = ds_type_name_pairs[ i ]
        ds_name = ds_type_name_pairs[ i + 1 ]
        attr_rec = State.DS_ATTR_BY_TYPE.get( ds_type )
        if attr_rec and 'mask' in attr_rec and \
	    hasattr( self, attr_rec[ 'attr' ] ):
	  setattr( self, attr_rec[ 'attr' ], ds_name )
	  mask |= attr_rec[ 'mask' ]
    #end if ds_type_name_pairs

    return  mask
  #end SetDataSetByType


#		-- Static Methods
#		--


  #----------------------------------------------------------------------
  #	METHOD:		CreateLocks()					-
  #----------------------------------------------------------------------
  @staticmethod
  def CreateLocks():
    """
@return		dict with all True for
		STATE_CHANGE_assemblyIndex,
		STATE_CHANGE_auxChannelColRows,
		STATE_CHANGE_auxPinColRows,
		STATE_CHANGE_axialValue,
		STATE_CHANGE_channelColRow,
		STATE_CHANGE_channelDataSet,
		STATE_CHANGE_detectorDataSet,
		STATE_CHANGE_detectorIndex,
		STATE_CHANGE_fixedDetectorDataSet,
		STATE_CHANGE_pinColRow,
		STATE_CHANGE_pinDataSet,
		STATE_CHANGE_scalarDataSet,
		STATE_CHANGE_scaleMode,
		STATE_CHANGE_stateIndex,
		STATE_CHANGE_timeDataSet
"""
    locks = {}
    for mask in LOCKABLE_STATES:
      locks[ mask ] = True
    return  locks
  #end CreateLocks


  #----------------------------------------------------------------------
  #	METHOD:		FindDataModel()					-
  #----------------------------------------------------------------------
  @staticmethod
  def FindDataModel( state ):
    data_model = None
    if state is not None and state.dataModel is not None:
      data_model = state.dataModel

    return  data_model
  #end FindDataModel
#end State
