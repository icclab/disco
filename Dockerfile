FROM ubuntu

RUN apt-get update
RUN apt-get install -y git python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjp$
RUN pip install --upgrade pip
RUN pip install python-heatclient lxml python-novaclient pbr urllib3[secure]

WORKDIR /home
RUN git clone https://github.com/icclab/hurtle_cc_sdk.git

WORKDIR /home/hurtle_cc_sdk
RUN python /home/hurtle_cc_sdk/setup.py install; exit 0
RUN python /home/hurtle_cc_sdk/setup.py install; exit 0
RUN python /home/hurtle_cc_sdk/setup.py install

WORKDIR /home
RUN git clone https://github.com/icclab/disco.git

WORKDIR /home/disco
RUN python /home/disco/setup.py install

RUN sed -i 's#manifest=.*#manifest=/home/disco/etc/service_manifest.json#' /home/disco/etc/sm.cfg
RUN sed -i 's#framework_directory=.*#framework_directory=/home/disco/sm/managers/data#' /home/disco/e$
RUN sed -i 's#design_uri=.*#design_uri=#' /home/disco/etc/sm.cfg

RUN echo '#!/bin/sh'"\n"'sed -i "s#design_uri=.*#design_uri=$DESIGN_URI#" /home/disco/etc/sm.cfg'"\n"$
RUN chmod a+x /home/disco/runsm.sh

CMD ["sh","-c","/home/disco/runsm.sh"]
