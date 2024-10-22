from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='fizz_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Fizz...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir fizz-build && cd fizz-build &&" +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\Fizz\\Binaries " +
                          f"-DCMAKE_PREFIX_PATH=C:\\\\Fizz\\Binaries " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} &&" +
                          f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj",
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\Fizz\\fizz',
                         clone_flags='--recursive',  # Add recursive flag as specified
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\Fizz\\fizz',
                         build_dir=f'C:\\\\Fizz\\Binaries',
                         project_git_url='https://github.com/facebookincubator/fizz.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['v2024.03.25.00', 'v2024.01.15.00', 'v2023.10.30.00'],  # Recent release tags
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()