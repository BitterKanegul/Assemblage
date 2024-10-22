from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='mbedtls_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building MbedTLS...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir build && cd build &&" +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\MbedTLS\\Binaries " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DENABLE_TESTING=OFF " +  # Disable testing as it requires Python/Perl
                          f"-DENABLE_PROGRAMS=ON &&" +  # Enable building programs including selftest
                          f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj", 
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'  # You can change this to 'x86' if needed

obj = CustomWindowsBuild(clone_dir='C:\\\\MbedTLS\\mbedtls',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\MbedTLS\\mbedtls',
                         build_dir=f'C:\\\\MbedTLS\\Binaries',
                         project_git_url='https://github.com/Mbed-TLS/mbedtls.git',
                         optimization='',
                         build_mode='Debug',  # Can be changed to 'Release'
                         arch=arch,
                         tags=['v3.5.2', 'v3.4.1', 'v3.3.0', 'v3.2.1'],  # Recent stable versions
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()