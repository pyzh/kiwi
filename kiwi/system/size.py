# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
# project
from kiwi.command import Command
from kiwi.defaults import Defaults


class SystemSize(object):
    """
    Provide source tree size information

    Attributes

    * :attr:`source_dir`
        source directory path name
    """
    def __init__(self, source_dir):
        self.source_dir = source_dir

    def customize(self, size, requested_filesystem):
        """
        Increase the sum of all file sizes by an empiric factor

        Each filesystem has some overhead it needs to manage itself.
        Thus the plain data size is always smaller as the size of
        the container which embeds it. This method increases the
        given size by a filesystem specific empiric factor to
        ensure the given data size can be stored in a filesystem
        of the customized size

        :param int size: mbsize to update
        :param string requested_filesystem: filesystem name

        :return: mbytes
        :rtype: int
        """
        if requested_filesystem:
            if requested_filesystem.startswith('ext'):
                size *= 1.5
                file_count = self.accumulate_files()
                inode_mbytes = \
                    file_count * Defaults.get_default_inode_size() / 1048576
                size += 2 * inode_mbytes
            elif requested_filesystem == 'btrfs':
                size *= 1.5
            elif requested_filesystem == 'xfs':
                size *= 1.5

        return int(size)

    def accumulate_mbyte_file_sizes(self):
        """
        Calculate data size of all data in the source tree

        :return: mbytes
        :rtype: int
        """
        du_call = Command.run(
            [
                'du', '-s', '--apparent-size', '--block-size', '1',
                self.source_dir
            ]
        )
        return int(du_call.output.split('\t')[0]) / 1048576

    def accumulate_files(self):
        """
        Calculate sum of all files in the source tree

        :return: number of files
        :rtype: int
        """
        bash_comand = [
            'find', self.source_dir, '|', 'wc', '-l'
        ]
        wc_call = Command.run(
            [
                'bash', '-c', ' '.join(bash_comand)
            ]
        )
        return int(wc_call.output.rstrip('\n'))
