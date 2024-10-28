from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   filename='telegram_build.log',
                   filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Install Python 3.10 if not present
    # Note: In practice, you might want to check if Python is already installed
    # and verify its version before proceeding
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Telegram Desktop...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to cmake preset arch
    arch_map = {'x64': 'x64', 'x64_arm': 'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}

    # First prepare the build environment using the provided script
    prepare_cmd = cmd_with_output(f"cd {clone_dir}\\Telegram\\build\\prepare && win.bat",
                                platform="windows",
                                cwd=clone_dir,
                                timelimit=600000)

    # Configure the build with cmake
    # Note: API_ID and API_HASH should be provided as environment variables or parameters
    configure_cmd = cmd_with_output(f"{vcvarsall_loc} {arch} && " +
                                  f"cd {clone_dir}\\Telegram && " +
                                  f"configure.bat {arch_map[arch]} " +
                                  f"-D TDESKTOP_API_ID=%TELEGRAM_API_ID% " +
                                  f"-D TDESKTOP_API_HASH=%TELEGRAM_API_HASH% " +
                                  f"-D CMAKE_BUILD_TYPE={build_mode}",
                                  platform="windows",
                                  cwd=clone_dir,
                                  timelimit=600000)

    # Build the project using MSBuild
    build_cmd = cmd_with_output(f"{vcvarsall_loc} {arch} && " +
                               f"cd {clone_dir}\\out && " +
                               f"msbuild Telegram.sln /p:Configuration={build_mode} /m",
                               platform="windows",
                               cwd=clone_dir,
                               timelimit=600000)

    # Copy the built executable to the collection directory
    collect_cmd = cmd_with_output(f"xcopy {clone_dir}\\out\\{build_mode}\\Telegram.exe {build_dir}\\",
                                platform="windows",
                                cwd=clone_dir,
                                timelimit=60000)

# Default architecture
arch = 'x64'

# Create the build object
obj = CustomWindowsBuild(
    clone_dir='C:\\TBuild\\tdesktop',
    clone_flags='--recursive',
    collect_dir="C:\\TBuild\\Binaries",
    source_dir='C:\\TBuild\\tdesktop',
    build_dir='C:\\TBuild\\Binaries',
    project_git_url='https://github.com/telegramdesktop/tdesktop.git',
    optimization='',
    build_mode='Release',
    arch=arch,
    tags=['v4.15.2', 'v4.15.1', 'v4.15.0', 'v4.14.13'],  # Recent stable versions
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)

# Run the build process
obj.run()