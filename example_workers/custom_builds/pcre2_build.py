from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='mstl.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building PCRE2...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir -p build1 && cd build1 &&" +
                          f"cmake .. -A {arch} -DCMAKE_BUILD_TYPE={build_mode} &&" +
                          f"msbuild PCRE2.sln", platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x86'

obj = CustomWindowsBuild(clone_dir='C:\\\\PCRE2\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\PCRE2\\',
                         build_dir=f'C:\\\\PCRE2\\build1\\',
                         project_git_url='https://github.com/PCRE2Project/pcre2',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['pcre2-10.44','pcre2-10.38','pcre2-10.34','pcre2-10.22'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()

'''
https://github.com/PCRE2Project/pcre2

NON-AUTOTOOLS-BUILD

https://github.com/PCRE2Project/pcre2/blob/master/NON-AUTOTOOLS-BUILD

BUILDING PCRE2 ON WINDOWS WITH VISUAL STUDIO

The code currently cannot be compiled without an inttypes.h header, which is
available only with Visual Studio 2013 or newer. However, this portable and
permissively-licensed implementation of the stdint.h header could be used as an
alternative:

  http://www.azillionmonkeys.com/qed/pstdint.h

Just rename it and drop it into the top level of the build tree.


'''