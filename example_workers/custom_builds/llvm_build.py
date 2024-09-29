from assemblage.worker.build_method import cmd_with_output
import os
import logging

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='go_build.log',
                    filemode='w')

def install_prerequisites_hook():
    print("Installing prerequisites...")
    print("Done")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building LLVM...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    #Maps vcvars arch to cmake preset arch
    arch_map ={'x64': 'x64', 'x64_arm':'ARM', 'x64_arm64': 'ARM64', 'x86': 'x86'}


    res = cmd_with_output(f"{vcvarsall_loc} {arch} &&" +
                          f"cd llvm && mkdir llvm-build-2 && cd llvm-build-2 &&" +
                          f"dir && " +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" -DCMAKE_INSTALL_PREFIX=C:\\\\LLVM\\Binaries"+
                          f" -DCMAKE_PREFIX_PATH= C:\\\\LLVM\\Binaries -DLLVM_ENABLE_ZLIB=OFF -DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DLLVM_USE_CRT_DEBUG=MTd -DLLVM_USE_CRT_RELEASE=MT -DLLVM_ENABLE_LIBXML2=OFF && " +
                          f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj && cd .. && " +
                          f"cd ../lld && mkdir lld-build && cd lld-build && " +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" -DCMAKE_INSTALL_PREFIX=C:\\\\LLVM\\Binaries " +
                          f" -DCMAKE_PREFIX_PATH= C:\\\\LLVM\\Binaries -DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DLLVM_USE_CRT_DEBUG=MTd -DLLVM_USE_CRT_RELEASE=MT && cd .. && " +
                          f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj && " +
                          f"cd clang && mkdir clang-build && cd clang-build && " +
                          f"cmake .. -Thost=x64 -A {arch} -G \"Visual Studio 17 2022\" -DCMAKE_INSTALL_PREFIX=C:\\\\LLVM\\Binaries " +
                          f" -DCMAKE_PREFIX_PATH= C:\\\\LLVM\\Binaries -DCMAKE_BUILD_TYPE={build_mode} " +
                          f"-DLLVM_USE_CRT_DEBUG=MTd -DLLVM_USE_CRT_RELEASE=MT && cd .. && " +
                          f"msbuild /m -p:Configuration={build_mode} INSTALL.vcxproj "
                          , platform="windows", cwd=clone_dir, timelimit=600000)
arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\LLVM\\llvm-project',
                         clone_flags=' --config core.autocrlf=false',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\LLVM\\llvm-project',
                         build_dir=f'C:\\\\LLVM\\Binaries',
                         project_git_url='https://github.com/llvm/llvm-project.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['llvmorg-19.1.0-rc4','llvmorg-17.0.6','llvmorg-16.0.6','llvmorg-14.0.6'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()

'''
LLVM build example
via https://github.com/ziglang/zig/wiki/How-to-build-LLVM,-libclang,-and-liblld-from-source#windows

Download llvm, clang, and lld The downloads from llvm lead to the github release pages, where the source's will be listed as : llvm-19.X.X.src.tar.xz, clang-19.X.X.src.tar.xz, lld-19.X.X.src.tar.xz. Unzip each to their own directory. Ensure no directories have spaces in them. For example:

C:\Users\Andy\llvm-19.1.0.src
C:\Users\Andy\clang-19.1.0.src
C:\Users\Andy\lld-19.1.0.src

Install Python 3.9.4. Tick the box to add python to your PATH environment variable.
Using the start menu, run x64 Native Tools Command Prompt for VS 2019 and execute these commands, replacing C:\Users\Andy with the correct value. Here is listed a brief explanation of each of the CMake parameters we pass when configuring the build

-Thost=x64 : Sets the windows toolset to use 64 bit mode.
-A x64 : Make the build target 64 bit .
-G "Visual Studio 16 2019" : Specifies to generate a 2019 Visual Studio project, the best supported version.
-DCMAKE_INSTALL_PREFIX="" : Path that llvm components will being installed into by the install project.
-DCMAKE_PREFIX_PATH="" : Path that CMake will look into first when trying to locate dependencies, should be the same place as the install prefix. This will ensure that clang and lld will use your newly built llvm libraries.
-DLLVM_ENABLE_ZLIB=OFF : Don't build llvm with ZLib support as it's not required and will disrupt the target dependencies for components linking against llvm. This only has to be passed when building llvm, as this option will be saved into the config headers.
-DCMAKE_BUILD_TYPE=Release : Build llvm and components in release mode.
-DCMAKE_BUILD_TYPE=Debug : Build llvm and components in debug mode.
-DLLVM_USE_CRT_RELEASE=MT : Which C runtime should llvm use during release builds.
-DLLVM_USE_CRT_DEBUG=MTd : Make llvm use the debug version of the runtime in debug builds.


Release mode:
mkdir C:\Users\Andy\llvm-19.1.0.src\build-release
cd C:\Users\Andy\llvm-19.1.0.src\build-release
"c:\Program Files\CMake\bin\cmake.exe" .. -Thost=x64 -G "Visual Studio 16 2019" -A x64 -DCMAKE_INSTALL_PREFIX=C:\Users\Andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-release-mt -DCMAKE_PREFIX_PATH=C:\Users\Andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-release-mt -
DLLVM_ENABLE_ZLIB=OFF -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_LIBXML2=OFF -DLLVM_USE_CRT_RELEASE=MT
msbuild /m -p:Configuration=Release INSTALL.vcxproj

Debug mode:
mkdir C:\Users\Andy\llvm-19.1.0.src\build-debug
cd C:\Users\Andy\llvm-19.1.0.src\build-debug
"c:\Program Files\CMake\bin\cmake.exe" .. -Thost=x64 -G "Visual Studio 16 2019" -A x64 -DCMAKE_INSTALL_PREFIX=C:\Users\andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-debug -
DLLVM_ENABLE_ZLIB=OFF -DCMAKE_PREFIX_PATH=C:\Users\andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-debug -DCMAKE_BUILD_TYPE=Debug -DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD="AVR" -DLLVM_ENABLE_LIBXML2=OFF -DLLVM_USE_CRT_DEBUG=MTd
msbuild /m INSTALL.vcxproj

LLD:

mkdir C:\Users\Andy\lld-19.1.0.src\build-release
cd C:\Users\Andy\lld-19.1.0.src\build-release
"c:\Program Files\CMake\bin\cmake.exe" .. -Thost=x64 -G "Visual Studio 16 2019" -A x64 -DCMAKE_INSTALL_PREFIX=C:\Users\Andy\llvm+clang+lld-14.0.6-x86_64-windows-msvc-release-mt -DCMAKE_PREFIX_PATH=C:\Users\Andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-release-mt -DCMAKE_BUILD_TYPE=Release -DLLVM_USE_CRT_RELEASE=MT
msbuild /m -p:Configuration=Release INSTALL.vcxproj


mkdir C:\Users\Andy\lld-19.1.0.src\build-debug
cd C:\Users\Andy\lld-19.1.0.src\build-debug
"c:\Program Files\CMake\bin\cmake.exe" .. -Thost=x64 -G "Visual Studio 16 2019" -A x64 -DCMAKE_INSTALL_PREFIX=C:\Users\andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-debug -DCMAKE_PREFIX_PATH=C:\Users\andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-debug -DCMAKE_BUILD_TYPE=Debug -DLLVM_USE_CRT_DEBUG=MTd
msbuild /m INSTALL.vcxproj


Clang:

mkdir C:\Users\Andy\clang-19.1.0.src\build-release
cd C:\Users\Andy\clang-19.1.0.src\build-release
"c:\Program Files\CMake\bin\cmake.exe" .. -Thost=x64 -G "Visual Studio 16 2019" -A x64 -DCMAKE_INSTALL_PREFIX=C:\Users\Andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-release-mt -DCMAKE_PREFIX_PATH=C:\Users\Andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-release-mt -DCMAKE_BUILD_TYPE=Release -DLLVM_USE_CRT_RELEASE=MT
msbuild /m -p:Configuration=Release INSTALL.vcxproj

mkdir C:\Users\Andy\clang-19.1.0.src\build-debug
cd C:\Users\Andy\clang-19.1.0.src\build-debug
"c:\Program Files\CMake\bin\cmake.exe" .. -Thost=x64 -G "Visual Studio 16 2019" -A x64 -DCMAKE_INSTALL_PREFIX=C:\Users\andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-debug -DCMAKE_PREFIX_PATH=C:\Users\andy\llvm+clang+lld-19.1.0-x86_64-windows-msvc-debug -DCMAKE_BUILD_TYPE=Debug -DLLVM_USE_CRT_DEBUG=MTd
msbuild /m INSTALL.vcxproj



git clone --config core.autocrlf=false https://github.com/llvm/llvm-project.git



'''