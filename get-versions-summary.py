import subprocess
from datetime import datetime
import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def run_git_command(cmd, repo_path):
    """
    Run a git command and print its output.
    
    Args:
        cmd (list): Command and arguments
        repo_path (str): Repository path for context
    
    Returns:
        subprocess.CompletedProcess
    """
    print(f"\nExecuting in {repo_path}:")
    print(f"$ git {' '.join(cmd[1:])}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    if result.stdout:
        print("Output:")
        print(result.stdout.rstrip())
    if result.stderr:
        print("Stderr:")
        print(result.stderr.rstrip())
    
    return result

def get_repo_tag_dates(repo_path='.') -> List[Tuple[str, datetime]]:
    """
    Get all tags and their last commit dates from a git repository.
    
    Args:
        repo_path (str): Path to the git repository
        
    Returns:
        list: List of tuples containing (tag_name, commit_date)
    """
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        tags_process = run_git_command(['git', 'tag'], repo_path)
        tags = tags_process.stdout.strip().split('\n')
        
        tag_dates = []
        for tag in tags:
            if not tag:  # Skip if empty tag
                continue
                
            print(f"\nProcessing tag: {tag}")
            
            hash_process = run_git_command(
                ['git', 'rev-list', '-n', '1', tag],
                repo_path
            )
            commit_hash = hash_process.stdout.strip()
            
            date_process = run_git_command(
                ['git', 'show', '-s', '--format=%ci', commit_hash],
                repo_path
            )
            commit_date = date_process.stdout.strip()
            
            date_obj = datetime.strptime(commit_date, '%Y-%m-%d %H:%M:%S %z')
            tag_dates.append((tag, date_obj))
        
        return sorted(tag_dates, key=lambda x: x[1], reverse=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command in {repo_path}: {e}")
        print(f"Command output: {e.output}")
        return []
    except Exception as e:
        print(f"An error occurred in {repo_path}: {e}")
        return []
    finally:
        os.chdir(original_dir)

def organize_tags_by_year(tag_dates: List[Tuple[str, datetime]]) -> Dict[int, List[dict]]:
    """
    Organize tags by year and format them for output.
    
    Args:
        tag_dates: List of (tag, datetime) tuples
    
    Returns:
        Dictionary with years as keys and list of tag information as values
    """
    tags_by_year = defaultdict(list)
    
    for tag, date in tag_dates:
        year = date.year
        tags_by_year[year].append({
            "tag": tag,
            "date": date.strftime('%Y-%m-%d %H:%M:%S %z')
        })
    
    return dict(sorted(tags_by_year.items(), reverse=True))

def process_repositories(base_folder, output_file):
    """
    Process all git repositories in the specified folder and save results to a file.
    """
    base_path = Path(base_folder)
    results = {}
    summary_stats = defaultdict(lambda: defaultdict(int))
    
    # Find all potential git repositories
    for item in base_path.iterdir():
        if item.is_dir() and (item / '.git').exists():
            print(f"\n{'='*60}")
            print(f"Processing repository: {item.name}")
            print(f"{'='*60}")
            
            tag_dates = get_repo_tag_dates(str(item))
            tags_by_year = organize_tags_by_year(tag_dates)
            
            # Update summary statistics
            for year, tags in tags_by_year.items():
                summary_stats[item.name][year] = len(tags)
            
            results[item.name] = tags_by_year

    # Save results
    file_extension = Path(output_file).suffix.lower()
    print(f"\nSaving results to {output_file}")
    
    if file_extension == '.json':
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    else:
        with open(output_file, 'w') as f:
            f.write("Repository Tags by Year\n")
            f.write("=" * 50 + "\n\n")
            
            for repo_name, years_data in results.items():
                f.write(f"\nRepository: {repo_name}\n")
                f.write("-" * 50 + "\n")
                
                if not years_data:
                    f.write("No tags found\n")
                    continue
                
                for year, tags in years_data.items():
                    f.write(f"\nYear {year} ({len(tags)} tags):\n")
                    # Show first 4 tags for each year
                    for tag_info in tags[:4]:
                        f.write(f"  Tag: {tag_info['tag']:<20} Last commit: {tag_info['date']}\n")
                    if len(tags) > 4:
                        f.write(f"  ... and {len(tags) - 4} more tags\n")
                
                f.write("\n")
            
            # Write summary section
            f.write("\nSummary Statistics\n")
            f.write("=" * 50 + "\n\n")
            
            for repo_name, year_stats in summary_stats.items():
                f.write(f"\nRepository: {repo_name}\n")
                f.write("-" * 30 + "\n")
                total_tags = sum(year_stats.values())
                f.write(f"Total tags: {total_tags}\n")
                for year, count in sorted(year_stats.items(), reverse=True):
                    f.write(f"  {year}: {count} tags ({(count/total_tags)*100:.1f}%)\n")
    
    print(f"Results saved successfully to {output_file}")
    
    # Print summary to console
    print("\nSummary Statistics:")
    print("=" * 50)
    for repo_name, year_stats in summary_stats.items():
        print(f"\nRepository: {repo_name}")
        print("-" * 30)
        total_tags = sum(year_stats.values())
        print(f"Total tags: {total_tags}")
        for year, count in sorted(year_stats.items(), reverse=True):
            print(f"  {year}: {count} tags ({(count/total_tags)*100:.1f}%)")

if __name__ == "__main__":
    base_folder = input("Enter folder containing repositories (or press Enter for current directory): ").strip() or '.'
    output_file = input("Enter output file path (e.g., 'output.txt' or 'output.json'): ").strip() or 'repo_tags2.txt'
    
    print(f"\nProcessing repositories in {base_folder}...")
    process_repositories(base_folder, output_file)
    print("\nDone!")