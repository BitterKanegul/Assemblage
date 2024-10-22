from assemblage.worker.build_method import cmd_with_output
import os
import logging
import shutil
import urllib.request
import ssl
import hashlib

from assemblage.worker.customize_strategies.custom_windows_build import CustomWindowsBuild

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='nginx_build.log',
                    filemode='w')

def download_file(url, filename, expected_sha256=None):
    """
    Download a file from URL with progress indicator and optional SHA256 verification
    """
    logging.info(f"Downloading {filename} from {url}")
    
    # Create SSL context that doesn't verify certificates
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(url, context=ctx) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(filename, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    f.write(buffer)
                    
                    # Calculate download percentage
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading {filename}: {percent:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            
            # Verify SHA256 if provided
            if expected_sha256:
                sha256_hash = hashlib.sha256()
                with open(filename, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                if sha256_hash.hexdigest() != expected_sha256:
                    raise Exception(f"SHA256 verification failed for {filename}")
                
            logging.info(f"Successfully downloaded {filename}")
            return True
    except Exception as e:
        logging.error(f"Error downloading {filename}: {str(e)}")
        return False

def install_prerequisites_hook():
    print("Installing prerequisites...")
    
    # Define required files with their URLs and SHA256 hashes
    required_files = {
        'pcre2-10.39.tar.gz': {
            'url': 'https://github.com/PCRE2Project/pcre2/releases/download/pcre2-10.39/pcre2-10.39.tar.gz',
            'sha256': '0f03caf57f81d9ff362ac28cd389c055ec2bf0678d277349a1a4bee00ad6d440'
        },
        'zlib-1.3.1.tar.gz': {
            'url': 'https://www.zlib.net/zlib-1.3.1.tar.gz',
            'sha256': '9a93b2b7dfdac77ceba5a558a580e74667dd6fede4585b91eefb60f03b72df23'
        },
        'openssl-3.0.14.tar.gz': {
            'url': 'https://www.openssl.org/source/openssl-3.0.14.tar.gz',
            'sha256': '61b9ed94647deeee9ce956c02e63463b3a868957038550dad40f6c593267d392'
        }
    }
    
    # Download missing files
    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)
    
    for file, info in required_files.items():
        file_path = os.path.join(downloads_dir, file)
        if not os.path.exists(file_path):
            print(f"Downloading {file}...")
            success = download_file(info['url'], file_path, info['sha256'])
            if not success:
                print(f"Failed to download {file}. Please download manually from {info['url']}")
                continue
        else:
            print(f"{file} already exists, skipping download")
    
    print("Prerequisite installation completed")

def build_hook(build_dir,
               clone_dir,
               build_mode,
               arch,
               optimization):
    logging.info("Building nginx...")
    vcvarsall_loc = "\"C:\\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat\""
    
    # Create build directories
    os.makedirs(os.path.join(clone_dir, "objs"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "objs", "lib"), exist_ok=True)
    
    # Copy dependency files from downloads directory to lib directory
    downloads_dir = "downloads"
    lib_dir = os.path.join(clone_dir, "objs", "lib")
    deps = ['pcre2-10.39.tar.gz', 'zlib-1.3.1.tar.gz', 'openssl-3.0.14.tar.gz']
    
    for dep in deps:
        src_path = os.path.join(downloads_dir, dep)
        dst_path = os.path.join(lib_dir, dep)
        if os.path.exists(src_path):
            shutil.copy(src_path, dst_path)
            logging.info(f"Copied {dep} to {lib_dir}")
        else:
            logging.error(f"Missing dependency: {dep}")
            raise Exception(f"Required dependency {dep} not found in downloads directory")
    
    # Create necessary directories for nginx
    os.makedirs(os.path.join(clone_dir, "temp", "client_body_temp"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "temp", "proxy_temp"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "temp", "fastcgi_temp"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "temp", "scgi_temp"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "temp", "uwsgi_temp"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(clone_dir, "conf"), exist_ok=True)
    
    # Build command
    build_cmd = (
        f"{vcvarsall_loc} {arch} && "
        f"cd {clone_dir} && "
        f"bash -c '"
        f"cd objs/lib && "
        f"tar -xzf pcre2-10.39.tar.gz && "
        f"tar -xzf zlib-1.3.1.tar.gz && "
        f"tar -xzf openssl-3.0.14.tar.gz && "
        f"cd ../.. && "
        f"auto/configure "
        f"--with-cc=cl "
        f"--with-debug "
        f"--prefix= "
        f"--conf-path=conf/nginx.conf "
        f"--pid-path=logs/nginx.pid "
        f"--http-log-path=logs/access.log "
        f"--error-log-path=logs/error.log "
        f"--sbin-path=nginx.exe "
        f"--http-client-body-temp-path=temp/client_body_temp "
        f"--http-proxy-temp-path=temp/proxy_temp "
        f"--http-fastcgi-temp-path=temp/fastcgi_temp "
        f"--http-scgi-temp-path=temp/scgi_temp "
        f"--http-uwsgi-temp-path=temp/uwsgi_temp "
        f"--with-cc-opt=-DFD_SETSIZE=1024 "
        f"--with-pcre=objs/lib/pcre2-10.39 "
        f"--with-zlib=objs/lib/zlib-1.3.1 "
        f"--with-openssl=objs/lib/openssl-3.0.14 "
        f"--with-openssl-opt=no-asm "
        f"--with-http_ssl_module && "
        f"nmake'"
    )
    
    res = cmd_with_output(build_cmd, platform="windows", cwd=clone_dir, timelimit=600000)

arch = 'x64'

obj = CustomWindowsBuild(clone_dir='C:\\\\nginx\\',
                         clone_flags='',
                         collect_dir="C:\\Binaries",
                         source_dir='C:\\\\nginx\\',
                         build_dir='C:\\\\nginx\\objs\\',
                         project_git_url='https://github.com/nginx/nginx.git',
                         optimization='',
                         build_mode='Debug',
                         arch=arch,
                         tags=['release-1.24.0', 'release-1.22.1', 'release-1.20.2', 'release-1.18.0'],
                         build_hook=build_hook,
                         install_prerequisites_hook=install_prerequisites_hook,
                         compiler_version="Visual Studio 17 2022")
obj.run()