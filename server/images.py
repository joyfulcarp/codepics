import os
from pathlib import Path

def find_images(root: str) -> dict[str: list[str]]:
    print(f'Searching for image collections in {root}')

    collections = {}
    collection_dirs = [f.name for f in os.scandir(root) if f.is_dir()]

    for src in collection_dirs:
        path = Path(root) / src
        imgs = []
        for f in os.scandir(path):
            if not f.is_file(follow_symlinks=False):
                continue
            elif Path(f.name).suffix not in ['.png', '.jpg', '.jpeg']:
                continue
            else:
                imgs.append(f.name)

        if len(imgs) >= 20:
            collections[src] = imgs
        else:
            print(f'Not enough images in collection {src}')

    return collections


def main():
    print(find_images('./static/cards'))


if __name__ == '__main__':
    main()
