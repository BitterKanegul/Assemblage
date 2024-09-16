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
    logging.info("Building STL...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"cmake --preset {arch_map[arch]} &&" +
                          f"cmake --build --preset {arch_map[arch]}", platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x86'

obj = CustomWindowsBuild(clone_dir='C:\\\\STL\\',
                         clone_flags=' --recursive',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\STL\\',
                         build_dir=f'C:\\\\STL\\out\\{arch}\\out',
                         project_git_url='https://github.com/microsoft/STL',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['vs-2022-17.11','vs-2022-17.10','vs-2022-17.9','vs-2022-17.8'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()


