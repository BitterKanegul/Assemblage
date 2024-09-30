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
                          f"msbuild ReShade.sln /p:Configuration=Debug /p:Platform=\"64-bit\"", platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\ReShade21\\',
                         clone_flags='--recurse-submodules',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\ReShade21\\',
                         build_dir=f'C:\\\\ReShade21\\',
                         project_git_url='https://github.com/crosire/reshade',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['v6.2.0', 'v5.9.1', 'v4.9.0', 'v3.4.1'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()

'''
https://github.com/crosire/reshade/blob/main/README.md

use msbuild since sln file is already present

'''