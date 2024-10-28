from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='winget_build.log',
                    filemode='w')

def install_prerequisites_hook():
    logging.info("Installing prerequisites...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Install Windows SDK if not present
    cmd_with_output("winget install Microsoft.WindowsSDK --version 10.0.22000.832 --accept-source-agreements --accept-package-agreements",
                   platform="windows", timelimit=300000)
    
    # Enable Developer Mode via registry
    cmd_with_output("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AppModelUnlock\" /t REG_DWORD /f /v \"AllowDevelopmentWithoutDevLicense\" /d \"1\"",
                   platform="windows", timelimit=60000)
    
    # Run vcpkg integrate install
    cmd_with_output(f"{vcvarsall_loc} x64 && vcpkg integrate install",
                   platform="windows", timelimit=300000)
    
    logging.info("Prerequisites installation completed")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Winget...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to msbuild arch
    arch_map = {
        'x64': 'x64',
        'x64_arm': 'ARM',
        'x64_arm64': 'ARM64',
        'x86': 'x86'
    }
    
    msbuild_arch = arch_map.get(arch, arch)
    
    # Apply configuration using winget configure
    cmd_with_output("winget configure .configurations/configuration.dsc.yaml",
                   platform="windows", cwd=clone_dir, timelimit=300000)
    
    # Build the solution
    res = cmd_with_output(
        f"{vcvarsall_loc} {arch} && " +
        f"cd src && " +
        f"msbuild AppInstallerCLI.sln " +
        f"/p:Configuration={build_mode} " +
        f"/p:Platform={msbuild_arch} " +
        f"/m /p:RestorePackagesConfig=true " +
        f"/t:Restore,Build " +
        f"&& msbuild AppInstallerCLI.sln /t:Deploy",
        platform="windows",
        cwd=clone_dir,
        timelimit=600000
    )
    
    logging.info("Build completed")
    return res

def main():
    arch = 'x64'  # Winget primarily targets x64
    
    obj = CustomWindowsBuild(
        clone_dir='C:\\\\Winget\\winget-cli',
        clone_flags='',
        collect_dir="C:\\Binaries",
        source_dir='C:\\\\Winget\\winget-cli',
        build_dir='C:\\\\Winget\\winget-cli\\src',
        project_git_url='https://github.com/microsoft/winget-cli.git',
        optimization='',
        build_mode='Release',  # Usually built in Release mode
        arch=arch,
        tags=['v1.7.10722', 'v1.6.3482', 'v1.5.2201', 'v1.4.11391'],  # Recent stable releases
        build_hook=build_hook,
        install_prerequisites_hook=install_prerequisites_hook,
        compiler_version="Visual Studio 17 2022"
    )
    
    obj.run()

if __name__ == "__main__":
    main()