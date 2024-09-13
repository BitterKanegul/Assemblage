
from assemblage.worker.build_method_new import post_processing_pdb
import os
from git import Repo
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='custom_windows_build.log',
                    filemode='w')

"""
Custom post build hooks, 
 - post_processing_pdb seems to be the standard one
- Also need a custom preprocessing hook for changing the optimization flags.

"""
class CustomWindowsBuild:
    def __init__(self,
                 clone_dir,
                 clone_flags,
                 collect_dir,
                 source_dir,
                 build_dir,
                 project_git_url,
                 optimization,
                 build_mode,
                 arch,
                 tags,
                 build_hook,
                 install_prerequisites_hook,
                 compiler_version="Visual Studio 15 2017",
                 post_build_hook=post_processing_pdb
                 ):
        logging.info("Initialized")
        self.clone_dir = clone_dir
        self.clone_flags = clone_flags
        self.collect_dir = collect_dir
        self.source_dir = source_dir
        self.build_dir = build_dir
        self.project_git_url = project_git_url
        self.optimization = optimization
        self.build_mode = build_mode
        self.arch = arch
        self.tags = tags
        self.compiler_version = compiler_version
        
        #Hooks to perform different build stages
        self.post_build_hook = post_build_hook
        self.build_hook = build_hook
        self.install_prerequisites_hook = install_prerequisites_hook


    """
    Clone the repository from the URL for each tag/ version
    """

    def clone_repo(self):
        if not os.path.isdir(self.clone_dir):
            os.system(f"git clone {self.clone_flags} {self.project_git_url} {self.clone_dir})")


    """
    Run the worker to clone repos, set the different flags and tags and then run the builds
    """

    def run(self):
        logging.info("Cloning repository from URL")
        self.clone_repo()

        logging.info("Installing prerequisites")
        self.install_prerequisites_hook()
        repo = Repo(self.clone_dir)
        for tag in self.tags:
            try:
                repo.git.checkout(tag, force=True)
            except Exception as e:
                logging.info("Tag not found %s, err %s", tag, str(e))
                continue
            logging.info("Tag found %s", tag)
            self.repo_current_commit_hash = tag + ":" + repo.head.commit.hexsha
            logging.info("Building %s at %s", self.repo_current_commit_hash, self.build_dir)
            self.build_hook(build_dir = self.build_dir,
                            clone_dir = self.clone_dir,
                            build_mode = self.build_mode,
                            arch = self.arch,
                            optimization = self.optimization
                            )
            self.post_build_hook(dest_binfolder=self.build_dir,
                                build_mode=self.build_mode,
                                library=self.arch,
                                repoinfo={"url": self.project_git_url, "updated_at": self.repo_current_commit_hash},
                                toolset=self.compiler_version,
                                optimization=self.optimization,
                                source_codedir=self.source_dir,
                                commit=self.repo_current_commit_hash,
                                movedir=f"{self.collect_dir}\\{self.project_git_url.split('/')[-1]}-{self.arch}-{self.optimization}-{tag}({self.compiler_version})"
                                )
