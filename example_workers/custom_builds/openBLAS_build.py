from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='openblas_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install required conda packages
    cmd_with_output("conda update -n base conda && " +
                   "conda config --add channels conda-forge && " +
                   "conda install -y cmake flang clangdev perl libflang ninja",
                   platform="windows", timelimit=300000)
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building OpenBLAS...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Set environment variables for build
    env_setup = (
        f"set \"LIB=%CONDA_PREFIX%\\Library\\lib;%LIB%\" && " +
        f"set \"CPATH=%CONDA_PREFIX%\\Library\\include;%CPATH%\" "
    )
    
    # Build command
    build_cmd = (
        f"{vcvarsall_loc} {arch} && {env_setup} && " +
        f"cd {clone_dir} && mkdir build && cd build && " +
        f"cmake .. -G \"Ninja\" " +
        f"-DCMAKE_CXX_COMPILER=clang-cl " +
        f"-DCMAKE_C_COMPILER=clang-cl " +
        f"-DCMAKE_Fortran_COMPILER=flang " +
        f"-DCMAKE_MT=mt " +
        f"-DBUILD_WITHOUT_LAPACK=no " +
        f"-DNOFORTRAN=0 " +
        f"-DDYNAMIC_ARCH=ON " +
        f"-DCMAKE_BUILD_TYPE={build_mode} && " +
        f"cmake --build . --config {build_mode} && " +
        f"cmake --install . --prefix {build_dir} -v"
    )

    res = cmd_with_output(build_cmd, platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\OpenBLAS\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\OpenBLAS\\',
                         build_dir=f'C:\\\\OpenBLAS\\install\\',
                         project_git_url='https://github.com/xianyi/OpenBLAS.git',
                         optimization='',
                         build_mode='Release',  # OpenBLAS recommends Release mode for best performance
                         arch=arch,
                         tags=['v0.3.26', 'v0.3.25', 'v0.3.24', 'v0.3.23'],  # Recent stable versions
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()