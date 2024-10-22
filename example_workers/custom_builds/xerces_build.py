from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='xerces_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Xerces-C...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"mkdir xerces-build && cd xerces-build &&" +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" " +
                          f"-DCMAKE_INSTALL_PREFIX=C:\\\\Xerces\\Binaries " +
                          f"-DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-Dnetwork-accessor=winsock " +  # Windows-specific network accessor
                          f"-Dtranscoder=windows " +        # Windows-specific transcoder
                          f"-Dmessage-loader=inmemory " +   # In-memory message loader
                          f"-Dxmlch-type=uint16_t " +      # Use uint16_t for XMLCh
                          f"-Dmutex-manager=windows " +     # Windows threading
                          f"-DBUILD_SHARED_LIBS=ON &&" +    # Build shared libraries
                          f"msbuild /m xerces-c.sln -p:Configuration={build_mode}",
                          platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\Xerces\\xerces-c',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\Xerces\\xerces-c',
                         build_dir=f'C:\\\\Xerces\\Binaries',
                         project_git_url='https://github.com/apache/xerces-c.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['v3.2.5', 'v3.2.4', 'v3.2.3', 'v3.2.2'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()