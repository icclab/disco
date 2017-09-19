FROM ubuntu

RUN apt-get update && apt-get install -y git python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev && pip install --upgrade pip && pip install python-heatclient lxml python-novaclient pbr urllib3[secure]

WORKDIR /home
RUN git clone https://github.com/icclab/hurtle_cc_sdk.git

WORKDIR /home/hurtle_cc_sdk
RUN python /home/hurtle_cc_sdk/setup.py install; exit 0
RUN python /home/hurtle_cc_sdk/setup.py install; exit 0
RUN python /home/hurtle_cc_sdk/setup.py install

WORKDIR /home
RUN git clone https://github.com/icclab/disco.git

WORKDIR /home/disco
RUN python /home/disco/setup.py install && sed -i 's#manifest=.*#manifest=/home/disco/etc/service_manifest.json#' /home/disco/etc/sm.cfg && sed -i 's#framework_directory=.*#framework_directory=/home/disco/sm/managers/data#' /home/disco/etc/sm.cfg && sed -i 's#design_uri=.*#design_uri=#' /home/disco/etc/sm.cfg && echo '#!/bin/sh'"\n"'sed -i "s#design_uri=.*#design_uri=$DESIGN_URI#" /home/disco/etc/sm.cfg'"\n"'service_manager -c /home/disco/etc/sm.cfg' > /home/disco/runsm.sh && chmod a+x /home/disco/runsm.sh

CMD /home/disco/runsm.sh
