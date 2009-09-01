#!/usr/bin/python

from distutils.command.build import build
from distutils.command.install import install
from distutils.core import Command, setup
import distutils.sysconfig
import os
import os.path
import re
import shutil
import subprocess
import sys
import tempfile

# Get the install prefix if one is specified from the command line
for i, arg in enumerate(sys.argv):
    prefix_regex = re.compile('(?P<prefix>--prefix)?[\=\s]?(?P<path>[\w:\\][\\\w\s/]*)')
    if prefix_regex.match(arg):
        if prefix_regex.match(arg).group('prefix') and not prefix_regex.match(arg).group('path'):
            # We got --prefix with a space instead of an equal. The next arg will have our path.
            prefix = os.path.expandvars(prefix_regex.match(sys.argv[i+1]).group('path'))
        elif prefix_regex.match(arg).group('path'):
            prefix = os.path.expandvars(prefix_regex.match(arg).group('path'))

data_files = [(os.path.join(prefix,'share/man/man1/'),
                    ['doc/turnin.1', 'doc/turnincfg.1'])]

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

class build_htmldocs(Command):

    description = 'Generate the HTML documentation.'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """ Call texi2html on the Texinfo document. """
        texi2html = check_executable_in_path('texi2html',
            "Please install the texi2html executable to generate the HTML " +
            "documentation")
        if texi2html:
            cargs = [texi2html, '--init-file=doc/turnin-ng.texi.init', 'doc/turnin-ng.texi']
            retcode = subprocess.call(cargs)
            if retcode < 0:
                raise subprocess.CalledProcessError(retcode, ' '.join(cargs))
            os.rename('turnin-ng.html', 'doc/turnin-ng.html')
            data_files.append((os.path.join(prefix, 'share/doc/turnin-ng/'),
                ['doc/turnin-ng.html']))

build.sub_commands.append(('build_htmldocs', None))

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
            data_files.append((os.path.join(prefix, 'share/info/'),
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
            success = True
            cargs = [texi2pdf, 'turnin-ng.texi']
            # We need to call texi2pdf twice.
            for i in range(1):
                retcode = subprocess.call(cargs)
                if retcode < 0:
                    success = False
                    raise subprocess.CalledProcessError(retcode, ' '.join(cargs))
                    break
            if success:
                shutil.copy('turnin-ng.pdf', doc)
                shutil.rmtree(tempdir, ignore_errors=True)
                # This is required so that the install command can find the
                # build directory. Without it, it searches for it in the
                # non-existent tempdir.
                os.chdir(os.path.join(doc, os.pardir))
                data_files.append((os.path.join(prefix, 'share/doc/turnin-ng/'),
                    ['doc/turnin-ng.pdf']))
                

build.sub_commands.append(('build_pdf', None))

class build_legacy(Command):

    description = 'Include the legacy files from renaming project to turnincfg'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        data_files.append((os.path.join(prefix, 'share/man/man1'),
                ['doc/project.1']))

build.sub_commands.append(('build_legacy', None))

class install_legacy(Command):

    description = 'Install the legacy symlink of project to turnincfg'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.symlink(os.path.join(prefix, 'bin/turnincfg'), os.path.join(prefix,
            'bin/project'))


install.sub_commands.append(('install_legacy', None))

setup(name='turnin-ng',
      version='1.0',
      description='Turn in your assignments with turnin',
      author='Ryan Kavanagh',
      author_email='ryanakca@kubuntu.org',
      license='GNU General Public License version 2, or (at your option) ' +\
              'any later version',
      scripts=['src/bin/turnincfg', 'src/bin/turnin'],
      packages=['turninng'],
      package_dir={'turninng':'src/turninng'},
      data_files=data_files,
      cmdclass={'build_infopage': build_infopage, 'build_pdf':build_pdf,
          'build_htmldocs': build_htmldocs, 'build_legacy': build_legacy,
          'install_legacy': install_legacy}
)
