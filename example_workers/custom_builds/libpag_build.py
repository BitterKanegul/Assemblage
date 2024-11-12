from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='libpag_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install NodeJS if not present (required for depsync)
    res = cmd_with_output("where node", platform="windows", timelimit=300)
    if res[0] != 0:
        print("NodeJS not found, please install NodeJS 14.14.0+ manually")
    
    # Install depsync
    cmd_with_output("npm install -g depsync", platform="windows", timelimit=300)
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building LibPAG...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Run depsync to get dependencies
    res = cmd_with_output("depsync", platform="windows", cwd=clone_dir, timelimit=600)
    if res[0] != 0:
        logging.error("Failed to sync dependencies")
        return res

    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Build command using CMake
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\LibPAG\\Binaries " +
                          f"-DPAG_BUILD_TESTS=OFF " +
                          f"-DPAG_BUILD_SHARED=ON &&" +
                          f"msbuild PAG.sln /m /p:Configuration={build_mode}", 
                          platform="windows", cwd=clone_dir, timelimit=7200)

    return res

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\LibPAG\\libpag',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\LibPAG\\libpag',
                         build_dir=f'C:\\\\LibPAG\\libpag\\build',
                         project_git_url='https://github.com/Tencent/libpag.git',
                         optimization='',
                         build_mode='Release',
                         arch=arch,
                         tags=['v4.3.41', 'v4.3.40', 'v4.2.93', 'v4.1.53'],  # Recent release tags
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()