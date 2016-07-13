#!/usr/bin/python
#
# DailyPatch - Automated Linux Kernel Patch Generate Engine
# Copyright (C) 2012 - 2016 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the DailyPatch package.
#
# DailyPatch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# DailyPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DailyPatch; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
import sys
import datetime
import subprocess
import json

from misc import is_source_file, _execute_shell
from celery.utils.text import indent

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DATAFILE = os.path.join(ROOT_DIR, 'data/fuzz_ret_chk_list.txt')
SCRIPTFILE = os.path.join(ROOT_DIR, 'script/fuzz_ret_chk_finder.cocci')
ERRPTRFILE = os.path.join(ROOT_DIR, 'script/ERR_PTR_RET_CHK.cocci')
NULLFILE = os.path.join(ROOT_DIR, 'script/NULL_RET_CHK.cocci')

def is_config_debug_fs(fname):
    cmd = "/usr/bin/grep -r \"CONFIG_DEBUG_FS\" %s > /dev/null" % (fname)
    if subprocess.call(cmd, shell=True) == 0:
        return True
    return False

def update_err_ptr_ret_chk(mfuncs):
    skiplist = ['rfkill_alloc', 'clk_get', 'clk_register', 'clk_register_fixed_rate',
                'rpcauth_create', 'vb2_dma_contig_init_ctx', 'of_clk_get',
                'arm_iommu_create_mapping', 'devm_regulator_get',
                'platform_device_register_full', 'anon_inode_getfile',
                'of_clk_get_by_name', 'sock_alloc_file', 'skb_mac_gso_segment',
                'get_fb_info', 'unpack_dfa', 'select_bad_process', 'perf_init_event',
                'debugfs_rename', 'pinctrl_register', 'rhashtable_walk_next',
                'devm_gpiod_get_index_optional', 'devm_gpiod_get_optional']

    funcs = []
    for key in sorted(mfuncs.keys()):
        if mfuncs[key]['TYPE'] != 'IS_ERR':
            continue
        if key in skiplist:
            continue
        if mfuncs[key]['IS_ERR'] < 2:
            continue
        funcs.append(key)

    scripts = '/// fix return value check in {{function}}\n\
///\n\
/// In case of error, the function XXXX() returns ERR_PTR()\n\
/// and never returns NULL. The NULL test in the return value check\n\
/// should be replaced with IS_ERR().\n\
///\n\
@@\n\
expression ret, E;\n\
@@\n\
ret = \(%s\)(...);\n\
... when != ret = E\n\
(\n\
- ret == NULL || IS_ERR(ret)\n\
+ IS_ERR(ret)\n\
|\n\
- IS_ERR(ret) || ret == NULL\n\
+ IS_ERR(ret)\n\
|\n\
- ret != NULL && !IS_ERR(ret)\n\
+ !IS_ERR(ret)\n\
|\n\
- !IS_ERR(ret) && ret != NULL\n\
+ !IS_ERR(ret)\n\
|\n\
- ret == NULL\n\
+ IS_ERR(ret)\n\
|\n\
- ret != NULL\n\
+ !IS_ERR(ret)\n\
)\n' % '\|\n'.join(funcs)

    with open(ERRPTRFILE, "w") as fp:
        fp.write(scripts)

def update_null_ret_chk(mfuncs):
    skiplist = ['fn', 'PTR_ERR_OR_ZERO', 'ALIGN', 'read', 'readl', 'strlen',
                'ACCESS_ONCE', 'ACPI_ALLOCATE', 'ACPI_ALLOCATE_ZEROED',
                'ACPI_COMPANION', 'ACPI_HANDLE', 'BNX2X_PCI_ALLOC',
                'DIV_ROUND_CLOSEST', 'I915_READ', 'IXGBE_READ_REG', 'KMEM_CACHE',
                'NCR_700_detect', 'PAGE_ALIGN', 'PTR_ERR', 'RBIOS16', 'READ_ONCE',
                'abs', 'cpu_to_le32', 'clk_get_parent', 'clk_get_rate',
                'be16_to_cpu', 'be32_to_cpup', 'be64_to_cpu']

    funcs = []
    for key in sorted(mfuncs.keys()):
        if mfuncs[key]['TYPE'] != 'NULL':
            continue
        if key in skiplist:
            continue
        if key.find('debugfs_') == 0:
            continue
        if mfuncs[key]['NULL'] < 3:
            continue
        funcs.append(key)

    scripts = '/// fix return value check in {{function}}\n\
///\n\
/// In case of error, the function XXXX() returns NULL pointer\n\
/// not ERR_PTR(). The IS_ERR() test in the return value check\n\
/// should be replaced with NULL test.\n\
///\n\
@@\n\
expression ret, E;\n\
@@\n\
ret = \(%s\)(...);\n\
... when != ret = E\n\
(\n\
- IS_ERR(ret)\n\
+ !ret\n\
|\n\
- !IS_ERR(ret)\n\
+ ret\n\
)\n' % '\|\n'.join(funcs)
    with open(NULLFILE, "w") as fp:
        fp.write(scripts)


def main(args):
    kdir = '/var/lib/dpatch/repo/2/linux-next'

    skip_list = [
        'malloc',
        'readb',
         'xchg',
         'PDE_DATA',
         'ioread32',
         'in_be32',
         'nv_ro16',
         'be32_to_cpu',
         'le32_to_cpu',
         'le64_to_cpu',
         'min',
         'min_t',
         'inl',
         'inb',
         'container_of',
         'ERR_CAST',
         'ERR_PTR',
         'list_entry',
         'list_first_entry',
         'key_ref_to_ptr',
         # skip special function
         'posix_acl_from_xattr',
         'skb_gso_segment',
         'd_hash_and_lookup',
         'rcu_dereference',
         'rcu_dereference_protected',
         'dget_parent',
         'get_acl',
         'netdev_priv',
         'ext4_bread',
         '__d_path',
         'i_size_read',
         '__skb_gso_segment',
         'dget',
         'map_extent_mft_record',
         'gfs2_lookupi',
         'fat_build_inode'
    ]

    _fix_table = {
        "clk_get": "IS_ERR",
        "dma_buf_attach": "IS_ERR",
        "platform_device_register_resndata": "IS_ERR",
        "syscon_node_to_regmap": "IS_ERR",
        "clk_get_parent": "NULL",
        "container_of": "NULL",
        "devm_request_and_ioremap": "NULL",
        "scsi_host_lookup": "NULL",
        "ubifs_fast_find_freeable": "NULL",
        "ubifs_fast_find_frdi_idx": "NULL",
        "btrfs_get_acl": "IS_ERR_OR_NULL",
        "btrfs_lookup_xattr": "IS_ERR_OR_NULL",
        "dma_buf_map_attachment": "IS_ERR",
        "ext2_get_acl": "IS_ERR_OR_NULL",
        "ext3_get_acl": "IS_ERR_OR_NULL",
        "ext4_get_acl": "IS_ERR_OR_NULL",
        "f2fs_get_acl": "IS_ERR_OR_NULL",
        "flow_cache_lookup": "IS_ERR_OR_NULL",
        "follow_page_mask": "IS_ERR_OR_NULL",
        "gfs2_get_acl": "IS_ERR_OR_NULL",
        "gfs2_lookupi": "IS_ERR_OR_NULL",
        "get_phy_device": "IS_ERR",
        "hfsplus_get_posix_acl": "IS_ERR_OR_NULL",
        "jffs2_get_acl": "IS_ERR_OR_NULL",
        "jfs_get_acl": "IS_ERR_OR_NULL",
        "nfs3_proc_getacl": "IS_ERR_OR_NULL",
        "posix_acl_from_xattr": "IS_ERR_OR_NULL",
        "reiserfs_get_acl": "IS_ERR_OR_NULL",
        "xfs_get_acl": "IS_ERR_OR_NULL",
        "pci_device_group": "IS_ERR_OR_NULL",
        "assoc_array_delete": "IS_ERR_OR_NULL"
    }

    if not os.path.exists(DATAFILE):
        sfiles = _execute_shell("find %s -type f" % kdir)[0:-1]
        count = 0
        fp = open(DATAFILE, "w")
        for sfile in sfiles:
            if not is_source_file(sfile):
                continue
            if sfile.find("Documentation/") == 0:
                continue
            if sfile.find("scripts/") == 0:
                continue
            if sfile.find("tools/") == 0:
                continue
            if sfile.find("firmware/") == 0:
                continue
            if count > 0 and count % 100 == 0:
                print 'current: %d, total: %d' % (count, len(sfiles))
            count += 1
            sargs = '/usr/bin/spatch -I %s -timeout 20 -very_quiet -sp_file %s %s | sort -u' % (
                        os.path.join(kdir, 'include'), SCRIPTFILE, sfile)
            lines = []
            for line in _execute_shell(sargs):
                if line.find('|') == -1:
                    continue
                #if not re.search('\w+', line):
                #    continue
                #if lines.count(line) != 0:
                #    continue
                if line in skip_list:
                    continue
                lines.append("%s|%s" % (line, sfile))

            if len(lines):
                fp.write('\n'.join(lines))
                fp.write('\n')
        fp.close()

    fp = open(DATAFILE, "r")
    lines = fp.readlines()
    fp.close()

    # merge data
    mlines = []
    lastfile = None
    mfuncs = {}
    for line in lines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if len(a) < 3:
            continue
        if a[0] in skip_list:
            continue
        if a[1] == 'IS_ERR_OR_NULL':
            continue
        if lastfile != a[2]:
            for fun in mfuncs.keys():
                mlines.append("%s|%s|%s" % (fun, mfuncs[fun], lastfile))
            mfuncs.clear()
            lastfile = a[2]
        if mfuncs.has_key(a[0]) and mfuncs[a[0]] != a[1]:
            #print 'fix for function: %s in file %s' %(a[0], a[2])
            mfuncs[a[0]] = 'IS_ERR_OR_NULL'
        else:
            mfuncs[a[0]] = a[1]
    if not lastfile is None:
        for fun in mfuncs.keys():
            mlines.append("%s|%s|%s" % (fun, mfuncs[fun], lastfile))

    mfuncs = {}
    for line in mlines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if len(a) < 3:
            continue
        if a[0] in skip_list:
            continue
        if not mfuncs.has_key(a[0]):
            mfuncs[a[0]] = {'TYPE': 'NULL', 'COUNT': 0, 'NULL': 0, 'IS_ERR': 0, 'IS_ERR_OR_NULL': 0}
        mfuncs[a[0]][a[1]] = mfuncs[a[0]][a[1]] + 1
        mfuncs[a[0]]['COUNT'] = mfuncs[a[0]]['COUNT'] + 1

        if _fix_table.has_key(a[0]):
            mfuncs[a[0]]['TYPE'] = _fix_table[a[0]]
        else:
            if mfuncs[a[0]]['NULL'] > mfuncs[a[0]]['IS_ERR']:
                if mfuncs[a[0]]['NULL'] > mfuncs[a[0]]['IS_ERR_OR_NULL']:
                    mfuncs[a[0]]['TYPE'] = 'NULL'
                else:
                    mfuncs[a[0]]['TYPE'] = 'IS_ERR_OR_NULL'
            else:
                if mfuncs[a[0]]['IS_ERR'] > mfuncs[a[0]]['IS_ERR_OR_NULL']:
                    mfuncs[a[0]]['TYPE'] = 'IS_ERR'
                else:
                    mfuncs[a[0]]['TYPE'] = 'IS_ERR_OR_NULL'

    for line in lines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if len(a) < 3:
            continue
        if a[0] in skip_list:
            continue
        if a[1] == 'IS_ERR_OR_NULL':
            continue
        if a[0].find('debugfs_') == 0: #and not is_config_debug_fs(a[2]):
            continue
        if mfuncs[a[0]]['TYPE'] != a[1] and mfuncs[a[0]]['IS_ERR'] != mfuncs[a[0]]['NULL'] and mfuncs[a[0]]['COUNT'] > 1:
            print "ERROR: %s, type: %s, real type: %s, file: %s, NULL: %d, IS_ERR:%d, IS_ERR_OR_NULL: %d" % (a[0],
                    a[1], mfuncs[a[0]]['TYPE'], a[2], mfuncs[a[0]]['NULL'], mfuncs[a[0]]['IS_ERR'], mfuncs[a[0]]['IS_ERR_OR_NULL'])

    update_err_ptr_ret_chk(mfuncs)
    update_null_ret_chk(mfuncs)

    #print json.dumps(mfuncs, indent = 4)

    '''
    # merge data
    mlines = []
    lastfile = None
    mfuncs = {}
    for line in lines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if len(a) < 3:
            continue
        if a[0] in skip_list:
            continue
        if a[1] == 'IS_ERR_OR_NULL':
            continue
        if lastfile != a[2]:
            for fun in mfuncs.keys():
                mlines.append("%s|%s|%s" % (fun, mfuncs[fun], lastfile))
            mfuncs.clear()
            lastfile = a[2]
        if mfuncs.has_key(a[0]) and mfuncs[a[0]] != a[1]:
            #print 'fix for function: %s in file %s' %(a[0], a[2])
            mfuncs[a[0]] = 'IS_ERR_OR_NULL'
        else:
            mfuncs[a[0]] = a[1]
    if not lastfile is None:
        for fun in mfuncs.keys():
            mlines.append("%s|%s|%s" % (fun, mfuncs[fun], lastfile))

    funcs = {}
    for line in mlines:
        if line.find('|') == -1:
            continue
        line = line.replace('\n', '')
        a = line.split('|')
        if len(a) < 3:
            continue
        if a[0] in skip_list:
            continue
        if funcs.has_key(a[0]):
            funcs[a[0]]['cnt'] += 1
            if funcs[a[0]]['type'] != a[1]:
                if a[1] == 'IS_ERR_OR_NULL':
                    #print "WARN: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], funcs[a[0]]['type'], a[2])
                    continue 
                if a[0].find('debugfs_') == 0 and not is_config_debug_fs(a[2]):
                    continue
                print "ERROR: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], funcs[a[0]]['type'], a[2])
        else:
            if _fix_table.has_key(a[0]):
                if _fix_table[a[0]] != a[1]:
                    if a[1] == 'IS_ERR_OR_NULL':
                        #print "WARN: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], _fix_table[a[0]], a[2])
                        continue 
                    if a[0].find('debugfs_') == 0 and not is_config_debug_fs(a[2]):
                        continue
                    print "ERROR: %s, type: %s, real type: %s, file: %s" % (a[0], a[1], _fix_table[a[0]], a[2])
                    funcs[a[0]] = {'type': _fix_table[a[0]], 'cnt': 1}
                else:
                    funcs[a[0]] = {'type': a[1], 'cnt': 1}
            else:
                funcs[a[0]] = {'type': a[1], 'cnt': 1}

    if not os.path.exists(ERRFILE):
        tmps = []
        for fn in funcs.keys():
            if funcs[fn]['type'] != 'IS_ERR':
                continue
            tmps.append("%s|%s|%s" % (fn, funcs[fn]['type'], funcs[fn]['cnt']))
     
        fp = open(ERRFILE, "w")
        fp.write("// Update: %s\n" % datetime.datetime.now())
        fp.write('\n'.join(tmps))
        fp.close()
   
    if not os.path.exists(NULLFILE):
        tmps = []
        for fn in funcs.keys():
            if funcs[fn]['type'] != 'NULL' or funcs[fn]['cnt'] < 2:
                continue
            tmps.append("%s|%s|%s" % (fn, funcs[fn]['type'], funcs[fn]['cnt']))
    
        fp = open(NULLFILE, "w")
        fp.write("// Update: %s\n" % datetime.datetime.now())
        fp.write('\n'.join(tmps))
        fp.close()
    '''
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
