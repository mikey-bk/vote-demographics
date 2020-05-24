import os

def mkdir_r(path):
    ''' Recursive mkdir - assumes directories separated by forward slashes ('/') '''
    dirs = path.split('/')
    the_path = ''
    for d in dirs:
        the_path = d if not the_path else '/'.join([the_path, d])
        if not os.path.exists(the_path):
            print(f'Creating: {the_path}')
            os.mkdir(the_path)


if __name__ == '__main__':
    mkdir_r('./test/several/directories')
