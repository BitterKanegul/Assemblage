from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='go_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building STL...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    build_map={'Release': 'release', 'Debug': 'debug'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"vcbuild.bat {build_map[build_mode]} {arch_map[arch]}", platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\Node\\node',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\Node\\node',
                         build_dir=f'C:\\\\Node\\node\\out\\Debug',
                         project_git_url='https://github.com/nodejs/node',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['v22.9.0','v20.17.0','v18.9.1','v16.4.0'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()

'''
via
https://github.com/nodejs/node/blob/main/BUILDING.md#windows

You may need disable vcpkg integration if you got link error about symbol redefine related to zlib.lib(zlib1.dll), even you never install it by hand, as vcpkg is part of CLion and Visual Studio now.


Windows Prerequisites
Option 1: Manual install
The current version of Python from the Microsoft Store
The "Desktop development with C++" workload from Visual Studio 2022 (17.6 or newer) or the "C++ build tools" workload from the Build Tools, with the default optional components
Basic Unix tools required for some tests, Git for Windows includes Git Bash and tools which can be included in the global PATH.
The NetWide Assembler, for OpenSSL assembler modules. If not installed in the default location, it needs to be manually added to PATH. A build with the openssl-no-asm option does not need this, nor does a build targeting ARM64 Windows.

Remember to first clone the Node.js repository with the Git command and head to the directory that Git created; If you haven't already
git clone https://github.com/nodejs/node.git
cd node

If you are building from a Windows machine, symlinks are disabled by default, and can be enabled by cloning with the -c core.symlinks=true flag.

To start the build process:

.\vcbuild


  vcbuild.bat debug                    : builds debug build
  vcbuild.bat release


'''