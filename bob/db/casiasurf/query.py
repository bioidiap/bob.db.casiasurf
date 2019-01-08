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
               protocol='default'):
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
      Extension of anootation files

    """
    super(Database, self).__init__(SQLITE_FILE, File, original_directory, original_extension)
    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension
    self.protocol = protocol

  @property
  def modalities(self):
    return ['rgb', 'nir', 'depth']

  def groups(self, protocol=None):     
    """Returns the names of all registered groups
    
    Parameters
    ----------
    protocol: str
      ignored, since the group are the same across protocols.
    
    """   
    return File.group_choices


  def purposes(self):
    """Returns purposes 
    
    """
    return File.purpose_choices


  def objects(self, purposes=None, groups=None, modality=None):
    """Returns a set of Files for the specific query by the user.

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
    modality: str or tuple
      One of the three modalities 'rgb', 'nir' and 'depth'

    Returns
    -------
    lst:
      A list of files which have the given properties.
    
    """
    from sqlalchemy import and_
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    modality = self.check_parameters_for_validity(modality, "modality", self.modalities)

    # Now query the database
    retval = []
    q = self.query(File)
    q = q.filter(File.group.in_(groups))
    q = q.filter(File.modality.in_(modality))
    q = q.filter(File.purpose.in_(purposes))
    retval += list(q)

    return list(set(retval))  # To remove duplicates
