from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='pdfio_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install zlib if not present - required for PDFio
    res = cmd_with_output("vcpkg install zlib:x64-windows-static", 
                         platform="windows", 
                         timelimit=300000)
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building PDFio...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # Build using Visual Studio solution
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"msbuild pdfio.sln /p:Configuration={build_mode} " +
                         f"/p:Platform={arch_map[arch]} /m", 
                         platform="windows", 
                         cwd=clone_dir,
                         timelimit=300000)

    # Copy built artifacts to collection directory
    if build_mode == 'Debug':
        dll_suffix = 'd'
    else:
        dll_suffix = ''
        
    res = cmd_with_output(f"copy {build_mode}\\PDFIO1{dll_suffix}.dll {build_dir} && " +
                         f"copy {build_mode}\\PDFIO1{dll_suffix}.lib {build_dir} && " +
                         f"copy {build_mode}\\PDFIO1{dll_suffix}.pdb {build_dir}",
                         platform="windows",
                         cwd=clone_dir,
                         timelimit=60000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\PDFio\\',
                        clone_flags='',
                        collect_dir="C:\\Binaries", 
                        source_dir='C:\\\\PDFio\\',
                        build_dir=f'C:\\\\PDFio\\build\\',
                        project_git_url='https://github.com/michaelrsweet/pdfio.git',
                        optimization='',
                        build_mode='Debug',
                        arch=arch,
                        tags=['v1.1.0', 'v1.0.0', 'v0.9.0', 'v0.8.0'],
                        build_hook=build_hook,
                        install_prerequisites_hook=install_prerequisites_hook,
                        compiler_version="Visual Studio 17 2022")
obj.run()