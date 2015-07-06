"""
Copyright (c) 2012-2015 RockStor, Inc. <http://rockstor.com>
This file is part of RockStor.

RockStor is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

RockStor is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

BTRFS = '/usr/sbin/btrfs'


import re
from django.conf import settings
from storageadmin.models import Pool
from system.osi import run_command


def main():
    for p in Pool.objects.all():
        mnt_pt = '%s%s' % (settings.MNT_PT, p.name)
        o, e, rc = run_command([BTRFS, 'subvol', 'list', mnt_pt])
        subvol_ids = []
        for l in o:
            if (re.match('ID ', l) is not None):
                subvol_ids.append(l.split()[1])

        o, e, rc = run_command([BTRFS, 'qgroup', 'show', mnt_pt])
        qgroup_ids = []
        for l in o:
            if (re.match('0/', l) is not None):
                q = l.split()[0].split('/')[1]
                if (q == '5'):
                    continue
                qgroup_ids.append(l.split()[0].split('/')[1])

        for q in qgroup_ids:
            if (q not in subvol_ids):
                print ('qgroup %s not in use. deleting' % q)
                run_command([BTRFS, 'qgroup', 'destroy', '0/%s' % q, mnt_pt])


if __name__ == '__main__':
    main()