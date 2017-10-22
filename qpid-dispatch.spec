# Define pkgdocdir for releases that don't define it already
%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

# determine whether to install systemd or sysvinit scripts
%if 0%{?fedora} || 0%{?rhel} >= 7

%global _use_sysvinit 0
%global _use_systemd 1

%else

%global _use_sysvinit 1
%global _use_systemd 0

%endif

%global proton_minimum_version 0.10

Name:          qpid-dispatch
Version:       1.1.0
Release:       SNAPSHOT%{?dist}
Summary:       Dispatch router for Qpid
License:       ASL 2.0
URL:           http://qpid.apache.org/

Source0:       qpid-dispatch-%{version}.tar.gz

BuildRequires: qpid-proton-c-devel >= %{proton_minimum_version}
BuildRequires: python-devel
BuildRequires: cmake
BuildRequires: python-qpid-proton >= %{proton_minimum_version}

# disable documentation for now
# BuildRequires: pandoc-pdf

%{?fedora:BuildRequires: systemd}

Requires:      qpid-proton-c%{?_isa} >= %{proton_minimum_version}
Requires:      python
Requires:      python-qpid-proton >= %{proton_minimum_version}

# need this for epel7
%if 0%{?rhel} >= 7
BuildRequires: systemd
%endif

%if %{_use_systemd}
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
%endif


%description
A lightweight message router, written in C and built on Qpid Proton, that provides flexible and scalable interconnect between AMQP endpoints or between endpoints and brokers.



%package -n libqpid-dispatch
Summary:  The Qpid Dispatch Router library
Requires: qpid-proton-c%{?_isa} >= %{proton_minimum_version}

%description -n libqpid-dispatch
%{summary}.


%files -n libqpid-dispatch
#%{_libdir}/libqpid-dispatch.so.*
%{_exec_prefix}/lib/qpid-dispatch/libqpid-dispatch.so
%{_exec_prefix}/lib/qpid-dispatch
%exclude %{_exec_prefix}/lib/qpid-dispatch/tests
%{python_sitelib}/qpid_dispatch_site.py*
%{python_sitelib}/qpid_dispatch
%exclude %{python_sitelib}/*egg-info

%post -n libqpid-dispatch -p /sbin/ldconfig

%postun -n libqpid-dispatch -p /sbin/ldconfig




%package -n libqpid-dispatch-devel
Summary:  Development files for Qpid Dispatch
Requires: qpid-proton-c-devel >= %{proton_minimum_version}
Requires: libqpid-dispatch%{?_isa} = %{version}-%{release}


%description -n libqpid-dispatch-devel
%{summary}.


%files -n libqpid-dispatch-devel
%{_includedir}/qpid/dispatch.h
%{_includedir}/qpid/dispatch
#%{_libdir}/libqpid-dispatch.so
%{_exec_prefix}/lib/qpid-dispatch/libqpid-dispatch.so



%package router
Summary:  The Qpid Dispatch Router executable
Requires: libqpid-dispatch%{?_isa} = %{version}-%{release}


%if %{_use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description router
%{summary}.


%files router
%{_sbindir}/qdrouterd
%{_datadir}/qpid-dispatch/console
%config(noreplace) %{_sysconfdir}/qpid-dispatch/qdrouterd.conf
%config(noreplace) %{_sysconfdir}/sasl2/qdrouterd.conf

%if %{_use_systemd}

%{_unitdir}/qdrouterd.service

%else

%{_initrddir}/qdrouterd

%endif

# %{_mandir}/man5/qdrouterd.conf.5*
# %{_mandir}/man8/qdrouterd.8*


%pre router
getent group qdrouterd >/dev/null || groupadd -r qdrouterd
getent passwd qdrouterd >/dev/null || \
  useradd -r -M -g qdrouterd -d %{_localstatedir}/lib/qdrouterd -s /sbin/nologin \
    -c "Owner of Qpid Dispatch Daemons" qdrouterd
exit 0


%if %{_use_systemd}

%post router
%systemd_post qdrouterd.service

%preun router
%systemd_preun qdrouterd.service

%postun router
%systemd_postun_with_restart qdrouterd.service

%endif

%if %{_use_sysvinit}

%post router
/sbin/chkconfig --add qdrouterd

%preun router
if [ $1 -eq 0 ]; then
    /sbin/service qdrouterd stop >/dev/null 2>&1
    /sbin/chkconfig --del qdrouterd
fi

%postun router
if [ "$1" -ge "1" ]; then
    /sbin/service qdrouterd confrestart >/dev/null 2>&1
fi

%endif



%package router-docs
Summary:   Documentation for the Qpid Dispatch router
BuildArch: noarch


%description router-docs
%{summary}.


%files router-docs
%doc %{_pkgdocdir}



%package tools
Summary: Tools for the Qpid Dispatch router
Requires: python-qpid-proton
Requires: libqpid-dispatch%{?_isa} = %{version}-%{release}


%description tools
%{summary}.


%files tools
%{_bindir}/qdstat
%{_bindir}/qdmanage
# %{_mandir}/man8/qdstat.8*
# %{_mandir}/man8/qdmanage.8*
# %exclude %{_sysconfdir}/qpid-dispatch/qdrouter.json
# %exclude %{_sysconfdir}/qpid-dispatch/qdrouter.json.readme.txt


%prep
%setup -q


%build
%cmake -DDOC_INSTALL_DIR=%{?_pkgdocdir} \
       -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DUSE_SETUP_PY=1 \
       -DQD_DOC_INSTALL_DIR=%{_pkgdocdir} \
       -DBUILD_DOCS=off \
       .



%install
%make_install

%if %{_use_systemd}

mkdir -p %{buildroot}/%{_unitdir}
install -pm 644 %{_builddir}/qpid-dispatch-%{version}/etc/qdrouterd.service \
                %{buildroot}/%{_unitdir}

%else

mkdir -p %{buildroot}/%{_initrddir}
install -pm 755 %{_builddir}/qpid-dispatch-%{version}/etc/qdrouterd \
                %{buildroot}/%{_initrddir}

%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%changelog
* Tue Apr 21 2015 Darryl L. Pierce <dpierce@rehdat.com> - 0.4-1
- Rebased on Dispatch 0.4.
- Changed username for qdrouterd to be qdrouterd.

* Tue Feb 24 2015 Darryl L. Pierce <dpierce@redhat.com> - 0.3-4
- Changed SysVInit script to properly name qdrouterd as the service to start.

* Fri Feb 20 2015 Darryl L. Pierce <dpierce@redhat.com> - 0.3-3
- Update inter-package dependencies to include release as well as version.

* Wed Feb 11 2015 Darryl L. Pierce <dpierce@redhat.com> - 0.3-2
- Disabled building documentation due to missing pandoc-pdf on EL6.
- Disabled daemon setgid.
- Fixes to accomodate Python 2.6 on EL6.
- Removed implicit dependency on python-qpid-proton in qpid-dispatch-router.

* Tue Jan 27 2015 Darryl L. Pierce <dpierce@redhat.com> - 0.3-1
- Rebased on Dispatch 0.3.
- Increased the minimum Proton version needed to 0.8.
- Moved all tests to the -devel package.
- Ensure executable bit turned off on systemd file.
- Set the location of installed documentation.

* Thu Nov 20 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.2-9
- Fixed a merge issue that resulted in two patches not being applied.
- Resolves: BZ#1165691

* Wed Nov 19 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.2-8
- DISPATCH-75 - Removed reference to qdstat.conf from qdstat manpage.
- Include systemd service file for EPEL7 packages.
- Brought systemd support up to current Fedora packaging guidelines.
- Resolves: BZ#1165691
- Resolves: BZ#1165681

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Jul  9 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.2-6
- Removed intro-package comments which can cause POSTUN warnings.
- Added dependency on libqpid-dispatch from qpid-dispatch-tools.

* Wed Jul  2 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.2-5
- Fixed the path for the configuration file.
- Resolves: BZ#1115416

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 30 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.2-3
- Fixed build type to be RelWithDebInfo

* Tue Apr 22 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.2-2
- Fixed merging problems across Fedora and EPEL releases.

* Tue Apr 22 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.2-1
- Rebased on Qpid Dispatch 0.2.

* Wed Feb  5 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.1-4
- Fixed path to configuration in qpid-dispatch.service file.
- Added requires from qpid-dispatch-tools to python-qpid-proton.

* Thu Jan 30 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.1-3
- Fix build system to not discard CFLAGS provided by Fedora
- Resolves: BZ#1058448
- Simplified the specfile to be used across release targets.

* Fri Jan 24 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.1-2
- First release for Fedora.
- Resolves: BZ#1055721

* Thu Jan 23 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.1-1.2
- Put all subpackage sections above prep/build/install.
- Removed check and clean sections.
- Added remaining systemd macros.
- Made qpid-dispatch-router-docs a noarch package.


* Wed Jan 22 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.1-1.1
- Added the systemd macros for post/preun/postun
- Moved prep/build/install/check/clean above package definitions.

* Mon Jan 20 2014 Darryl L. Pierce <dpierce@redhat.com> - 0.1-1
- Initial packaging of the codebase.
