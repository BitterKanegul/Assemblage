from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='godot_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    # Python 3.6+ and SCons 3.1.2+ are required
    res = cmd_with_output("python -m pip install --upgrade scons", 
                         platform="windows", 
                         timelimit=300)
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building Godot...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Maps vcvars arch to scons arch
    arch_map = {
        'x64': 'x86_64',
        'x86': 'x86_32',
        'x64_arm64': 'arm64'
    }
    
    scons_arch = arch_map.get(arch, 'x86_64')
    
    # Build main editor
    editor_cmd = (
        f"{vcvarsall_loc} {arch} && "
        f"cd {clone_dir} && "
        f"scons platform=windows "
        f"target=editor "
        f"arch={scons_arch} "
        f"production={optimization} "
        f"debug_symbols=no "
    )
    
    if build_mode.lower() == 'debug':
        editor_cmd += "dev_build=yes "
    
    res = cmd_with_output(editor_cmd, platform="windows", cwd=clone_dir, timelimit=7200)
    
    # Build export templates
    template_modes = ['template_debug', 'template_release']
    
    for template_mode in template_modes:
        template_cmd = (
            f"{vcvarsall_loc} {arch} && "
            f"cd {clone_dir} && "
            f"scons platform=windows "
            f"target={template_mode} "
            f"arch={scons_arch} "
            f"production={optimization} "
            f"debug_symbols=no "
        )
        
        res = cmd_with_output(template_cmd, platform="windows", cwd=clone_dir, timelimit=7200)

arch = 'x64'
optimization = 'yes'  # Enable production optimizations

obj = CustomWindowsBuild(
    clone_dir='C:\\\\Godot\\',
    clone_flags='',
    collect_dir="C:\\Binaries",
    source_dir='C:\\\\Godot\\',
    build_dir='C:\\\\Godot\\bin\\',
    project_git_url='https://github.com/godotengine/godot.git',
    optimization=optimization,
    build_mode='Release',
    arch=arch,
    tags=['4.2.1-stable', '4.1.3-stable', '4.0.4-stable', '3.5.3-stable'],
    build_hook=build_hook,
    install_prerequisites_hook=install_prerequisites_hook,
    compiler_version="Visual Studio 17 2022"
)

obj.run()