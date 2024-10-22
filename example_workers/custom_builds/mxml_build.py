from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='mxml_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building MXML...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # For MXML, we need to use the Visual Studio solution in the vcnet directory
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"cd vcnet &&" +
                         f"msbuild mxml.sln /p:Configuration={build_mode} /p:Platform={arch_map[arch]} /m",
                         platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\MXML\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\MXML\\',
                         build_dir=f'C:\\\\MXML\\vcnet\\',
                         project_git_url='https://github.com/michaelrsweet/mxml.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['v3.3.1', 'v3.3', 'v3.2', 'v3.1'],  # Recent stable releases
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()