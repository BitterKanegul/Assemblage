from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='arrayfire_build.log',
                    filemode='w')

def install_prerequisites_hook():
    logging.info("Installing prerequisites...")
    vcpkg_commands = [
        # Backend-independent dependencies
        "vcpkg install --triplet x64-windows freeimage",
        # Graphics support
        "vcpkg install --triplet x64-windows glfw3 freetype",
        # CPU backend
        "vcpkg install --triplet x64-windows openblas fftw3",
        # CUDA backend
        "vcpkg install --triplet x64-windows boost",
        # OpenCL backend
        "vcpkg install --triplet x64-windows openblas"
    ]
    
    for cmd in vcpkg_commands:
        res = cmd_with_output(cmd, platform="windows", timelimit=300000)
    
    # Initialize oneAPI environment if needed
    oneapi_init = "\"C:\\Program Files (x86)\\Intel\\oneAPI\\setvars.bat\""
    res = cmd_with_output(oneapi_init, platform="windows", timelimit=60000)
    
    logging.info("Prerequisites installation completed")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building ArrayFire...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # Get vcpkg path from environment or use default
    vcpkg_path = os.getenv('VCPKG_ROOT', 'C:\\vcpkg')
    
    cmake_options = [
        f"-G \"Visual Studio 17 2022\"",
        f"-A {arch}",
        f"-DCMAKE_TOOLCHAIN_FILE=\"{vcpkg_path}\\scripts\\buildsystems\\vcpkg.cmake\"",
        "-DCMAKE_BUILD_TYPE=" + build_mode,
        "-DAF_BUILD_CUDA=ON",
        "-DAF_BUILD_OPENCL=ON",
        "-DAF_BUILD_ONEAPI=ON",
        "-DAF_BUILD_CPU=ON",
        "-DAF_BUILD_FORGE=ON",
        "-DBUILD_TESTING=ON"
    ]
    
    # For CUDA compatibility with VS2022, use the v143 toolset
    if arch == 'x64':
        cmake_options.append("-Tv143")
    
    cmake_command = " ".join(cmake_options)
    
    build_command = (
        f"{vcvarsall_loc} {arch} && "
        f"cd {clone_dir} && "
        f"mkdir build && cd build && "
        f"cmake {cmake_command} .. && "
        f"msbuild ArrayFire.sln /m /p:Configuration={build_mode}"
    )
    
    res = cmd_with_output(build_command, platform="windows", cwd=clone_dir, timelimit=600000)

# Main execution
arch = 'x64'

obj = CustomWindowsBuild(
    clone_dir='C:\\\\ArrayFire',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\ArrayFire',
    build_dir='C:\\\\ArrayFire\\build',
    project_git_url='https://github.com/arrayfire/arrayfire.git',
    optimization='',
    build_mode='Release',
    arch=arch,
    tags=['v3.9.0', 'v3.8.3', 'v3.8.2', 'v3.8.1'],
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)

obj.run()