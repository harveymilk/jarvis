import subprocess, os
import re


def download_repo(repo_url: str, output_dir: str, depth: int = 1):
    """
    Download a repository from a given URL to a specified output directory.

    Args:
        repo_url (str): The URL of the repository to download.
        output_dir (str): The directory to save the downloaded repository.
        depth (int): The depth of the repository to download.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    subprocess.run(["git", "clone", "--depth", str(depth), repo_url, output_dir])


def clean_readme(repo_dir: str):
    """
    Clean a README file by removing all code blocks and code snippets.
    """
    readme_path = os.path.join(repo_dir, "README.md")
    with open(readme_path, encoding="utf-8") as f:
        content = f.read()
    no_inline = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    no_images = re.sub(r'!\[.*?\]\(.*?\)', '', no_inline)
    no_urls = re.sub(r'http[s]?://\S+', '', no_images)
    no_badges = re.sub(r'!\[.*?(shields\.io|badge)\S*\).*', '', no_urls)
    # md_text = BeautifulSoup(no_badges, "lxml").get_text()
    print(no_badges)





if __name__ == "__main__":
    download_repo(
        "https://github.com/denizsafak/abogen.git",
        "downloaded_repos/abogen",
        1,
    )
    clean_readme("downloaded_repos/abogen")