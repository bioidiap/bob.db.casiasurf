#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
from .models import *

from bob.db.base.driver import Interface as BaseInterface

import bob.core
logger = bob.core.log.setup('bob.db.casiasurf')


def add_files(session, imagesdir, extension='.jpg'):
  """ Add face images files.

  This function adds the face image files to the database.

  Parameters
  ----------
  session:
    The session to the SQLite database 
  imagesdir : :py:obj:str
    The directory where to find the images 
  extension: :py:obj:str
    The extension of the image file.

  """

  for root, dirs, files in os.walk(imagesdir, topdown=False):
    for name in files:
      image_filename = os.path.join(root, name)

      # just to make sure that nothing weird will be added
      if os.path.splitext(image_filename)[1] == extension:

        # get all the info, base on the file path
        image_info = image_filename.replace(imagesdir, '')
        infos = image_info.split('/')
       
        attack_type = None 
        purpose = None
        
        if infos[0] == 'Training': 
          
          group = 'train'
          
          if infos[1] == 'fake_part': purpose = 'attack'
          if infos[1] == 'real_part': purpose = 'real'
          
          if purpose == 'attack':
            attack_type = infos[3].split('_')[0]
          
          stream = infos[4]
          if stream == 'color': modality = 'rgb'
          if stream == 'ir': modality = 'nir'
          if stream == 'depth': modality = 'depth'
      
          print("group = {}, purpose = {}, attack_type = {}, mod = {}".format(group, purpose, attack_type, modality))

        elif infos[0] == 'Val':

          group = 'dev'
          temp = infos[2].split('-')
          stream = temp[1].split('.')[0]
          if stream == 'color': modality = 'rgb'
          if stream == 'ir': modality = 'nir'
          if stream == 'depth': modality = 'depth'
          print("group = {}, purpose = {}, attack_type = {}, mod = {}".format(group, purpose, attack_type, modality))

        stem = image_info[0:-len(extension)]
        logger.info("Adding file {}".format(stem))
        o = File(path=stem, group=group, modality=modality, purpose=purpose, attack_type=attack_type)
        session.add(o)

def create_tables(args):
    """Creates all necessary tables (only to be used at the first time)"""

    from bob.db.base.utils import create_engine_try_nolock
    engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
    Base.metadata.create_all(engine)


# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  from bob.db.base.utils import session_try_nolock

  print(args)
  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print(('unlinking %s...' % dbfile))
    if os.path.exists(dbfile):
      os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  bob.core.log.set_verbosity_level(logger, args.verbose)

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=False)
  add_files(s, args.imagesdir)
  s.commit()
  s.close()

  return 0


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', default=False,
                      help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', default=0,
                      help="Do SQL operations in a verbose way")
  parser.add_argument('imagesdir', action='store', metavar='DIR',
                      help="The path to the extracted images of the FARGO database")

  parser.set_defaults(func=create)  # action
