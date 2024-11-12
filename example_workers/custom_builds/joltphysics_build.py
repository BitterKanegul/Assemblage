from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='jolt_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building JoltPhysics...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # CMake configuration based on JoltPhysics build requirements
    cmake_config = [
        f"-A {arch}",
        f"-DCMAKE_BUILD_TYPE={build_mode}",
        "-G \"Visual Studio 17 2022\"",
        # Add common JoltPhysics build options
        "-DINTERPROCEDURAL_OPTIMIZATION=ON",
        "-DTARGET_UNIT_TESTS=ON",
        "-DTARGET_SAMPLES=ON"
    ]
    
    # For distribution builds, disable debug features
    if build_mode == "Distribution":
        cmake_config.extend([
            "-DDEBUG_RENDERER_IN_DISTRIBUTION=OFF",
            "-DJPH_DEBUG_RENDERER=OFF"
        ])
    else:
        cmake_config.extend([
            "-DDEBUG_RENDERER_IN_DEBUG_AND_RELEASE=ON",
            "-DJPH_DEBUG_RENDERER=ON"
        ])

    cmake_args = " ".join(cmake_config)
    
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"mkdir build_{build_mode.lower()} && " +
                         f"cd build_{build_mode.lower()} && " +
                         f"cmake .. {cmake_args} && " +
                         f"msbuild JoltPhysics.sln /m /p:Configuration={build_mode}", 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\JoltPhysics\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\JoltPhysics\\',
                         build_dir=f'C:\\\\JoltPhysics\\build_{build_mode.lower()}\\',
                         project_git_url='https://github.com/jrouwe/JoltPhysics.git',
                         optimization='',
                         build_mode='Release',  # Options: Debug, Release, Distribution
                         arch=arch,
                         tags=['v4.0.2', 'v4.0.1', 'v4.0.0', 'v3.0.1'],  # Recent release tags
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()