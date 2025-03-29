import subprocess
import sys
import os
import logging
import shutil

# Assume assemblage CustomWindowsBuild and cmd_with_output exist
# If cmd_with_output is not available, define a placeholder:
try:
    from assemblage.worker.build_method import cmd_with_output
except ImportError:
    print("Warning: assemblage.worker.build_method not found. Using subprocess fallback for cmd_with_output.")
    def cmd_with_output(command, platform="windows", cwd=None, timelimit=None, shell=True):
        print(f"Executing: {command} in {cwd}")
        try:
            # On Windows, shell=True is often needed for complex commands with &&
            # Use a timeout if provided
            result = subprocess.run(command, cwd=cwd, shell=shell, check=True, 
                                    capture_output=True, text=True, timeout=timelimit)
            print("STDOUT:\n", result.stdout)
            print("STDERR:\n", result.stderr)
            return result.returncode == 0 # Return True on success
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {command}")
            print("Return Code:", e.returncode)
            print("STDOUT:\n", e.stdout)
            print("STDERR:\n", e.stderr)
            return False # Return False on failure
        except subprocess.TimeoutExpired as e:
            print(f"Command timed out after {timelimit} seconds: {command}")
            print("STDOUT:\n", e.stdout)
            print("STDERR:\n", e.stderr)
            return False # Return False on timeout
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

try:
    from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild
except ImportError:
    print("Warning: assemblage.worker.customize_strategies.custom_windows_build not found. Using placeholder.")
    # Define a placeholder class that mimics the expected structure
    class CustomWindowsBuild:
        def __init__(self, clone_dir, clone_flags, collect_dir, source_dir, build_dir,
                     project_git_url, optimization, build_mode, arch, tags,
                     build_hook, install_prerequisites_hook, compiler_version):
            self.clone_dir = clone_dir
            self.clone_flags = clone_flags
            self.collect_dir = collect_dir
            self.source_dir = source_dir
            self.build_dir = build_dir # This will be the *base* build dir
            self.project_git_url = project_git_url
            # These might not be directly used if build_hook handles everything
            self.optimization = optimization
            self.build_mode = build_mode
            self.arch = arch
            self.tags = tags # List of tags to iterate over
            self.build_hook = build_hook
            self.install_prerequisites_hook = install_prerequisites_hook
            self.compiler_version = compiler_version
            self.current_tag = None
            self.current_config = None

        def setup_build_environment(self, tag, config):
            """Sets up specific directories for the current tag and config."""
            self.current_tag = tag
            self.current_config = config
            # --- Crucial: Create unique build and collection paths ---
            self.specific_build_dir = os.path.join(self.build_dir, tag, config['name'])
            self.specific_collect_dir = os.path.join(self.collect_dir, tag, config['name'])
            os.makedirs(self.specific_build_dir, exist_ok=True)
            os.makedirs(self.specific_collect_dir, exist_ok=True)
            logging.info(f"Set build directory: {self.specific_build_dir}")
            logging.info(f"Set collect directory: {self.specific_collect_dir}")
            
            # Simulate Git checkout (in a real scenario, this would happen before build)
            # For this placeholder, we assume the source is already at clone_dir
            logging.info(f"Checking out tag: {tag} (simulation)")
            # cmd_with_output(f"git checkout {tag}", cwd=self.clone_dir) # Real command

        def collect_artifacts(self):
            """Collects build artifacts."""
            logging.info(f"Collecting artifacts for {self.current_tag} / {self.current_config['name']}")
            # Determine source of artifacts (usually Release or Debug subdir)
            artifact_src_dir = os.path.join(self.clone_dir, "src", "tools", "msvc", self.current_config['output_subdir'])
            
            if os.path.isdir(artifact_src_dir):
                logging.info(f"Searching for artifacts in: {artifact_src_dir}")
                # Copy relevant files (e.g., *.exe, *.dll, *.pdb)
                for item in os.listdir(artifact_src_dir):
                    s = os.path.join(artifact_src_dir, item)
                    d = os.path.join(self.specific_collect_dir, item)
                    if item.endswith(('.exe', '.dll', '.pdb')):
                         if os.path.isfile(s):
                            logging.info(f"Copying {s} to {d}")
                            try:
                                shutil.copy2(s, d) # copy2 preserves metadata
                            except Exception as e:
                                logging.error(f"Failed to copy {s}: {e}")
                         elif os.path.isdir(s):
                             # Optionally copy directories if needed
                             pass
            else:
                 logging.warning(f"Artifact source directory not found: {artifact_src_dir}")

        def run(self, tag, config):
            """Simulates the build process for a specific tag and config."""
            logging.info(f"--- Starting build for Tag: {tag}, Config: {config['name']} ---")
            try:
                self.setup_build_environment(tag, config)

                # Call prerequisites hook (if defined) - should ideally run only once overall
                # if self.install_prerequisites_hook:
                #    self.install_prerequisites_hook()

                # Call the actual build hook
                if self.build_hook:
                    build_success = self.build_hook(
                        build_dir=self.specific_build_dir, # Pass specific build dir
                        clone_dir=self.clone_dir,
                        config=config, # Pass the whole config dict
                        arch=self.arch,
                        vcvarsall_loc=f"\"C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\"" # Example path
                    )
                    if not build_success:
                         raise Exception("Build hook reported failure.")
                else:
                    logging.warning("No build_hook defined.")
                    build_success = False # Treat as failure if no hook

                # Collect artifacts if build succeeded
                if build_success:
                    self.collect_artifacts()
                else:
                    logging.error(f"Build failed for {tag} / {config['name']}. Skipping artifact collection.")

                logging.info(f"--- Finished build for Tag: {tag}, Config: {config['name']} ---")
                return build_success

            except Exception as e:
                logging.error(f"Build process failed for Tag: {tag}, Config: {config['name']}: {e}", exc_info=True)
                return False


# --- Configuration ---
LOG_FILE = 'postgres_build.log'
BASE_CLONE_DIR = 'C:\\Postgresql_Build\\postgres' # Base source dir
BASE_BUILD_DIR = 'C:\\Postgresql_Build\\build'   # Base dir for intermediate build files
COLLECT_DIR = "C:\\Postgresql_Build\\Binaries" # Final artifact collection base dir
PROJECT_GIT_URL = 'https://github.com/postgres/postgres'
# Specify the tags you want to build
POSTGRES_TAGS = ['REL_16_2', 'REL_16_3'] # Example tags
VCVARSALL_PATH = "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat" # Adjust if needed
MINGW_BIN_PATH = 'C:\\MinGW\\msys\\1.0\\bin' # Adjust if needed
TARGET_ARCH = 'x64' # Or 'x86'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE,
                    filemode='w')
# Also log to console
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


# --- Build Configurations Definition ---
# Customize optimization and security flags as needed.
# /Zi : Generate PDB
# /DEBUG : Linker flag for debug info
# /O1 : Minimize size
# /O2 : Maximize speed
# /Ox : Full optimization (/O2 /Ob2 /Oi /Ot /Oy /GL)
# /Od : Disable optimization (good for debugging)
# /GS : Buffer security check (usually default)
# /DYNAMICBASE : ASLR (usually default)
# /NXCOMPAT : DEP (usually default)
# /guard:cf : Control Flow Guard

BUILD_CONFIGURATIONS = [
    {
        'name': 'Debug_Default',
        'build_mode': 'debug', # Passed to build.bat as DEBUG=1
        'optimization': '', # Debug mode usually means /Od implicitly
        'security_flags': '/GS /guard:cf', # Add desired flags
        'add_debug_flags': True, # Let DEBUG=1 handle it mostly
        'output_subdir': 'Debug' # Subdir where artifacts are expected
    },
    {
        'name': 'Release_Default',
        'build_mode': 'release', # Passed to build.bat (no DEBUG=1)
        'optimization': '/O2', # Standard release optimization
        'security_flags': '/GS /DYNAMICBASE /NXCOMPAT /guard:cf',
        'add_debug_flags': False,
        'output_subdir': 'Release'
    },
    {
        'name': 'Release_WithDebug', # Release build with PDBs
        'build_mode': 'release',
        'optimization': '/O2',
        'security_flags': '/GS /DYNAMICBASE /NXCOMPAT /guard:cf',
        'add_debug_flags': True, # Manually add /Zi and /DEBUG
        'output_subdir': 'Release' # Still outputs to Release dir typically
    },
    {
        'name': 'Release_OptimizeSize',
        'build_mode': 'release',
        'optimization': '/O1',
        'security_flags': '/GS /DYNAMICBASE /NXCOMPAT /guard:cf',
        'add_debug_flags': False,
        'output_subdir': 'Release'
    },
    {
        'name': 'Release_FullOptimize',
        'build_mode': 'release',
        'optimization': '/Ox /GL', # Full optimization + Link Time Code Gen
        'security_flags': '/GS /DYNAMICBASE /NXCOMPAT /guard:cf',
        'add_debug_flags': False, # Add /Zi /DEBUG here if you want PDBs for this too
        'output_subdir': 'Release'
    },
    # Add up to 10 configurations as needed...
    # {
    #     'name': 'Debug_Optimized', # A debug build with some optimizations? Less common.
    #     'build_mode': 'debug',
    #     'optimization': '/O1', # Example
    #     'security_flags': '/GS /guard:cf',
    #     'add_debug_flags': True,
    #     'output_subdir': 'Debug'
    # },
]

# --- Hooks ---

def install_prerequisites_hook():
    """Placeholder for installing prerequisites like Perl."""
    logging.info("Running prerequisite installation hook...")
    # Add commands to install ActiveState Perl or ensure it's in PATH
    # Example (manual check):
    try:
        subprocess.run(['perl', '--version'], check=True, capture_output=True)
        logging.info("Perl found.")
    except FileNotFoundError:
        logging.error("Perl not found in PATH. Please install ActiveState Perl or ensure MinGW/MSYS Perl is available.")
        # Add installation commands here if desired
        # e.g., using PowerShell to run the ActiveState installer
        return False # Indicate failure
    logging.info("Prerequisites check/install done.")
    return True # Indicate success


def modify_config_pl_once(clone_dir, mingw_path):
    """Adds the MinGW path to src/tools/msvc/config.pl if not already present."""
    config_file_path = os.path.join(clone_dir, "src", "tools", "msvc", "config.pl")
    add_mingw_line = f"$ENV{{'PATH'}} = $ENV{{'PATH'}} . ';{mingw_path}';"
    
    if not os.path.exists(config_file_path):
        logging.error(f"Config file not found: {config_file_path}")
        return False

    try:
        with open(config_file_path, 'r') as file:
            content = file.read()
        
        if add_mingw_line in content:
            logging.info(f"MinGW path already present in {config_file_path}")
            return True
        else:
            logging.info(f"Adding MinGW path to {config_file_path}")
            with open(config_file_path, 'a') as file:
                file.write('\n' + add_mingw_line + '\n')
            logging.info("Added MinGW environment vars to config.pl")
            return True
            
    except Exception as e:
        logging.error(f"Failed to modify {config_file_path}: {e}")
        return False

# --- Build Hook ---
def build_hook(build_dir, # Note: This might be the specific dir now
               clone_dir,
               config,    # Current configuration dictionary
               arch,
               vcvarsall_loc):
    """Builds PostgreSQL using build.bat with specific configuration flags."""
    logging.info(f"Starting build for config: {config['name']}")
    
    build_script_path = os.path.join(clone_dir, "src", "tools", "msvc")
    build_command_parts = [
        f'cd /d "{build_script_path}"', # Ensure we are in the correct directory
        f'"{vcvarsall_loc}" {arch}' # Set up MSVC environment
    ]

    # --- Construct CFLAGS and LDFLAGS ---
    cflags = []
    ldflags = []

    if config['optimization']:
        cflags.append(config['optimization'])
        # Some optimizations require linker flags (like /GL -> /LTCG)
        if "/GL" in config['optimization']:
            ldflags.append("/LTCG")

    if config['security_flags']:
        # Security flags often apply to both compiler and linker
        flags = config['security_flags'].split()
        cflags.extend(flags)
        ldflags.extend(flags) # Add security flags to linker too where applicable

    if config['add_debug_flags']:
        cflags.append("/Zi") # Generate PDB info
        ldflags.append("/DEBUG") # Link with debug info

    # Clean flags (remove duplicates, handle potential conflicts if necessary)
    cflags = list(dict.fromkeys(cflags)) # Simple way to remove duplicates, preserves order
    ldflags = list(dict.fromkeys(ldflags))

    # --- Construct build.bat command ---
    build_bat_cmd = ["build.bat"]
    if config['build_mode'] == 'debug':
        build_bat_cmd.append("DEBUG=1")

    # Pass CFLAGS and LDFLAGS - quoting is important for spaces
    if cflags:
        build_bat_cmd.append(f'CFLAGS="{" ".join(cflags)}"')
    if ldflags:
        build_bat_cmd.append(f'LDFLAGS="{" ".join(ldflags)}"')
        
    # Add the build.bat command part
    build_command_parts.append(" ".join(build_bat_cmd))

    # Combine parts with '&&' for sequential execution in one shell
    full_command = " && ".join(build_command_parts)
    
    logging.info(f"Executing build command: {full_command}")

    # Execute the command
    success = cmd_with_output(full_command, platform="windows", cwd=clone_dir, timelimit=3600) # Increased timeout to 1hr

    if success:
        logging.info(f"Build successful for config: {config['name']}")
    else:
        logging.error(f"Build failed for config: {config['name']}")

    return success


# --- Main Execution Logic ---

def main():
    logging.info("Starting PostgreSQL build process...")

    # 1. Ensure base clone directory exists (or clone if needed)
    if not os.path.isdir(os.path.join(BASE_CLONE_DIR, '.git')):
        logging.info(f"Cloning {PROJECT_GIT_URL} into {BASE_CLONE_DIR}...")
        clone_success = cmd_with_output(f'git clone "{PROJECT_GIT_URL}" "{BASE_CLONE_DIR}"', cwd=".")
        if not clone_success:
            logging.error("Failed to clone repository. Exiting.")
            return
    else:
        logging.info(f"Using existing repository in {BASE_CLONE_DIR}")
        # Optionally run 'git fetch' or 'git pull' here
        cmd_with_output('git fetch --all --tags', cwd=BASE_CLONE_DIR)


    # 2. Install prerequisites (if needed) - Run once
    # if not install_prerequisites_hook():
    #     logging.error("Prerequisite installation failed. Exiting.")
    #     return
    logging.warning("Skipping prerequisite installation hook. Ensure Perl is available.")


    # 3. Modify config.pl (if needed) - Run once
    if not modify_config_pl_once(BASE_CLONE_DIR, MINGW_BIN_PATH):
         logging.error("Failed to modify config.pl. Exiting.")
         return

    # 4. Iterate through Tags and Configurations
    total_builds = len(POSTGRES_TAGS) * len(BUILD_CONFIGURATIONS)
    build_count = 0
    success_count = 0
    failed_builds = []

    for tag in POSTGRES_TAGS:
        logging.info(f"Processing Tag: {tag}")
        # Checkout the specific tag - do this *outside* the config loop
        checkout_success = cmd_with_output(f'git checkout {tag}', cwd=BASE_CLONE_DIR)
        if not checkout_success:
            logging.error(f"Failed to checkout tag {tag}. Skipping builds for this tag.")
            continue # Skip to the next tag

        # Clean previous build results for this tag (optional but recommended)
        logging.info(f"Cleaning previous build artifacts for tag {tag}...")
        clean_script_path = os.path.join(BASE_CLONE_DIR, "src", "tools", "msvc")
        clean_cmd = f'cd /d "{clean_script_path}" && "{VCVARSALL_PATH}" {TARGET_ARCH} && build.bat clean'
        cmd_with_output(clean_cmd, platform="windows", cwd=BASE_CLONE_DIR)


        for config in BUILD_CONFIGURATIONS:
            build_count += 1
            logging.info(f"--- Starting Build {build_count}/{total_builds}: Tag={tag}, Config={config['name']} ---")

            # Use the placeholder CustomWindowsBuild or the real one
            builder = CustomWindowsBuild(
                clone_dir=BASE_CLONE_DIR,
                clone_flags='', # Handled manually above
                collect_dir=COLLECT_DIR, # Base collection dir
                source_dir=os.path.join(BASE_CLONE_DIR, 'src'), # Example
                build_dir=BASE_BUILD_DIR, # Base build dir
                project_git_url=PROJECT_GIT_URL,
                # These might be less relevant now config dict is used
                optimization=config['optimization'],
                build_mode=config['build_mode'],
                arch=TARGET_ARCH,
                tags=[tag], # Pass only the current tag
                build_hook=build_hook,
                install_prerequisites_hook=None, # Run once outside
                compiler_version="Visual Studio 17 2022" # Example
            )

            # The run method now needs the tag and config to set up paths etc.
            # (Modified placeholder `run` method to accept these)
            try:
                build_successful = builder.run(tag=tag, config=config)
                if build_successful:
                    success_count += 1
                else:
                    failed_builds.append(f"{tag} / {config['name']}")
            except Exception as e:
                logging.error(f"Critical error during build for {tag} / {config['name']}: {e}", exc_info=True)
                failed_builds.append(f"{tag} / {config['name']}")

            logging.info(f"--- Finished Build {build_count}/{total_builds} ---")

    # 5. Summary
    logging.info("=" * 50)
    logging.info("Build Process Summary")
    logging.info(f"Total Builds Attempted: {build_count}")
    logging.info(f"Successful Builds: {success_count}")
    logging.info(f"Failed Builds: {len(failed_builds)}")
    if failed_builds:
        logging.warning("Failed Configurations:")
        for failed in failed_builds:
            logging.warning(f"  - {failed}")
    logging.info("=" * 50)

if __name__ == "__main__":
    main()
