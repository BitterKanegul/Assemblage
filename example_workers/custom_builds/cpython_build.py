from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='cpython.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building CPython...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""

    res = cmd_with_output(f"cd PCBuild &&" +
                          f"{vcvarsall_loc} {arch} &&" +
                          f"build.bat -c {build_mode} -p {arch}", platform="windows", cwd=clone_dir, timelimit=600000)



obj = CustomWindowsBuild(clone_dir='C:\\\\CPython\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\CPython\\',
                         build_dir='C:\\\\CPython\\',
                         project_git_url='https://github.com/python/cpython',
                         optimization='',
                         build_mode='Debug',
                         arch='x64',
                         tags=['v3.12.6', 'v3.12.0', 'v3.11.10', 'v3.10.15'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()



# Run build.bat after cloning the repo
#  -c Release ^| Debug