from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='grpc_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install NASM which is required by boringssl
    res = cmd_with_output("choco install nasm -y", platform="windows")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building gRPC...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # First update submodules to get all dependencies
    res = cmd_with_output("git submodule update --init", 
                         platform="windows", 
                         cwd=clone_dir)

    # Build using cmake
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir .build && cd .build &&" +
                          f"cmake .. -A {arch} " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\GRPC\\Binaries " +
                          # DLL builds not recommended for gRPC on Windows
                          f"-DBUILD_SHARED_LIBS=OFF &&" +
                          f"cmake --build . --config {build_mode}",
                          platform="windows",
                          cwd=clone_dir,
                          timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\GRPC\\grpc',
                         # Need --recursive to get submodules
                         clone_flags='--recursive',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\GRPC\\grpc',
                         build_dir='C:\\\\GRPC\\Binaries',
                         project_git_url='https://github.com/grpc/grpc.git',
                         optimization='',
                         build_mode='Release',
                         arch=arch,
                         # Some recent stable release tags
                         tags=['v1.62.0',
                              'v1.61.1',
                              'v1.59.3',
                              'v1.58.2'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()