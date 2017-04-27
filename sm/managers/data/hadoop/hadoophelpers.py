# Copyright (c) 2017. Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Author: Balazs Meszaros
import bisect

def rampercontainer(context, memory, cores):
    try:
        # RAM - per - container = max(MIN_CONTAINER_SIZE, (Total Available RAM)
        # / containers))

        # values taken from https://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.3.4/bk_installing_manually_book/content/determine-hdp-memory-config.html
        cpus = int(cores[0])
        ram = int(memory[0])

        avail_mem = 0

        # in every case, at least 1G has to be available for the OS
        ram_mapping = [(4000, 1000), (16000, 2000), (24000, 4000), (48000, 6000), (72000, 8000), (96000, 12000), (128000, 24000), (256000, 32000), (512000, 64000)]
        ram_mapping.sort()
        ram_pos = bisect.bisect_right(ram_mapping, (ram,))

        # total available ram
        avail_mem = ram - ram_mapping[ram_pos][1]

        if avail_mem<0:
            return "0"

        min_cont_size = 0

        cont_size_mapping = [(4000, 256), (8000, 512), (24000, 1024)]
        cont_size_mapping.sort()

        if avail_mem>24000:
            min_cont_size = 2048
        else:
            cont_size_pos = bisect.bisect_right(cont_size_mapping, (avail_mem,))
            min_cont_size = cont_size_mapping[cont_size_pos][1]

        # disks not taken into account as the environment is virtualised
        containernumber = min( 2*cpus, avail_mem/min_cont_size)

        ram_per_container = max(min_cont_size, int(avail_mem/containernumber))
        return str(ram_per_container)
    except Exception as e:
        return str(e)

def containercount(context, memory, cores):
    try:
        # number of containers = min (2*CORES, 1.8*DISKS, (Total available
        # RAM) / MIN_CONTAINER_SIZE)

        # values taken from https://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.3.4/bk_installing_manually_book/content/determine-hdp-memory-config.html
        cpus = int(cores[0])
        ram = int(memory[0])

        avail_mem = 0

        # in every case, at least 1G has to be available for the OS
        ram_mapping = [(4000, 1000), (16000, 2000), (24000, 4000), (48000, 6000), (72000, 8000), (96000, 12000), (128000, 24000), (256000, 32000), (512000, 64000)]
        ram_mapping.sort()
        ram_pos = bisect.bisect_right(ram_mapping, (ram,))

        # total available ram
        avail_mem = ram - ram_mapping[ram_pos][1]

        if avail_mem<0:
            return "0"

        min_cont_size = 0

        cont_size_mapping = [(4000, 256), (8000, 512), (24000, 1024)]
        cont_size_mapping.sort()

        if avail_mem>24000:
            min_cont_size = 2048
        else:
            cont_size_pos = bisect.bisect_right(cont_size_mapping, (avail_mem,))
            min_cont_size = cont_size_mapping[cont_size_pos][1]

        # disks not taken into account as the environment is virtualised
        containernumber = int(min( 2*cpus, avail_mem/min_cont_size))

        return str(containernumber)
    except Exception as e:
        return str(e)
