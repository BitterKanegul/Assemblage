from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='xalanc_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Xalan-C...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Configure CMake build command
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\XalanC\\Binaries " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-Dtranscoder=default " +  # Using default transcoder
                          f"-Dmessage-loader=inmemory " +  # Using in-memory message loader
                          f"-Dsystem-encoding=ascii &&" +  # Using ASCII encoding
                          f"msbuild /m INSTALL.vcxproj -p:Configuration={build_mode}", 
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\XalanC\\xalan-c',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\XalanC\\xalan-c',
                         build_dir=f'C:\\\\XalanC\\Binaries',
                         project_git_url='https://github.com/apache/xalan-c.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['Xalan-C_1_12_0', 'Xalan-C_1_11_0', 'Xalan-C_1_10_0'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()