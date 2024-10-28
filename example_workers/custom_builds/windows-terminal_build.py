from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='openconsole_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Initialize and update git submodules
    res = cmd_with_output("git submodule update --init --recursive", 
                         platform="windows", 
                         cwd=clone_dir)
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building OpenConsole...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to msbuild arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}
    
    # First, import the PowerShell module and set up the dev environment
    powershell_setup = (
        "powershell -ExecutionPolicy Bypass -Command \"" +
        "Import-Module .\\tools\\OpenConsole.psm1; " +
        "Set-MsBuildDevEnvironment; "
    )
    
    # Build command using MSBuild directly with the solution file
    build_cmd = (
        f"{vcvarsall_loc} {arch} && " +
        f"{powershell_setup} " +
        f"msbuild /m /p:Configuration={build_mode} /p:Platform={arch_map[arch]} " +
        f"/p:WindowsTerminalBranding=Dev OpenConsole.sln\""
    )
    
    res = cmd_with_output(build_cmd, 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=600000)
    
    logging.info("Build completed")
    return res

# Configuration for the target architecture
arch = 'x64'

obj = CustomWindowsBuild(
    clone_dir='C:\\\\OpenConsole\\',
    clone_flags='',
    collect_dir="C:\\Binaries\\OpenConsole",
    source_dir='C:\\\\OpenConsole\\',
    build_dir='C:\\\\OpenConsole\\bin\\',
    project_git_url='https://github.com/microsoft/terminal.git',
    optimization='',
    build_mode='Release',  # Can be changed to Debug if needed
    arch=arch,
    tags=['release-v1.19.10171.0', 'release-v1.18.3181.0', 'release-v1.17.11461.0'],  # Recent releases
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)

obj.run()