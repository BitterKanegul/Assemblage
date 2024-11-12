from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='aws_sdk_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Could add libcurl and openssl installation here if needed
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building AWS SDK C++...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Create build directory and run CMake configuration and build
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. -A {arch} " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DCMAKE_INSTALL_PREFIX={build_dir} " +
                          # Build only core and s3 for example - can be modified based on needs
                          f"-DBUILD_ONLY=\"core;s3\" " +
                          # Use static CRT to match other builds
                          f"-DSTATIC_CRT=ON &&" +
                          f"cmake --build . --config {build_mode} &&" +
                          f"cmake --install . --config {build_mode}", 
                          platform="windows", 
                          cwd=clone_dir, 
                          timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\AWS\\aws-sdk-cpp',
                         # Include --recurse-submodules as required by AWS SDK
                         clone_flags='--recurse-submodules',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\AWS\\aws-sdk-cpp',
                         build_dir=f'C:\\\\AWS\\install',
                         project_git_url='https://github.com/aws/aws-sdk-cpp.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         # Recent release tags from AWS SDK
                         tags=['1.11.238','1.11.182','1.11.163','1.11.141'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()