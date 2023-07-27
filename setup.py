import platform
import os
import subprocess


def main():
    package_manager = determine_package_manager()
    update_system(package_manager)
    install_packages(package_manager)
    if ask_for_zsh():
        set_zsh_as_default()
    if ask_for_nerd_fonts():
        install_fonts()
    if ask_for_chezmoi():
        chezmoi_location = ask_chezmoi_location()
        github_username = input('Enter your GitHub username: ')
        install_chezmoi_and_dotfiles(github_username, chezmoi_location)
    if ask_for_flatpak():
        install_flatpaks()


def determine_package_manager():
    package_managers = {
        'ubuntu': {
            'package_manager': 'apt',
            'install_args': {
                'install',
                '-y'
            },
            'update_args': {
                'update'
            }
        },
        'fedora': {
            'package_manager': 'dnf',
            'install_args': {
                'install',
                '-y'
            },
            'update_args': {
                'update'
                '-y'
            }
        },
        'opensuse': {
            'package_manager': 'zypper',
            'install_args': {
                'in',
                '-y'
            },
            'update_args': {
                'dup',
                '-y'
            }
        },
        'arch': {
            'package_manager': 'pacman',
            'install_args': {
                '-S',
                '--noconfirm'
            },
            'update_args': {
                '-Syu',
                '--noconfirm'
            }
        }
    }

    try:
        for id in platform.freedesktop_os_release()['ID_LIKE'].split():
            if id in package_managers:
                return package_managers[id]

    except KeyError:
        print('Your distro is not supported')
        exit(1)


def update_system(package_manager):
    subprocess.call(['sudo', package_manager['package_manager'],
                    *package_manager['update_args']])
    if package_manager['package_manager'] == 'apt':
        subprocess.call(['sudo', 'apt', 'upgrade', '-y'])


def install_packages(package_manager):
    with open('packages.txt', 'r') as f:
        packages = f.read().splitlines()
        packages = ' '.join(packages)
    # for package in packages:
    command = ['sudo', package_manager['package_manager'], *package_manager['install_args'], packages]
    command = ' '.join(command).strip()
    os.system(command)


def ask_for_zsh():
    print('This requires to have zsh installed or have it in the packages.txt file')
    answer = input('Do you want to make zsh your default shell? y/n: ').lower()
    return True if answer == 'y' else False


def ask_for_nerd_fonts():
    print('This will download 1GB of fonts from ryanoasis/nerd-fonts github repo and install them')
    answer = input('Do you want to install nerd fonts? y/n: ').lower()
    return True if answer == 'y' else False


def set_zsh_as_default():
    os.system('chsh -s $(which zsh)')


def ask_for_chezmoi():
    print('You can install all your dotfiles using chezmoi')
    print('This requires you to have a public github repo called dotfiles with all your dotfiles in it uploaded using chezmoi')
    print('This will overwrite your current dotfiles')
    answer = input(
        'Do you want to install chezmoi and dotfiles? y/n: ').lower()
    return True if answer == 'y' or answer is None else False

def ask_chezmoi_location():
    print('Where do you want to install chezmoi?')
    print('Recommended is system wide install at /bin')
    print('But you can also install it in your home directory at ~/bin')
    answer = input('Enter location L if you want to install it locally')
    return '~/bin' if answer == 'L' else '/bin'

def ask_for_flatpak():
    print('Do you want to install flatpaks?')
    print('This requires you to have a file called flatpaks.txt in the root of your dotfiles repo')
    print('This file should contain a list of flatpaks you want to install')
    answer = input('y/n: ').lower()
    return True if answer == 'y' or answer is None else False


def add_flathub():
    os.system(
        'flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo')


def install_flatpaks():
    with open('packages.txt', 'r') as f:
        packages = f.read().splitlines()
        packages = ' '.join(packages)
    if packages:
        add_flathub()
        os.system(f'flatpak install {packages} -y')


def install_fonts():
    os.system('cd ~')
    os.system('git clone https://github.com/ryanoasis/nerd-fonts.git --depth 1')
    os.system('cd nerd-fonts && ./install.sh')


def install_chezmoi_and_dotfiles(github_username):
    os.system('cd ~')
    os.system(
        f'sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply {github_username}')


if __name__ == '__main__':
    main()
