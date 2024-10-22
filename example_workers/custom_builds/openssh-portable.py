from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   filename='openssh_build.log',
                   filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building OpenSSH...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to PowerShell build script arch
    arch_map = {
        'x64': 'x64',
        'x86': 'x86',
        'x64_arm': 'ARM',
        'x64_arm64': 'ARM64'
    }

    # The build command using PowerShell and the provided build helper module
    res = cmd_with_output(f"{vcvarsall_loc} {arch} && " +
                         f"powershell -ExecutionPolicy Bypass -Command \"" +
                         f"Import-Module .\\contrib\\win32\\openssh\\OpenSSHBuildHelper.psm1 -Force; " +
                         f"Start-OpenSSHBuild -Configuration {build_mode} -NativeHostArch {arch_map[arch]}\"",
                         platform="windows",
                         cwd=clone_dir,
                         timelimit=600000)

# Default architecture
arch = 'x64'

obj = CustomWindowsBuild(
    clone_dir='C:\\\\OpenSSH\\',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\OpenSSH\\',
    build_dir='C:\\\\OpenSSH\\bin',
    project_git_url='https://github.com/PowerShell/openssh-portable.git',
    optimization='',
    build_mode='Debug',
    arch=arch,
    tags=['V9.5.0.0', 'V9.4.0.0', 'V9.3.0.0', 'V9.2.0.0'],  # Recent OpenSSH Windows release tags
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022")

obj.run()

'''
Building OpenSSH for Windows

Requirements:
- Visual Studio 2022
- PowerShell
- Git for Windows

The script will:
1. Clone the OpenSSH repository
2. Import the PowerShell build helper module
3. Execute the build process using the specified configuration and architecture
4. Output binaries to the specified collection directory

Usage:
1. Ensure Visual Studio 2022 is installed
2. Run the script with appropriate permissions
3. Built binaries will be available in C:\\Binaries

The script supports:
- Debug and Release configurations
- x64, x86, ARM, and ARM64 architectures
- Building specific tagged versions
'''