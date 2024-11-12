from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='mmkv_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building MMKV...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'Win32'}

    # Convert arch to the format expected by MSBuild
    platform = arch_map.get(arch, 'Win32')
    
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"cd Core && " +
                         f"msbuild core.vcxproj " +
                         f"/p:Configuration={build_mode} " +
                         f"/p:Platform={platform} " +
                         f"/p:PlatformToolset=v143 " +  # VS2022 toolset
                         f"/p:RuntimeLibrary={'MultiThreadedDebug' if build_mode == 'Debug' else 'MultiThreaded'}", 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=600000)
    
    # Copy the built files to the collection directory
    output_dir = os.path.join(clone_dir, "Win32", "MMKV")
    if arch == "x64":
        output_dir = os.path.join(output_dir, "x64")
    output_dir = os.path.join(output_dir, build_mode)
    
    # Create include directory and copy headers
    include_dir = os.path.join(build_dir, "include", "MMKV")
    os.makedirs(include_dir, exist_ok=True)
    cmd_with_output(f"xcopy /Y /S /I {clone_dir}\\Core\\*.h {include_dir}", 
                   platform="windows", 
                   cwd=clone_dir)
    
    # Copy library files
    os.makedirs(build_dir, exist_ok=True)
    cmd_with_output(f"xcopy /Y {output_dir}\\mmkv.lib {build_dir} && " +
                   f"xcopy /Y {output_dir}\\mmkv.pdb {build_dir}",
                   platform="windows",
                   cwd=clone_dir)

arch = 'x64'  # or 'x86' for 32-bit builds

obj = CustomWindowsBuild(clone_dir='C:\\\\MMKV',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\MMKV',
                         build_dir='C:\\\\MMKV\\build',
                         project_git_url='https://github.com/Tencent/MMKV.git',
                         optimization='',
                         build_mode='Debug',  # or 'Release'
                         arch=arch,
                         tags=['v1.3.3', 'v1.3.2', 'v1.3.1', 'v1.3.0'],  # Recent versions
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()