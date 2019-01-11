#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base
from bob.db.base.sqlalchemy_migration import Enum, relationship

import bob.core

logger = bob.core.log.setup('bob.db.casiasurf')

Base = declarative_base()

protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('imagefile_id',  Integer, ForeignKey('imagefile.id')))


class Sample(Base):
  """ A sample describe an example for this database.
      
      A sample consists in a single frame.
      Each sample may contain up to 3 modalities: RGB, NIR and depth.

  Attributes
  ----------
  id: str
    The id for the sample
  
  """
  
  __tablename__ = 'sample'
  id = Column(String(100), primary_key=True)
  group_choices = ('train', 'validation', 'test')
  group = Column(Enum(*group_choices))
  attack_type = Column(Integer)

  def __init__(self, id, group, attack_type=0):
    """ Init function
    
    Parameters
    ----------
    sample_id: str
      The id for the sample
    group: str
      The group this client belongs to (either 'train', 'validation' or 'test')
    attack_type: int
      The type of attack. Note that 0 corresponds to a real attempt.
    """
    self.id = id
    self.group = group
    self.attack_type = attack_type

  def load(self, modality='all'):
    pass
   
  def is_attack(self):
    return self.attack_type != 0


class ImageFile(Base, bob.db.base.File):
  """Generic file container
  
  Class that defines an image file of the CASIA-SURF database.

  Attributes
  ----------
  sample_id: str
    The id of the sample associated to this file
  modality: str
    The modality from which this file was recorded
  path: str
    The path on the disk where this file is stored.
  """
  
  __tablename__ = 'imagefile'

  # key id for files
  id = Column(Integer, primary_key=True)

  # client id of this file
  sample_id = Column(String(100), ForeignKey('sample.id'))  
  sample = relationship(Sample, backref=backref('image_file', order_by=id))
  
  # path of this file in the database
  path = Column(String(100), unique=True)
  
  # modality
  modality_choices = ('rgb', 'nir', 'depth')
  modality = Column(Enum(*modality_choices))


  def __init__(self, sample_id, path, modality):
    """ Init function

    Parameters
    ----------
    sample_id: str
      The id of the sample associated to this file
    path: str
      The path on the disk where this file is stored.
    modality: str
      The modality from which this file was recorded
    
    """
    bob.db.base.File.__init__(self, path=path)
    self.sample_id = sample_id
    self.path = path
    self.modality = modality

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


class Protocol(Base):
  """CASIA-SURF protocols
 
  The class representing the protocols.

  For now, the protocols are simply used to retrieve different modalities.
  Namely, the default protocol will retrieve all modalities for each sample,
  and there also are protocols that retrieve a single modality (rgb, nir, depth)

  Attributes
  ----------
  name:
    The name of the protocol
  """

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)
  name = Column(String(20), unique=True)

  def __init__(self, name):
    """ Init function

    Parameters
    ----------
    name:
      The name of the protocol
    
    """
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name,)


class ProtocolPurpose(Base):
  """CASIA-SURF protocol purposes
  
  This class represent the protocol purposes, and 
  more importantly, contains the set of files
  associated with each group and each purpose
  for each protocol.

  Attributes
  ----------
  protocol_id: str
    The associated protocol
  group: str
    The group in the associated protocol ('train', 'validation' or 'test')
  purpose: str
    The purpose of the group in this protocol ('real', 'attack' or 'unknown')
  
  """

  __tablename__ = 'protocolPurpose'

  id = Column(Integer, primary_key=True)
  
  protocol_id = Column(Integer, ForeignKey('protocol.id'))
  group_choices = ('train', 'validation', 'test')
  group = Column(Enum(*group_choices))
  purpose_choices = ('real', 'attack', 'unknown')
  purpose = Column(Enum(*purpose_choices))

  # protocol: a protocol have 1 to many purpose
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  
  # files: many to many relationship
  files = relationship("ImageFile", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))

  def __init__(self, protocol_id, group, purpose):
    """ Init function

    Parameters
    ----------
    protocol_id: str
      The associated protocol
    group: str
      The group in the associated protocol ('world', 'dev' or 'eval')
    purpose: str
      The purpose of the group in this protocol ('train', 'enroll' or 'probe')
   
    """
    self.protocol_id = protocol_id
    self.group = group
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.group, self.purpose)
