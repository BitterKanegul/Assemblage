from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='onetbb_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building oneTBB...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\TBB\\Binaries " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DTBB_TEST=OFF &&" +
                          f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj",
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\TBB\\oneTBB',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\TBB\\oneTBB',
                         build_dir=f'C:\\\\TBB\\Binaries',
                         project_git_url='https://github.com/oneapi-src/oneTBB.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['v2021.11.0', 'v2021.10.0', 'v2021.9.0', 'v2021.8.0'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()