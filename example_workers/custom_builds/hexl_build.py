from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='hexl_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building HEXL...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Based on HEXL's requirements, we use specific CMake flags
    cmake_flags = [
        f"-A {arch}",
        f"-DCMAKE_BUILD_TYPE={build_mode}",
        "-DHEXL_BENCHMARK=ON",          # Enable benchmarks
        "-DHEXL_TESTING=ON",            # Enable testing
        "-DHEXL_SHARED_LIB=OFF",        # Build static library by default
        "-DCMAKE_INSTALL_PREFIX=C:\\\\HEXL\\Binaries"
    ]

    cmake_flags_str = " ".join(cmake_flags)

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. {cmake_flags_str} -G \"Visual Studio 17 2022\" &&" +
                          f"msbuild INSTALL.vcxproj /p:Configuration={build_mode} /m", 
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'  # HEXL performs best with x64 architecture

obj = CustomWindowsBuild(clone_dir='C:\\\\HEXL\\hexl',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\HEXL\\hexl',
                         build_dir=f'C:\\\\HEXL\\Binaries',
                         project_git_url='https://github.com/intel/hexl.git',
                         optimization='',
                         build_mode='Release',  # Using Release mode for best performance
                         arch=arch,
                         tags=['v1.2.5', 'v1.2.4', 'v1.2.3', 'v1.2.2'],  # Recent stable releases
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()