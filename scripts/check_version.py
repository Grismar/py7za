import re
import subprocess
import sys


def get_latest_git_tag():
    try:
        # Get the latest commit that has a tag
        rev = subprocess.check_output(
            ['git', 'rev-list', '--tags', '--max-count=1'],
            text=True
        ).strip()

        # Describe that commit to get the tag
        tag = subprocess.check_output(
            ['git', 'describe', '--tags', rev],
            text=True
        ).strip()

        return tag
    except subprocess.CalledProcessError as e:
        print("Git command failed:", e)
        return None


def get_changelog_version():
    with open('CHANGELOG.md') as f:
        text = f.read()
        xs = re.finditer('\[(.*?)]', text)
        assert next(xs).group(0), '[Unreleased]'
        return next(xs).group(1)


def main(arg_version):
    try:
        from py7za._version import __version__

        if arg_version != __version__:
            print("Version in code does not match stated version: {} != {}".format(__version__, arg_version))
            exit(1)

        changelog_version = get_changelog_version()
        if __version__ != changelog_version:
            print('Version does not match: {} != {}'.format(__version__, changelog_version))
            exit(1)

        latest_tag = get_latest_git_tag()
        if latest_tag is None:
            print('No git tag found')
            exit(1)
        if latest_tag == __version__:
            print('Current software version already tagged in Git repo: {}'.format(latest_tag))
            exit(1)
    except (ImportError, AssertionError, IOError) as e:
        print('Something went wrong. {}'.format(e))
        exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: check_version.py <version>')
        exit(1)
    main(sys.argv[1])
