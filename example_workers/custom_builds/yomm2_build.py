from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='yomm2_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # YOMM2 requires Boost libraries
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building YOMM2...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Build commands based on README instructions
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build1 && cd build1 &&" +
                          f"cmake .. -A {arch} " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DYOMM2_ENABLE_TESTS=0 " +  # Disable tests by default
                          f"-DYOMM2_ENABLE_BENCHMARKS=0 " +  # Disable benchmarks by default
                          f"-DYOMM2_SHARED=1 " +  # Build as shared library
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\YOMM2\\install &&" +
                          f"cmake --build . --config {build_mode} --target install",
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\YOMM2\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\YOMM2\\',
                         build_dir=f'C:\\\\YOMM2\\build1\\',
                         project_git_url='https://github.com/jll63/yomm2.git',
                         optimization='',
                         build_mode='Release',
                         arch=arch,
                         # Tags from GitHub releases
                         tags=['v1.3.0', 'v1.2.1', 'v1.2.0', 'v1.1.0'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()