#!/usr/bin/env python
# encoding: utf-8

import os
from bob.db.base import utils
from .models import *

from .driver import Interface
INFO = Interface()
SQLITE_FILE = INFO.files()[0]

import bob.db.base

class Database(bob.db.base.SQLiteDatabase):
  """ Class representing the database

  See parent class `:py:class:bob.db.base.SQLiteDatabase` for more details ...

  Attributes
  ----------
  original_directory: str
    Path where the database is stored
  original_extension: str
    Extension of files in the database 
  annotation_directory: str
    Path where the annotations are stored
  annotation_extension: str
    Extension of anootation files

  """

  def __init__(self, 
               original_directory=None, 
               original_extension=None,
               annotation_directory=None,
               annotation_extension=None,
               protocol='all'):
    """ Init function

    Parameters
    ----------
    original_directory: str
      Path where the database is stored
    original_extension: str
      Extension of files in the database 
    annotation_directory: str
      Path where the annotations are stored
    annotation_extension: str
      Extension of annotation files

    """
    super(Database, self).__init__(SQLITE_FILE, ImageFile, original_directory, original_extension)
    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension
    self.protocol = protocol

  def groups(self, protocol=None):     
    """Returns the names of all registered groups
    
    Parameters
    ----------
    protocol: str
      ignored, since the group are the same across protocols.
    
    """   
    return ProtocolPurpose.group_choices


  def purposes(self):
    """Returns purposes 
    
    """
    return ProtocolPurpose.purpose_choices


  def objects(self, purposes=None, groups=None):
    """Returns a set of Samples for the specific query by the user.
    
    Note that a sample may contain up to 3 modalities (color, infrared and depth)
    The protocol specifies which modality(ies) should be loaded

    Parameters
    ----------
    purposes: str or tuple of str
      The purposes required to be retrieved ('real', 'attack') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. 
    groups: str or tuple of str
      One of the groups ('dev', 'eval', 'train') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    Returns
    -------
    lst:
      A list of samples which have the given properties.
    
    """
    from sqlalchemy import and_
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())

    #print("In low-level DB (objects): groups = {}".format(groups))
    #print("In low-level DB (objects): purposes = {}".format(purposes))


    # Now query the database
    #q = self.query(Sample).join((ProtocolPurpose, Sample.protocolPurposes)).join(Protocol).filter(Sample.group.in_(groups))
    
    #q = self.query(Sample).filter(Sample.group.in_(groups))

    #print("# of retrieved objects = {}".format(len(list(q))))
    #

    ##q = q.filter(Sample.group.in_(groups))
    ##print("FILTERING GROUPS : # of retrieved objects = {}".format(len(list(q))))
    #
    ## get the right purpose 
    #if 'attack' in purposes:
    #  print("Filtering: attacks -> {}".format(len(list(q))))
    #  q = q.filter(Sample.attack_type > 0)
    #if 'real' in purposes:
    #  print("Filtering: real examples -> {}".format(len(list(q))))
    #  q = q.filter(Sample.attack_type == 0)
    #if 'unknown' in purposes:
    #  print("Filtering: real examples -> {}".format(len(list(q))))
    #  q = q.filter(Sample.attack_type == 0)
    
    q = self.query(Sample)\
                       .join((ProtocolPurpose, Sample.protocolPurposes))\
                       .filter(ProtocolPurpose.group.in_(groups))\
                       .filter(ProtocolPurpose.purpose.in_(purposes))\


    retval = list(set(q))
    #print("number of objects = {}".format(len(retval)))
    #print("================== DONE ======================")
    return list(set(retval))  # To remove duplicates
