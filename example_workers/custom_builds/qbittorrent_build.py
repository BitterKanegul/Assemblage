from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='qbittorrent_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install vcpkg dependencies
    vcpkg_cmd = (
        "git clone https://github.com/microsoft/vcpkg && "
        "cd vcpkg && "
        ".\\bootstrap-vcpkg.bat -disableMetrics && "
        ".\\vcpkg integrate install && "
        ".\\vcpkg install boost-circular-buffer:x64-windows-static " +
        "boost-stacktrace:x64-windows-static " +
        "openssl:x64-windows-static " +
        "qt5-base:x64-windows-static " +
        "qt5-svg:x64-windows-static " +
        "qt5-tools:x64-windows-static " +
        "qt5-winextras:x64-windows-static " +
        "libtorrent:x64-windows-static"
    )
    cmd_with_output(vcpkg_cmd, platform="windows", cwd="C:\\")
    print("Done installing prerequisites")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building qBittorrent...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # Get the vcpkg toolchain file path
    vcpkg_toolchain = "C:\\\\vcpkg\\scripts\\buildsystems\\vcpkg.cmake"
    
    build_cmd = (
        f"{vcvarsall_loc} {arch} && "
        f"cmake -G \"Ninja\" -B build "
        f"-DCMAKE_BUILD_TYPE={build_mode} "
        f"-DCMAKE_TOOLCHAIN_FILE=\"{vcpkg_toolchain}\" "
        f"-DVCPKG_TARGET_TRIPLET=\"{arch}-windows-static\" "
        f"-DMSVC_RUNTIME_DYNAMIC=OFF && "
        f"cmake --build build"
    )
    
    res = cmd_with_output(build_cmd, platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(
    clone_dir='C:\\\\qBittorrent\\',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\qBittorrent\\',
    build_dir='C:\\\\qBittorrent\\build\\',
    project_git_url='https://github.com/qbittorrent/qBittorrent.git',
    optimization='',
    build_mode='Release',
    arch=arch,
    tags=['release-4.6.3', 'release-4.5.5', 'release-4.4.5'],  # Recent stable releases
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)
obj.run()