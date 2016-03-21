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
from tempfile import NamedTemporaryFile

# project
from ..command import Command
from ..logger import log
from .base import PartitionerBase


class PartitionerDasd(PartitionerBase):
    """
        implement fdasd partition setup
    """
    def post_init(self):
        # fdasd partition type/flag map
        self.flag_map = {
            'f.active': None,
            't.linux': '1',
            't.lvm': '1',
            't.raid': '1',
            't.efi': None,
            't.csm': None
        }

    def create(self, name, mbsize, type_name, flags=None):
        self.partition_id += 1
        fdasd_input = NamedTemporaryFile()
        with open(fdasd_input.name, 'w') as partition:
            log.debug(
                '%s: fdasd: n p cur_position +%sM w q',
                name, format(mbsize)
            )
            if mbsize == 'all_free':
                partition.write('n\np\n\n\nw\nq\n')
            else:
                partition.write('n\np\n\n+%dM\nw\nq\n' % mbsize)
        bash_command = ' '.join(
            ['cat', fdasd_input.name, '|', 'fdasd', '-f', self.disk_device]
        )
        try:
            Command.run(
                ['bash', '-c', bash_command]
            )
        except Exception:
            # unfortunately fdasd reports that it can't read in the partition
            # table which I consider a bug in fdasd. However the table was
            # correctly created and therefore we continue. Problem is that we
            # are not able to detect real errors with the fdasd operation at
            # that point.
            log.debug('potential fdasd errors were ignored')
