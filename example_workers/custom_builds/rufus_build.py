from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='rufus_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Rufus doesn't have specific prerequisites to install
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Rufus...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Rufus uses Visual Studio solution file directly
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"msbuild rufus.sln /p:Configuration={build_mode} " +
                         f"/p:Platform={arch_map[arch]}", 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=600000)

# Rufus supports both x86 and x64 builds
arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\Rufus\\',
                        clone_flags='',
                        collect_dir="C:\\Binaries",
                        source_dir='C:\\\\Rufus\\',
                        build_dir=f'C:\\\\Rufus\\build\\',
                        project_git_url='https://github.com/pbatard/rufus.git',
                        optimization='',
                        build_mode='Release',
                        arch=arch,
                        # Using some recent release tags from Rufus
                        tags=['v4.4', 'v4.3', 'v4.2', 'v4.1'],
                        build_hook=build_hook,
                        install_prerequisites_hook=install_prerequisites_hook,
                        compiler_version="Visual Studio 17 2022")
obj.run()