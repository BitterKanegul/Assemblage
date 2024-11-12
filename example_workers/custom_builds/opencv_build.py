from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='opencv_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building OpenCV...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # Create build directory for OpenCV
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"cd {clone_dir} && " +
                          f"mkdir opencv-build && cd opencv-build && " +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\OpenCV\\Binaries " +
                          f"-DOPENCV_EXTRA_MODULES_PATH={clone_dir}\\..\\opencv_contrib\\modules " +
                          f"-DBUILD_WITH_DEBUG_INFO=ON " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DBUILD_SHARED_LIBS=ON " +
                          f"-DBUILD_EXAMPLES=OFF " +
                          f"-DBUILD_TESTS=OFF " +
                          f"-DBUILD_PERF_TESTS=OFF " +
                          f"-DBUILD_opencv_world=ON " +
                          f"-DWITH_CUDA=OFF " +  # Adjust based on your needs
                          f"-DINSTALL_PYTHON_EXAMPLES=OFF " +
                          f"-DINSTALL_C_EXAMPLES=OFF && " +
                          f"msbuild /m -p:Configuration={build_mode} ALL_BUILD.vcxproj && " +
                          f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj",
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

# Main OpenCV repository
opencv_obj = CustomWindowsBuild(
    clone_dir='C:\\\\OpenCV\\opencv',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\OpenCV\\opencv',
    build_dir='C:\\\\OpenCV\\Binaries',
    project_git_url='https://github.com/opencv/opencv.git',
    optimization='',
    build_mode='Release',  # You can change to 'Debug' if needed
    arch=arch,
    tags=['4.9.0', '4.8.0', '4.7.0'],  # Adjust versions as needed
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)

# OpenCV contrib modules repository
opencv_contrib_obj = CustomWindowsBuild(
    clone_dir='C:\\\\OpenCV\\opencv_contrib',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\OpenCV\\opencv_contrib',
    build_dir='C:\\\\OpenCV\\Binaries',
    project_git_url='https://github.com/opencv/opencv_contrib.git',
    optimization='',
    build_mode='Release',  # Should match main OpenCV build mode
    arch=arch,
    tags=['4.9.0', '4.8.0', '4.7.0'],  # Should match main OpenCV tags
    build_hook=None,  # No separate build needed for contrib
    install_prerequisites_hook=None,
    compiler_version="Visual Studio 17 2022"
)

# First clone and checkout both repositories
opencv_contrib_obj.clone_and_checkout()
opencv_obj.run()  # This will handle the full build process