from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='cpprestsdk_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install dependencies using vcpkg
    vcpkg_cmd = ("vcpkg install --triplet x64-windows zlib openssl boost-system " +
                "boost-date-time boost-regex boost-interprocess websocketpp brotli")
    cmd_with_output(vcpkg_cmd, platform="windows")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building CppRestSDK...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    vcpkg_toolchain = "C:\\vcpkg\\scripts\\buildsystems\\vcpkg.cmake"  # Update this path as needed
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    build_cmd = (
        f"{vcvarsall_loc} {arch} && " +
        f"cd Release && mkdir build.{arch} && cd build.{arch} && " +
        f"cmake .. -A {arch_map[arch]} " +
        f"-DCMAKE_TOOLCHAIN_FILE={vcpkg_toolchain} " +
        f"-DCMAKE_BUILD_TYPE={build_mode} && " +
        f"cmake --build . --config {build_mode}"
    )

    res = cmd_with_output(build_cmd, platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(
    clone_dir='C:\\\\CppRestSDK\\',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\CppRestSDK\\',
    build_dir=f'C:\\\\CppRestSDK\\Release\\build.{arch}\\',
    project_git_url='https://github.com/Microsoft/cpprestsdk.git',
    optimization='',
    build_mode='Release',  # Default to Release build
    arch=arch,
    tags=['v2.10.19', 'v2.10.18', 'v2.10.17', 'v2.10.16'],  # Recent release tags
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)
obj.run()