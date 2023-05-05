import os
import hashlib
import time
import sys
import argparse
import shutil

def log(message, log_file):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(log_file, 'a') as f:
        f.write(f'[{now}]{message}\n')
    print(f'[{now}]{message}')

def compare_files(file1, file2):
    with open(file1, 'rb') as f1:
        with open(file2, 'rb') as f2:
            return hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Folder synchronization script.')
    parser.add_argument('source_folder', help='Path to the source folder')
    parser.add_argument('replica_folder', help='Path to the replica folder')
    parser.add_argument('--sync_interval', type=int, default=300, help='Synchronization interval in seconds (default: 300)')
    parser.add_argument('--log_file', default='sync_log.txt', help='Path to the log file (default: sync_log.txt)')
    return parser.parse_args()

def main():
    args = parse_arguments()

    source_folder = os.path.abspath(args.source_folder)
    replica_folder = os.path.abspath(args.replica_folder)
    sync_interval = args.sync_interval
    log_file = args.log_file

    if not os.path.isdir(source_folder):
        log(f'Source folder {source_folder} does not exist.', log_file)
        sys.exit(1)

    if not os.path.isdir(replica_folder):
        log(f'Replica folder {replica_folder} does not exist.', log_file)
        sys.exit(1)

    while True:
        source_files = set(os.listdir(source_folder))
        replica_files = set(os.listdir(replica_folder))

        for file in source_files:
            src_path = os.path.join(source_folder, file)
            replica_path = os.path.join(replica_folder, file)

            if file not in replica_files:
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, replica_path)
                    log(f'Copied {file} to replica folder.', log_file)
                elif os.path.isdir(src_path):
                    shutil.copytree(src_path, replica_path)
                    log(f'Copied directory {file} to replica folder.', log_file)
            else:
                if os.path.isfile(src_path) and not compare_files(src_path, replica_path):
                    shutil.copy2(src_path, replica_path)
                    log(f'Updated {file} in replica folder.', log_file)

        for file in replica_files - source_files:
            replica_path = os.path.join(replica_folder, file)
            if os.path.isfile(replica_path):
                os.remove(replica_path)
                log(f'Removed {file} from replica folder.', log_file)
            elif os.path.isdir(replica_path):
                shutil.rmtree(replica_path)
                log(f'Removed directory {file} from replica folder.', log_file)

        time.sleep(sync_interval)

if __name__ == '__main__':
    main()
