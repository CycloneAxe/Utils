#!/usr/bin/env python3

import subprocess, os, re

# 可读写的 ntfs 新挂载点
ntfs_volumes = '/tmp/ntfs/'
ntfs_pattern = re.compile(r'File System Personality:  NTFS')
ntfs_device_node = re.compile(r'.*Device Node:.*')
device_dict = {}

def get_device_node():
	disk = subprocess.check_output(['ls', '-1', '/Volumes']).decode('utf-8')
	disk_list = [ disk for disk in disk.split("\n") if disk.strip() ]
	# 忽略 Mac OSX 系统盘
	for disk_name in disk_list[1:]:
		disk_path = '/Volumes/' + disk_name
		try:
			disk_info = subprocess.check_output(['diskutil', 'info', disk_path]).decode('utf-8')
		except subprocess.CalledProcessError as e:
			print("diskutil stderr output:\n", e.output)
		if ntfs_pattern.search(disk_info):
			device_node_str = ntfs_device_node.findall(disk_info)
			device_node = device_node_str[0].split()[2]
			device_dict[disk_path] = device_node

def mount_ntfs():
	if not device_dict:
		print('No ntfs filesystem found...')
		return

	print('hdiutil detach disk...')
	for (disk_path, device_node) in device_dict.items():
		if os.path.isdir(disk_path):
			subprocess.check_output(['hdiutil', 'detach', disk_path])

		ntfs_volume = os.path.join(ntfs_volumes, disk_path.lstrip('/.'))
		if not os.path.isdir(ntfs_volume):
			os.makedirs(ntfs_volume)

		# ntfs_volume = ntfs_volume.replace(' ', '\ ')
		print('sudo /sbin/mount_ntfs -o rw,nobrowse %s %s' % (device_node, ntfs_volume))
		subprocess.check_output([
			'sudo',
			'mount_ntfs',
			'-o',
			'rw,nobrowse',
			device_node,
			ntfs_volume
		])

if __name__ == '__main__':
	get_device_node()
	mount_ntfs()