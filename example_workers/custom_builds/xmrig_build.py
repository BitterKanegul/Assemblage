from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='xmrig_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Download and setup dependencies
    res = cmd_with_output(
        "git clone https://github.com/xmrig/xmrig-deps.git C:\\xmrig-deps",
        platform="windows",
        timelimit=300000
    )
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building XMRig...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Construct the build command
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"cd {clone_dir} && mkdir build && cd build &&" +
                          f"cmake .. -G \"Visual Studio 17 2022\" -A {arch} " +
                          f"-DXMRIG_DEPS=C:\\\\xmrig-deps\\msvc2019\\{arch} " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} &&" +
                          f"cmake --build . --config {build_mode}",
                          platform="windows",
                          cwd=clone_dir,
                          timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\XMRig\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\XMRig\\',
                         build_dir=f'C:\\\\XMRig\\build\\',
                         project_git_url='https://github.com/xmrig/xmrig.git',
                         optimization='',
                         build_mode='Release',
                         arch=arch,
                         tags=['v6.21.0', 'v6.20.0', 'v6.19.3', 'v6.19.2'],  # Recent stable versions
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()