from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='obs_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building OBS Studio...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Only x64 is supported for OBS Studio as per documentation
    if arch != 'x64':
        raise ValueError("OBS Studio only supports x64 architecture")

    # Configure and build using CMake presets
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"cmake --preset windows-x64 -DCMAKE_BUILD_TYPE={build_mode} &&" +
                         f"cmake --build --preset windows-x64 --config {build_mode}", 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=600000)
    
    # Copy built files to collection directory
    # The built files will be in build_x64/rundir/<build_mode>/bin/64bit
    build_output = os.path.join(clone_dir, "build_x64", "rundir", build_mode, "bin", "64bit")
    collect_cmd = f"xcopy /E /I /Y \"{build_output}\" \"{build_dir}\""
    
    res = cmd_with_output(collect_cmd, platform="windows", cwd=clone_dir, timelimit=60000)

# Set architecture to x64 as it's the only supported option
arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\OBS\\obs-studio',
                         # Use --recursive to clone submodules as required
                         clone_flags='--recursive',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\OBS\\obs-studio',
                         build_dir=f'C:\\\\OBS\\Binaries',
                         project_git_url='https://github.com/obsproject/obs-studio.git',
                         optimization='',
                         build_mode='Release',
                         arch=arch,
                         # Add relevant OBS Studio version tags
                         tags=['30.0.2', '29.1.3', '29.1.2', '29.1.1'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()