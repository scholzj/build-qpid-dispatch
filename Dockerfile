# DISPATCH
#
# VERSION               0.0.1

FROM		centos:centos7
MAINTAINER 	JAkub Scholz "www@scholzj.com"

ARG FTP_USERNAME
ARG FTP_PASSWORD
ARG FTP_HOSTNAME

# Install all dependencies
USER root
RUN yum -y install epel-release
RUN yum -y install wget tar rpm-build rpmdevtools gcc cmake make libuuid-devel openssl-devel swig python-devel epydoc doxygen cyrus-sasl.x86_64 cyrus-sasl-devel.x86_64 cyrus-sasl-plain.x86_64 cyrus-sasl-md5.x86_64 createrepo ncftp

# Install Qpid Proton dependency
RUN wget http://repo.effectivemessaging.com/qpid-proton-testing.repo -P /etc/yum.repos.d
RUN yum -y install qpid-proton-c qpid-proton-c-devel python-qpid-proton

# Create the RPMs
RUN rpmdev-setuptree
ADD ./qpid-dispatch.spec /root/rpmbuild/SPECS/qpid-dispatch.spec
WORKDIR /root/rpmbuild/SOURCES
RUN wget https://github.com/apache/qpid-dispatch/archive/0.7.0-rc1.tar.gz
RUN tar -xf 0.7.0-rc1.tar.gz
RUN mv qpid-dispatch-0.7.0-rc1/ qpid-dispatch-0.7.0/
RUN tar -z -cf qpid-dispatch-0.7.0.tar.gz qpid-dispatch-0.7.0/
RUN rm -rf 0.7.0-rc1.tar.gz qpid-dispatch-0.7.0-rc1/
ADD ./0001-NO-JIRA-Systemd-control-file-for-qdrouterd.patch /root/rpmbuild/SOURCES/0001-NO-JIRA-Systemd-control-file-for-qdrouterd.patch
ADD ./0002-NO-JIRA-new-SysVInit-script-for-qdrouterd-from-Alan-.patch /root/rpmbuild/SOURCES/0002-NO-JIRA-new-SysVInit-script-for-qdrouterd-from-Alan-.patch
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
RUN ncftpget -u $FTP_USERNAME -p $FTP_PASSWORD -R -DD $FTP_HOSTNAME /tmp/ /web/repo/qpid-dispatch-testing/
RUN ncftpput -u $FTP_USERNAME -p $FTP_PASSWORD -R $FTP_HOSTNAME /web/repo/qpid-dispatch-testing/ /root/repo/*

# Nothing to run
CMD    /bin/bash
