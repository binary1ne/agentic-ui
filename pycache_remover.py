import os
import shutil

def delete_pycache(directory):
    """
    Recursively deletes all __pycache__ directories within the specified directory.
    
    Args:
    - directory (str): The path of the directory to start searching.
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    print(f"Deleted: {dir_path}")
                except Exception as e:
                    print(f"Error deleting {dir_path}: {e}")

if __name__ == "__main__":
    # Replace with the directory you want to clean up
    directory_path = input("Enter the directory path to delete __pycache__: ")
    delete_pycache(directory_path)
