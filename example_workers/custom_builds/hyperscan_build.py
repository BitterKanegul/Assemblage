from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='hyperscan_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Based on the requirements from documentation
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Hyperscan...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Following the build instructions from documentation
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          # Adding required CMake flags from documentation
                          f"-DBUILD_SHARED_LIBS=ON " +
                          f"-DFAT_RUNTIME=OFF " +  # Fat runtime not supported on Windows
                          f"-DBOOST_ROOT=C:\\\\boost_1_57_0 &&" +
                          f"msbuild ALL_BUILD.vcxproj /p:Configuration={build_mode} /m", 
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'  # Default to x64 as Hyperscan requires modern x86 processors

obj = CustomWindowsBuild(clone_dir='C:\\\\Hyperscan\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\Hyperscan\\',
                         build_dir=f'C:\\\\Hyperscan\\build\\',
                         project_git_url='https://github.com/intel/hyperscan.git',
                         optimization='',
                         build_mode='Debug',  # Can be Debug or Release
                         arch=arch,
                         # Using some recent versions from their releases
                         tags=['v5.4.2', 'v5.4.1', 'v5.4.0', 'v5.3.0'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()