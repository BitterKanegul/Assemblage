from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   filename='re2_build.log',
                   filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install Abseil dependency first
    vcvarsall_loc = "\"C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    abseil_commands = [
        f"git clone https://github.com/abseil/abseil-cpp.git C:\\abseil",
        f"cd C:\\abseil && mkdir build && cd build &&",
        f"{vcvarsall_loc} x64 &&",
        f"cmake .. -A x64 -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_STANDARD=17 &&",
        f"msbuild absl.sln /m /p:Configuration=Debug"
    ]
    
    for cmd in abseil_commands:
        cmd_with_output(cmd, platform="windows", timelimit=300000)
    print("Done installing prerequisites")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building RE2...")
    vcvarsall_loc = "\"C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Build RE2 using CMake
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"mkdir build && cd build &&" +
                         f"cmake .. -A {arch} " +
                         f"-DCMAKE_BUILD_TYPE={build_mode} " +
                         f"-DCMAKE_CXX_STANDARD=17 " +
                         f"-DCMAKE_PREFIX_PATH=C:\\abseil\\build " +
                         f"-DRE2_BUILD_TESTING=OFF &&" +
                         f"msbuild re2.sln /m /p:Configuration={build_mode}",
                         platform="windows",
                         cwd=clone_dir,
                         timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\RE2',
                        clone_flags='',
                        collect_dir="C:\\Binaries",
                        source_dir='C:\\RE2',
                        build_dir='C:\\RE2\\build',
                        project_git_url='https://github.com/google/re2.git',
                        optimization='',
                        build_mode='Debug',
                        arch=arch,
                        tags=['2024-03-01', '2023-11-01', '2023-09-01', '2023-07-01'],
                        build_hook=build_hook,
                        install_prerequisites_hook=install_prerequisites_hook,
                        compiler_version="Visual Studio 17 2022")
obj.run()