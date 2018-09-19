from __future__ import print_function
import psutil
import sys


arg = sys.argv[1]


def get_cpu_usage():
    cpu_used_percent = psutil.cpu_percent(interval=1)
    print(cpu_used_percent, end='')


def get_mem_usage():
    mem_used_percent = psutil.virtual_memory().percent
    print(mem_used_percent, end='')


def get_disk_usage():

    partition_info = psutil.disk_partitions()

    partitions = []
    for item in partition_info:
        partition = item.mountpoint
        partitions.append(partition)

    disks_used_percent = {}
    for item in partitions:
        percent = psutil.disk_usage(item).percent
        disks_used_percent[item] = percent

    print(disks_used_percent, end='')


def main():
    if arg == 'cpu':
        get_cpu_usage()
    elif arg == 'mem':
        get_mem_usage()
    elif arg == 'disk':
        get_disk_usage()


if __name__ == '__main__':
    main()
