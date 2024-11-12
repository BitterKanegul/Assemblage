from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='folly_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Folly has several dependencies but they should be handled by the build system
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Folly...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Note: Folly requires C++17, so we add the appropriate flags
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. -A {arch} " +
                          f"-G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\Folly\\Binaries " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DBOOST_ROOT=C:\\\\boost " +  # Adjust paths as needed
                          f"-DBUILD_TESTS=OFF " +
                          f"-DCMAKE_CXX_STANDARD=17 " +
                          f"-DFOLLY_USE_STATIC_RUNTIME=ON &&" +
                          f"msbuild folly.sln /m /p:Configuration={build_mode} " +
                          f"/p:Platform={arch} /p:PreferredToolArchitecture=x64",
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'  # Folly is primarily tested on x64

obj = CustomWindowsBuild(clone_dir='C:\\\\Folly\\folly',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\Folly\\folly',
                         build_dir=f'C:\\\\Folly\\Binaries',
                         project_git_url='https://github.com/facebook/folly.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['v2024.01.15.00', 'v2023.12.18.00', 'v2023.11.20.00', 'v2023.10.23.00'],  # Recent releases
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()

'''
Building Facebook's Folly Library
================================

Prerequisites:
- Visual Studio 2022 with C++ workload
- CMake 3.13+
- Python 3.6+
- Git
- Boost (with C++17 support)
- OpenSSL
- Double-conversion
- gflags
- glog
- ZLIB
- zstd
- libevent
- snappy
- lz4
- libsodium

Build Process:
1. Clone the repository
2. Create build directory
3. Configure with CMake
4. Build with MSBuild
5. Install to specified location

Key CMake Options:
-DBUILD_TESTS=OFF : Disable building tests
-DCMAKE_CXX_STANDARD=17 : Enable C++17 support
-DFOLLY_USE_STATIC_RUNTIME=ON : Use static runtime linking

Note: Dependencies should be installed and findable by CMake. Adjust paths in 
CMake configuration if needed.

References:
- https://github.com/facebook/folly
- https://github.com/facebook/folly/blob/main/CMake/README.md
'''