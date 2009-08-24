#!/usr/bin/python

from distutils.command.build import build
from distutils.core import Command, setup
import os
import os.path
import shutil
import subprocess
import tempfile

data_files = [('/usr/local/share/man/man1/', ['doc/turnin.1', 'doc/project.1'])]

def check_executable_in_path(executable, message):
    """ Checks that executable is installed in the system's PATH and returns
    it's location.
    
    """
    if os.environ.has_key('PATH'):
        for directory in os.environ['PATH'].split(':'):
            if os.path.exists(os.path.join(directory, executable)):
                return os.path.join(directory, executable)
    else:
        for directory in ['/usr/bin', '/usr/local/bin']:
            if os.path.exists(os.path.join(directory, executable)):
                return os.path.join(directory, executable)
    print message
    return False

class build_infopage(Command):

    description = 'Generate the info document.'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """ Call makeinfo on the Texinfo document. """
        makeinfo = check_executable_in_path('makeinfo',
            "Please install the makeinfo executable to generate the info document")
        if makeinfo:
            cargs = [makeinfo, '-o', 'doc/turnin-ng.info', 'doc/turnin-ng.texi']
            retcode = subprocess.call(cargs)
            if retcode < 0:
                raise subprocess.CalledProcessError(retcode, ' '.join(cargs))
            data_files.append(('/usr/local/share/info/',
                ['doc/turnin-ng.info']))

build.sub_commands.append(('build_infopage', None))

class build_pdf(Command):

    description = 'Generate the pdf document.'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """ Call texi2pdf on the Texinfo document. """
        texi2pdf = check_executable_in_path('texi2pdf',
            "Please install texi2pdf to generate the PDF documentation")
        if texi2pdf:
            tempdir = tempfile.mkdtemp()
            shutil.copy(os.path.join('doc', 'turnin-ng.texi'), tempdir)
            shutil.copy(os.path.join('doc', 'gpl-2.0.texi'), tempdir)
            doc = os.path.join(os.getcwd(), 'doc')
            os.chdir(tempdir)
            cargs = [texi2pdf, 'turnin-ng.texi']
            # We need to call texi2pdf twice.
            for i in range(2):
                retcode = subprocess.call(cargs)
                if retcode < 0:
                    raise subprocess.CalledProcessError(retcode, ' '.join(cargs))
            else:
                shutil.copy('turnin-ng.pdf', doc)
                shutil.rmtree(tempdir, ignore_errors=True)
                # This is required so that the install command can find the
                # build directory. Without it, it searches for it in the
                # non-existent tempdir.
                os.chdir(os.path.join(doc, os.pardir))
                data_files.append(('/usr/local/share/doc/',
                    ['doc/turnin-ng.pdf']))
                

build.sub_commands.append(('build_pdf', None))


setup(name='turnin-ng',
      version='1.0~beta2',
      description='Turn in your assignments with turnin',
      author='Ryan Kavanagh',
      author_email='ryanakca@kubuntu.org',
      license='GNU General Public License version 2, or (at your option) ' +\
              'any later version',
      scripts=['src/bin/project', 'src/bin/turnin'],
      packages=['turninng'],
      package_dir={'turninng':'src/turninng'},
      data_files=data_files,
      cmdclass={'build_infopage': build_infopage, 'build_pdf':build_pdf}
)
