from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='arrow_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install vcpkg dependencies
    vcpkg_cmd = ("vcpkg install "
                 "--triplet x64-windows "
                 "--x-manifest-root cpp "
                 "--feature-flags=versions "
                 "--clean-after-build")
    
    res = cmd_with_output(vcpkg_cmd, platform="windows", timelimit=7200)
    print("Done installing prerequisites")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Arrow...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # Determine if we're doing a debug build
    is_debug = build_mode.lower() == 'debug'
    
    # Base CMake configuration
    cmake_config = [
        f"cmake .. -Thost=x64 -A {arch}",
        "-G \"Visual Studio 17 2022\"",
        "-DARROW_DEPENDENCY_SOURCE=VCPKG",
        "-DARROW_BUILD_TESTS=ON",
        "-DARROW_BOOST_USE_SHARED=OFF"  # Especially important for debug builds
    ]
    
    # Add debug-specific configurations
    if is_debug:
        cmake_config.extend([
            "-DCMAKE_BUILD_TYPE=Debug",
            "-DBOOST_ROOT=C:/local/boost_1_63_0",
            "-DBOOST_LIBRARYDIR=C:/local/boost_1_63_0/lib64-msvc-14.0"
        ])
    
    # Static linking configurations for various dependencies
    static_lib_configs = [
        "-DBROTLI_MSVC_STATIC_LIB_SUFFIX=_static",
        "-DSNAPPY_MSVC_STATIC_LIB_SUFFIX=_static",
        "-DLZ4_MSVC_STATIC_LIB_SUFFIX=_static",
        "-DZSTD_MSVC_STATIC_LIB_SUFFIX=_static"
    ]
    
    cmake_config.extend(static_lib_configs)
    
    # Combine all CMake configurations
    cmake_command = " ".join(cmake_config)
    
    # Full build command
    build_command = (
        f"{vcvarsall_loc} {arch} && "
        f"cd cpp && "
        f"mkdir build && "
        f"cd build && "
        f"{cmake_command} && "
        f"cmake --build . --config {build_mode}"
    )
    
    res = cmd_with_output(build_command, 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=7200)  # Increased timeout for Arrow build

# Main build configuration
arch = 'x64'

obj = CustomWindowsBuild(
    clone_dir='C:\\\\Arrow\\',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\Arrow\\',
    build_dir='C:\\\\Arrow\\cpp\\build\\',
    project_git_url='https://github.com/apache/arrow.git',
    optimization='',
    build_mode='Release',  # Can be changed to 'Debug' as needed
    arch=arch,
    tags=['apache-arrow-11.0.0', 'apache-arrow-10.0.0', 'apache-arrow-9.0.0'],
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)
obj.run()