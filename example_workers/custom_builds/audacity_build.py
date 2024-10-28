from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='audacity.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Audacity...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir -p build1 && cd build1 &&" +
                          f"cmake .. -A {arch} -DCMAKE_BUILD_TYPE={build_mode} &&" +
                          f"msbuild Audacity.sln", platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x86'

obj = CustomWindowsBuild(clone_dir='C:\\\\Audacity\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\Audacity\\',
                         build_dir=f'C:\\\\Audacity\\build1\\',
                         project_git_url='https://github.com/audacity/audacity',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['Audacity-3.6.4','Audacity-3.0.5','Audacity-2.3.3','Audacity-2.0.2'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()

'''
https://github.com/audacity/audacity/blob/master/BUILDING.md


'''