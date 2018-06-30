FROM		scholzj/centos-builder-base:centos7-latest
MAINTAINER 	JAkub Scholz "www@scholzj.com"

ARG FTP_USERNAME
ARG FTP_PASSWORD
ARG FTP_HOSTNAME

USER root

# Install Qpid Proton dependency
RUN wget http://repo.effectivemessaging.com/qpid-proton-devel.repo -P /etc/yum.repos.d
RUN yum -y install qpid-proton-c qpid-proton-c-devel python-qpid-proton

# Create the RPMs
RUN rpmdev-setuptree
ADD ./qpid-dispatch.spec /root/rpmbuild/SPECS/qpid-dispatch.spec
WORKDIR /root/rpmbuild/SOURCES
RUN wget https://github.com/apache/qpid-dispatch/archive/master.tar.gz
RUN tar -xf master.tar.gz
RUN mv qpid-dispatch-master/ qpid-dispatch-1.3.0/
RUN tar -z -cf qpid-dispatch-1.3.0.tar.gz qpid-dispatch-1.3.0/
RUN rm -rf master.tar.gz qpid-dispatch-1.3.0/
WORKDIR /root/rpmbuild/SPECS
RUN rpmbuild -ba qpid-dispatch.spec

# Create and deploy the RPMs to the repository
RUN mkdir -p /root/repo/CentOS/7/x86_64
RUN mkdir -p /root/repo/CentOS/7/SRPMS
RUN mv /root/rpmbuild/RPMS/x86_64/*.rpm /root/repo/CentOS/7/x86_64/
RUN mv /root/rpmbuild/RPMS/noarch/*.rpm /root/repo/CentOS/7/x86_64/
RUN mv /root/rpmbuild/SRPMS/*.rpm /root/repo/CentOS/7/SRPMS/
WORKDIR /root/repo/CentOS/7/x86_64/
RUN createrepo .
WORKDIR /root/repo/CentOS/7/SRPMS
RUN createrepo .
RUN ncftpget -u $FTP_USERNAME -p $FTP_PASSWORD -R -DD $FTP_HOSTNAME /tmp/ /web/repo/qpid-dispatch-devel/
RUN ncftpput -u $FTP_USERNAME -p $FTP_PASSWORD -R $FTP_HOSTNAME /web/repo/qpid-dispatch-devel/ /root/repo/*

# Nothing to run
CMD    /bin/bash
