from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='postgres.log',
                    filemode='w')

def install_prerequisites_hook(clone_dir):
    #Install activestate perl
    #    via https://docs.activestate.com/platform/state/install/

    install_activeperl_cmd = "& $([scriptblock]::Create((New-Object Net.WebClient).DownloadString('https://platform.activestate.com/dl/cli/install.ps1')))"
    run_powershell_cmd = f'powershell.exe -Command "{install_activeperl_cmd}"'
    install_perl_cmd = "state checkout ActiveState-Projects/ActiveState-Perl-5.36.0 . && state use ActiveState-Perl-5.36.0"
    cmd_with_output(run_powershell_cmd, clone_dir)
    cmd_with_output(install_perl_cmd, clone_dir)


    #Adding mingw binaries for building
    config_file = r"\src\tools\msvc\config.pl"
    file_path = os.path.join(clone_dir, config_file)
    add_mingw = "ENV{PATH}=$ENV{PATH} . ';C:\\MinGW\\msys\\1.0\\bin';"
    with open(file_path, 'a') as file:
        file.write(add_mingw + '\n')
    logging.info("Added mingw environment vars to config")

def build_hook(build_dir,
                        clone_dir,
                        build_mode,
                        arch,
                        optimization):
    #Build using build.bat
    cmd_with_output(f"cd src\\tools\\msvc\\ &&" +
                    f"vcvarsall.bat {arch} &&" +
                    f"build.bat", platform="windows", cwd=clone_dir)


obj = CustomWindowsBuild(clone_dir='C:\\Postgresql\\postgres',
                 clone_flags='',
                 collect_dir="C:\\Binaries",
                 source_dir='C:\\\Postgresql\\postgres\\src',
                 build_dir='C:\\Postgresql\\postgres\\Release',
                 project_git_url='https://github.com/postgres/postgres',
                 optimization='',
                 build_mode='release',
                 arch='x64',
                 tags=['REL_16_4'],
                 build_hook=build_hook,
                 install_prerequisites_hook=install_prerequisites_hook,
                 compiler_version="Visual Studio 15 2017")
obj.run()



'''
For Postgres
-  
git clone https://github.com/postgres/postgres
git checkout REL_16_4
 cd .\src\tools\msvc\
*edit config.pl and add* $ENV{PATH}=$ENV{PATH} . ';C:\MinGW\msys\1.0\bin';
vcvarsall.bat x64  
build.bat
cd ~/Debug or cd ~/Release

Need to check optimization options

'''