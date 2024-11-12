from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='leveldb_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building LevelDB...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # Determine appropriate generator platform based on arch
    platform = "Win64" if arch == "x64" else ""
    generator_platform = f" Win64" if platform else ""

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"cd {clone_dir} && " +
                         f"mkdir build && cd build &&" +
                         f"cmake -G \"Visual Studio 17 2022\" -A {arch_map[arch]} .. &&" +
                         f"msbuild leveldb.sln /m /p:Configuration={build_mode}", 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=300000)

# Set architecture (can be 'x86' or 'x64')
arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\LevelDB\\',
                        clone_flags='',
                        collect_dir="C:\\Binaries",
                        source_dir='C:\\\\LevelDB\\',
                        build_dir=f'C:\\\\LevelDB\\build\\',
                        project_git_url='https://github.com/google/leveldb.git',
                        optimization='',
                        build_mode='Debug',
                        arch=arch,
                        tags=['1.23', '1.22', '1.21', '1.20'],  # Recent LevelDB versions
                        build_hook=build_hook,
                        install_prerequisites_hook=install_prerequisites_hook,
                        compiler_version="Visual Studio 17 2022")
obj.run()