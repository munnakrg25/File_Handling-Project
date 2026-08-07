from pathlib import Path
import os

def createfile():
    try:
        name = input('enter the name of the file: ')
        path = Path(name)
        if not path.exists():
            data = input('enter the data you want to write in the file: ')
            with open(name, 'w') as fs:
                fs.write(data)
            print('file created successfully')
        else:
            print('file already exists')

    except Exception as err:
        print(f'error occurred: {err}')
        

def readfile():
    name = input('enter the name of the file you want to read: ')
    path = Path(name)
    try:

        if path.exists():
            with open(path, 'r') as fs:
                content = fs.read()
                print(f'content of the file is: \n{content}')

        else:
            print('file does not exist')    
    except Exception as err:
        print(f'An error occurred: {err}')
def updatefile():
    try:
        name = input('enter the name of the file you want to update: ')
        path = Path(name)
        if path.exists():
            print('operations')
            print(' 1. for renaming the file')
            print(' 2. for appending  the file')
            print(' 3. for writing to the file')

        choice = int(input('enter your choice: '))
        if choice == 1:
            newname = input('enter the new name of the file: ')
            new_path = Path(newname)
            if not new_path.exists():
                path.rename(new_path)
                print('file renamed successfully')
            else:
                print('file with this name already exists')

        elif choice == 2:
            with open(path, 'a') as fs:
                data = input('enter the data you want to append: ')
                fs.write('\n' + data)
            print('data appended successfully')

        elif choice == 3:
            with open(path, 'w') as fs:
                data = input('enter the data you want to write: ')
                fs.write(data)
            print('data written successfully')
    except Exception as err:
        print(f'An error occurred: {err}')


def deletefile():
    try:
        name = input('enter the name of the file you want to delete: ')
        path = Path(name)
        if path.exists():
            os.remove(path)
            print('file deleted successfully')
        else:
            print('file does not exist')
    except Exception as err:
        print(f'An error occurred: {err}')

print('press 1 for creating a file')
print('press 2 for reading a file')
print('press 3 for updating a file')
print('press 4 for deleting a file')

a = int(input('\n tell your response: '))

if a == 1:
    createfile()

if a == 2:
    readfile()

if a == 3:
    updatefile()

if a == 4:
    deletefile()