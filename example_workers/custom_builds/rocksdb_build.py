from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   filename='rocksdb_build.log',
                   filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # RocksDB can build without dependencies but recommended to have compression libraries
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building RocksDB...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # RocksDB CMake build command
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"mkdir build && cd build &&" +
                         f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                         f"-DCMAKE_INSTALL_PREFIX=C:\\\\RocksDB\\Binaries " +
                         f"-DCMAKE_BUILD_TYPE={build_mode} " +
                         f"-DPORTABLE=1 " +  # For better compatibility
                         f"-DWITH_GFLAGS=OFF " +  # Optional dependency
                         f"-DROCKSDB_BUILD_SHARED=OFF " +  # Build static lib only
                         f"-DROCKSDB_LITE=OFF " +  # Full feature set
                         f"-DWITH_TESTS=OFF " +  # Skip tests
                         f"-DWITH_TOOLS=OFF && " +  # Skip tools
                         f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj",
                         platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\RocksDB\\',
                        clone_flags='',
                        collect_dir="C:\\Binaries",
                        source_dir='C:\\\\RocksDB\\',
                        build_dir=f'C:\\\\RocksDB\\build\\',
                        project_git_url='https://github.com/facebook/rocksdb.git',
                        optimization='',
                        build_mode='Release',  # Using Release mode for production build
                        arch=arch,
                        tags=['v8.10.0', 'v8.9.1', 'v8.8.1', 'v8.7.3', 'v8.6.7'],  # Recent stable versions
                        build_hook=build_hook,
                        install_prerequisites_hook=install_prerequisites_hook,
                        compiler_version="Visual Studio 17 2022")
obj.run()