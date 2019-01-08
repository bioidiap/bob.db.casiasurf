#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

import bob.core

logger = bob.core.log.setup('bob.db.casiasurf')
Base = declarative_base()

class File(Base, bob.db.base.File):
  """Generic file container
  
  Class that defines an image file of the CASIA-SURF database.

  Attributes
  ----------
  modality: str
    The modality from which this file was recorded
  path: str
    The path on the disk where this file is stored.
  
  """

  __tablename__ = 'file'

  # key id for files
  id = Column(Integer, primary_key=True)

  # path of this file in the database
  path = Column(String(100), unique=True)
  
  # group
  group_choices = ('train', 'dev', 'eval')
  group = Column(Enum(*group_choices))

  # modality
  modality_choices = ('rgb', 'nir', 'depth')
  modality = Column(Enum(*modality_choices))

  # purpose
  purpose_choices = ('real', 'attack')
  purpose = Column(Enum(*purpose_choices))
        
  # attack type
  attack_type = Column(String(10))


  def __init__(self, path, group, modality, purpose=None, attack_type=None):
    """ Init function

    Parameters
    ----------
    path: str
      The path on the disk where this file is stored.
    group: str
      The group this file belongs to ('train', 'dev', 'eval')
    purpose: str
      The purpose this file belongs to ('real', 'attack')
    modality: str
      The modality from which this file was recorded
    attack_type: int
      The type of attack (1 to 6) 
    
    """
    bob.db.base.File.__init__(self, path=path)
    self.group = group
    self.modality = modality
    self.purpose = purpose
    self.attack_type = attack_type

  def __repr__(self):
    return "File('%s')" % self.path


  def make_path(self, directory=None, extension=None):
    """Wraps the current path so that a complete path is formed

    Parameters
    ----------
    directory
      An optional directory name that will be prefixed to the returned result.
    extension
      An optional extension that will be suffixed to the returned filename. 
      extension normally includes the leading ``.`` character 

    Returns
    -------
    str:
      the newly generated file path.
    
    """
    if not directory:
      directory = ''
    if not extension:
      extension = ''
    return str(os.path.join(directory, self.path + extension))
