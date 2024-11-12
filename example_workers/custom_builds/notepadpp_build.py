from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='notepadpp_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Notepad++...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to Visual Studio arch format
    arch_map = {'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'Win32'}
    vs_arch = arch_map.get(arch, 'x64')  # Default to x64 if mapping not found
    
    # Building Scintilla static library first
    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                         f"cd scintilla\\win32 &&" +
                         f"nmake -f scintilla.mak {'' if build_mode == 'Release' else 'DEBUG=1'} &&" +
                         f"cd ..\\..\\lexilla\\src &&" +
                         f"nmake -f lexilla.mak {'' if build_mode == 'Release' else 'DEBUG=1'} &&" +
                         f"cd ..\\..\\PowerEditor\\visual.net &&" +
                         f"msbuild notepadPlus.sln /p:Configuration={build_mode} /p:Platform={vs_arch}", 
                         platform="windows", 
                         cwd=clone_dir, 
                         timelimit=600000)

arch = 'x64'  # Can be modified based on needs

obj = CustomWindowsBuild(clone_dir='C:\\\\NotepadPP\\notepad-plus-plus',
                        clone_flags='',
                        collect_dir="C:\\Binaries",
                        source_dir='C:\\\\NotepadPP\\notepad-plus-plus',
                        build_dir=f'C:\\\\NotepadPP\\notepad-plus-plus\\PowerEditor\\visual.net\\{arch}\\{build_mode}',
                        project_git_url='https://github.com/notepad-plus-plus/notepad-plus-plus.git',
                        optimization='',
                        build_mode='Release',  # Can be 'Debug' or 'Release'
                        arch=arch,
                        tags=['v8.6.4', 'v8.6.3', 'v8.6.2', 'v8.6.1', 'v8.6'],  # Recent releases
                        build_hook=build_hook,
                        install_prerequisites_hook=install_prerequisites_hook,
                        compiler_version="Visual Studio 17 2022")
obj.run()