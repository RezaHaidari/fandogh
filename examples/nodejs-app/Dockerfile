FROM    centos:centos6
# Enable Extra Packages for Enterprise Linux (EPEL) for CentOS
RUN     yum install -y epel-release
# Install Node.js and npm
RUN     yum install -y nodejs npm

# Install app dependencies
COPY package.json /src/package.json
RUN npm config set strict-ssl false

RUN cd /src; npm install --production

COPY . /src

EXPOSE  80

CMD ["node", "/src/index.js"]
