%global pykde4_akonadi 1
%global pyqt4_version 4.6.2
%global python_ver %(%{__python} -c "import sys ; print sys.version[:3]")
%global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")
%global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")

Name: kdebindings
Version: 4.3.4
Release: 5%{?dist}
Summary: KDE bindings to non-C++ languages

# http://techbase.kde.org/Policies/Licensing_Policy
License: LGPLv2+
Group: User Interface/Desktops
URL: http://developer.kde.org/language-bindings/

# license issue, remove csharp from tarball, create new source archive without these files
# Source0: ftp://ftp.kde.org/pub/kde/stable/%{version}/src/%{name}-%{version}.tar.bz2
Source0: %{name}-%{version}-patched.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# workaround change to sip/phonon/backendcapabilities.sip which requires PyQt4 4.5
Patch1: kdebindings-4.2.85-old-PyQt4.patch

# disable webkit
Patch2: kdebindings-4.3.4-webkit.patch

# upstream patches


BuildRequires: akonadi-devel >= 1.1.0
BuildRequires: kdebase-workspace-devel >= %{version}
BuildRequires: kdegraphics-devel >= %{version}
BuildRequires: kdelibs4-devel >= %{version}
BuildRequires: kdepimlibs-devel >= %{version}
BuildRequires: python-devel
BuildRequires: PyQt4-devel >= %{pyqt4_version}
BuildRequires: qimageblitz-devel
BuildRequires: soprano-devel

Requires: kdelibs4 >= %{version}

Obsoletes: kdebindings-devel < %{version}-%{release}

%description
KDE bindings to non-C++ languages

%package -n PyKDE4
Group: Development/Languages
Summary: Python bindings for KDE4
Requires: kdelibs4 >= %{version}
Requires: PyQt4 >= %{pyqt4_version}
%{?_sip_api:Requires: sip-api(%{_sip_api_major}) >= %{_sip_api}}

%description -n PyKDE4
%{summary}.

%package -n PyKDE4-akonadi
Summary: Akonadi runtime support for PyKDE4 
Group: Development/Languages 
Requires: PyKDE4 = %{version}-%{release}
Requires: kdepimlibs-akonadi%{?_isa} >= %{version} 

%description -n PyKDE4-akonadi 
%{summary}.

%package -n PyKDE4-devel
Group: Development/Languages
Summary: Files needed to build PyKDE4-based applications
Requires: PyQt4-devel
Requires: PyKDE4 = %{version}-%{release}
Requires: PyKDE4-akonadi%{?_isa} = %{version}-%{release}

%description -n PyKDE4-devel
%{summary}.

%package -n kross-python
Group: Development/Languages
Summary: Kross plugin for python
Requires: kdelibs4 >= %{version}
Provides: kross(python) = %{version}-%{release}

%description -n kross-python
Python plugin for the Kross archtecture in KDE4.

%prep
%setup -q -n %{name}-%{version}-patched

%patch1 -p0 -b .old-PyQt4
%patch2 -p1 -b .webkit

# upstream patches


%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kde4} \
  -DPYTHON_LIBRARY=%{_libdir}/libpython%{python_ver}.so.1.0 \
  -DPYTHON_LIBRARIES=%{_libdir}/libpython%{python_ver}.so.1.0 \
  -DPYTHON_INCLUDE_PATH=%{_includedir}/python%{python_ver} \
  -DBUILD_csharp=OFF \
  -DBUILD_falcon=OFF \
  -DBUILD_php=OFF \
  -DBUILD_ruby=OFF \
  -DBUILD_smoke=OFF \
  -DBUILD_java=OFF \
  ..
popd

# smp build not recommended (upstream)
make -C %{_target_platform}

%install
rm -rf %{buildroot}
make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

rm -rf %{buildroot}%{_kde4_datadir}/sip/PyKDE4/polkitqt/ \
       %{buildroot}%{_kde4_appsdir}/pykde4/examples/polkitqtExamples/

# fix multilb conflict, similar to PyQt4's http://bugzilla.redhat.com/509415
rm -fv %{buildroot}%{_bindir}/pykdeuic4
mv %{buildroot}%{python_sitearch}/PyQt4/uic/pykdeuic4.py \
   %{buildroot}%{_bindir}/pykdeuic4
ln -s %{_bindir}/pykdeuic4 \
      %{buildroot}%{python_sitearch}/PyQt4/uic/pykdeuic4.py

# install pykde4 examples under correct directory
mkdir -p %{buildroot}%{_docdir}
rm -f %{buildroot}%{_kde4_appsdir}/pykde4/examples/*.py?
mv %{buildroot}%{_kde4_appsdir}/pykde4 %{buildroot}%{_docdir}/

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files -n PyKDE4
%defattr(-,root,root,-)
%doc COPYING AUTHORS ChangeLog NEWS README
%dir %{_docdir}/pykde4
%{python_sitearch}/PyKDE4/
%{python_sitearch}/PyQt4/uic/widget-plugins/kde4.py*
%{_kde4_libdir}/kde4/kpythonpluginfactory.so
%exclude %{python_sitearch}/PyKDE4/akonadi.so

%files -n PyKDE4-akonadi
%defattr(-,root,root,-)
%{python_sitearch}/PyKDE4/akonadi.so

%files -n PyKDE4-devel
%defattr(-,root,root,-)
%{_kde4_bindir}/pykdeuic4
%{python_sitearch}/PyQt4/uic/pykdeuic4.py*
%{_docdir}/pykde4/examples/
%{_kde4_datadir}/sip/PyKDE4/

%files -n kross-python
%defattr(-,root,root,-)
%{_kde4_libdir}/kde4/krosspython.so

%changelog
* Mon Jun 28 2010 Than Ngo <than@redhat.com> 4.3.4-5
- Resolves: bz#597271, drop WebKit support in Qt

* Tue Mar 30 2010 Than Ngo <than@redhat.com> - 4.3.4-4
- rebuilt against qt 4.6.2

* Thu Feb 25 2010 Than Ngo <than@redhat.com> - 4.3.4-3
- fix license

* Sat Dec 12 2009 Than Ngo <than@redhat.com> - 4.3.4-2
- cleanup

* Tue Dec 01 2009 Than Ngo <than@redhat.com> - 4.3.4-1
- 4.3.4

* Mon Nov 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-4
- Requires: sip-api(%%_sip_api_major) >= %%_sip_api

* Wed Nov 11 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-3
- pyqt4_version 4.6.1 (everywhere)
- drop qt46 patch (not working yet)

* Fri Nov 06 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.3-2
- try to fix build with Qt 4.6 (f13+)

* Sat Oct 31 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.3-1
- 4.3.3

* Mon Oct 26 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.2-3
- sync archs supporting csharp(mono)

* Sun Oct 25 2009 Ben Boeckel <MathStuf@gmail.com> - 4.3.2-2
- fix bz#530667

* Wed Oct 07 2009 Than Ngo <than@redhat.com> - 4.3.2-1
- 4.3.2
- fix bz#527464

* Fri Sep 25 2009 Than Ngo <than@redhat.com> - 4.3.1-4
- rhel cleanup

* Thu Sep 03 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.1-3
- also disable polkit-qt on EL6+
- also remove polkit-qt sip files and examples on F12+/EL6+

* Thu Sep 03 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.3.1-2
- only (temporarily) disable Falcon on F12+
- drop bindings for polkit-qt on F12+ (PolicyKit 0.9 is going away)
- remove unused (commented out) patch

* Fri Aug 28 2009 Than Ngo <than@redhat.com> - 4.3.1-1
- 4.3.1
- temporarily disable Falcon bindings (build fails with Falcon 0.9.x)

* Mon Aug 17 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.0-5
- re-enable php bindings (rawhide)

* Tue Aug 11 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.0-4.1
- BR: qscintilla-devel >= 2.4

* Sun Aug 09 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.3.0-4
- manually specify PYTHON_LIBRARIES (and friends) (#516386)

* Mon Aug 03 2009 Than Ngo <than@redhat.com> - 4.3.0-3
- respin

* Sat Aug 01 2009 Rex Dieter <rdieter@fedoraproject.org> 4.3.0-2
- workaround pykdeuic4 upgrade brokenness (introduced in 4.2.98)

* Thu Jul 30 2009 Than Ngo <than@redhat.com> - 4.3.0-1
- 4.3.0
- more pykdeuic4 and related multilib love (kdebug#198162)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.98-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Than Ngo <than@redhat.com> - 4.2.98-1
- 4.3rc3 

* Mon Jul 20 2009 Than Ngo <than@redhat.com> - 4.2.96-5
- add correct check for php version

* Mon Jul 20 2009 Than Ngo <than@redhat.com> - 4.2.96-4
- allow for build php-5.2.x

* Mon Jul 20 2009 Than Ngo <than@redhat.com> - 4.2.96-3
- fix build issue with php-5.3.x

* Thu Jul 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.96-2
- fix pykdeuic4-related install bits (kdebug#198162)
- pyqt4_version 4.5.2
- License: LGPLv2+

* Fri Jul 10 2009 Than Ngo <than@redhat.com> - 4.2.96-1
- 4.3rc2

* Fri Jun 26 2009 Than Ngo <than@redhat.com> - 4.2.95-1
- 4.3rc1

* Mon Jun 22 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.2.90-3
- make the Python plugin factory work without python-devel

* Wed Jun 17 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.90-2
- rework old-PyQt4 patch 

* Wed Jun 03 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.90-1
- KDE-4.3 beta2 (4.2.90)

* Thu May 21 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.85-2
- respin against PyQt-4.5

* Wed May 20 2009 Than Ngo <than@redhat.com> - 4.2.85-1
- 4.2.85 (4.3 beta1)
- build fixes backported from trunk by Nicolas Lécureuil <neoclust@mandriva.org>
- revert change which requires PyQt4 4.5 (Kevin Kofler)
- fix build issue with gcc-4.4

* Tue Apr 21 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.2.2-5
- F11+: enable csharp on ppc64

* Wed Apr 15 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 4.2.2-4
- reenable csharp on ppc

* Wed Apr 08 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.2-3
- enable csharp only on archs supported by mono (ie, drop ppc)

* Wed Apr 01 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.2-2
- relax dep on kdepimlibs-akonadi

* Tue Mar 31 2009 Lukáš Tinkl <ltinkl@redhat.com> - 4.2.2-1
- KDE 4.2.2

* Sat Mar 28 2009 Ben Boeckel <Mathstuf@gmail.com> - 4.2.1-8
- Only install the .pc file if building csharp/qyoto support

* Sat Mar 28 2009 Ben Boeckel <Mathstuf@gmail.com> - 4.2.1-7
- Fix install line

* Sat Mar 28 2009 Ben Boeckel <Mathstuf@gmail.com> - 4.2.1-6
- Create pkgconfig directory

* Sat Mar 28 2009 Ben Boeckel <Mathstuf@gmail.com> - 4.2.1-5
- Ship qyoto.pc file as well
- Add dependency on mono-devel from qyoto-devel

* Fri Mar 20 2009 Ben Boeckel <Mathstuf@gmail.com> - 4.2.1-4
- Don't enable csharp on ppc64

* Fri Mar 20 2009 Ben Boeckel <Mathstuf@gmail.com> - 4.2.1-3
- Clean up conditionals
- Enable PHP and C# bindings

* Wed Mar 18 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.1-2
- fix typos in Provides: kross(python)

* Fri Feb 27 2009 Than Ngo <than@redhat.com> - 4.2.1-1
- 4.2.1

* Wed Feb 25 2009 Than Ngo <than@redhat.com> - 4.2.0-7
- fix build issue again qt-4.5

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 20 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-5
- enable PyKDE4-akonadi subpkg

* Mon Feb 16 2009 Rex Dieter <rdieter@fedoraproject.org> - 4.2.0-4
- include toggle for PyKDE4-akonadi subpkg (not enabled)
- PyKDE4: move examples to -devel pkg
- PyKDE4: make dep on PyQt4 versioned
- PyKDE4: Provides: -akonadi, Requires: kdepimlibs-akonadi
- PyKDE4(-devel): adjust description/summary

* Sun Feb 9 2009 Ben Boeckel <MathStuf@gmail.com> - 4.2.0-3
- Enabled Falcon for Kross (min version met)

* Sat Jan 24 2009 Ben Boeckel <MathStuf@gmail.com> - 4.2.0-2
- Removed Ruby examples; killed upstream

* Thu Jan 22 2009 Than Ngo <than@redhat.com> - 4.2.0-1
- 4.2.0

* Thu Jan 15 2009 Rex Dieter <rdieter@fedoraproject.org> 4.1.96-5
- toggle for QtRuby/kde-plasma-ruby bootstrap

* Thu Jan 15 2009 Rex Dieter <rdieter@fedoraproject.org> 4.1.96-4
- update %%description/%%summaries for new (sub)pkgs
- use versioned Provides/Requires all over
- BR: akonadi-devel kdegraphics-devel
- don't package kde-plasma-ruby-* (cmake error "rbuic4 not found")

* Thu Jan 15 2009 Ben Boeckel <MathStuf@gmail.com> 4.1.96-3
- Fixed QtRuby version
- Moved QtRuby tools to QtRuby-devel

* Wed Jan 14 2009 Ben Boeckel <MathStuf@gmail.com> 4.1.96-2
- Split out Ruby bindings and Kross modules

* Wed Jan 07 2009 Than Ngo <than@redhat.com> - 4.1.96-1
- 4.2rc1

* Fri Dec 12 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.85-2
- reenable smoke, ruby
- disable NepomukSmoke for now: it wasn't actually used (the corresponding
  Ruby binding is disabled by default and we don't build the C# bindings) and it
  depends on nepomukquery libs from kdebase (which also means we need to sort
  out the -devel symlink mess there first)

* Fri Dec 12 2008 Than Ngo <than@redhat.com> 4.1.85-1
- 4.2beta2

* Mon Dec 01 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.80-5
- rebuild for Python 2.6

* Mon Dec 01 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.80-4
- don't require kdebase-workspace(-devel)

* Thu Nov 27 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.80-3
- BR plasma-devel instead of kdebase-workspace-devel
- disable smoke,ruby (for now, busted)

* Thu Nov 20 2008 Than Ngo <than@redhat.com> 4.1.80-2
- merged

* Thu Nov 20 2008 Lorenzo Villani <lvillani@binaryhelix.net> - 4.1.80-1
- 4.1.80
- BR cmake >= 2.6.2
- make install/fast

* Mon Nov 17 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-2.1
- respin (qscintilla)

* Wed Nov 12 2008 Than Ngo <than@redhat.com> 4.1.3-1
- 4.1.3

* Mon Sep 29 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-2
- make VERBOSE=1
- respin against new(er) kde-filesystem

* Fri Sep 26 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.2-1
- 4.1.2

* Thu Sep 25 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.1-2
- respin (for qscintilla)

* Fri Aug 29 2008 Than Ngo <than@redhat.com> 4.1.1-1
- 4.1.1

* Mon Jul 28 2008 Than Ngo <than@redhat.com> -  4.1.0-5
- respun
- get rid of kdebindings-4.1.0-kde#167450.patch that is included in new upstream

* Sat Jul 26 2008 Rex Dieter <rdieter@fedoraproject.org> 4.1.0-4.1
- BR: qscintilla-devel >= 2.2

* Fri Jul 25 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.0-4
- fix Python and Ruby bindings overwriting each other (#456722, kde#167450)

* Fri Jul 25 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.1.0-3
- drop unneeded BR kdegraphics4-devel (Ruby Okular bindings disabled by default)
- add BR kdepimlibs-devel for Python Akonadi bindings

* Fri Jul 25 2008 Than Ngo <than@redhat.com> 4.1.0-2
- respun

* Wed Jul 23 2008 Than Ngo <than@redhat.com> 4.1.0-1
- 4.1.0

* Fri Jul 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.99-1
- 4.0.99

* Mon Jul 14 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-3
- re-enable smoke (patched), ruby

* Mon Jul 14 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-2
- omit smoke, ruby bindings (build failures, sorting out upstream)
- -devel: -BR: PyQt4-devel

* Fri Jul 11 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.98-1
- 4.0.98

* Sun Jul 06 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.85-1
- 4.0.85

* Sat Jun 28 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.84-2
- fix Python bindings for Phonon and Soprano

* Fri Jun 27 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.84-1
- 4.0.84

* Sat Jun 21 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.83-4
- fix PyKDE4-devel to require PyKDE4 rather than itself

* Sat Jun 21 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.83-3
- reenable Ruby again
- add missing Epoch for minimum kdegraphics-devel version requirement
- fix CMake target name conflict between Ruby and Python bindings
- fix file list for Ruby

* Fri Jun 20 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.83-2
- reenable smoke again (keep ruby off for now)
- drop explicit ENABLE_SMOKEKDEVPLATFORM=OFF (now off by default)
- add BR kdegraphics-devel for the Smoke Okular bindings
- fix file list

* Thu Jun 19 2008 Than Ngo <than@redhat.com> 4.0.83-1
- 4.0.83 (beta2)

* Wed Jun 18 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.82-3
- revert, more borkage.

* Tue Jun 17 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.82-2
- reenable smoke and ruby, set ENABLE_SMOKEKDEVPLATFORM=OFF (no kdevplatform)

* Sun Jun 15 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.82-1
- 4.0.82
- omit ruby, smoke (busted) => no -devel subpkg (for now)
- PyKDE4(-devel) subpkgs

* Tue May 27 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.80-2
- disable php-qt for now
- apply PyKDE4 and smokekde build fixes from upstream
- update file lists (comment out smokeplasma, add new smoke/ruby files)
- fix incorrect libdir on lib64 platforms

* Mon May 26 2008 Than Ngo <than@redhat.com> 4.0.80-1
- 4.1 beta1

* Wed May 07 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.72-1
- update to 4.0.72
- add BR soprano-devel
- update file list to include plasma-ruby stuff

* Thu Apr 03 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-3
- rebuild (again) for the fixed %%{_kde4_buildtype}

* Mon Mar 31 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.3-2
- Rebuild for NDEBUG

* Fri Mar 28 2008 Than Ngo <than@redhat.com> 4.0.3-1
- 4.0.3

* Mon Mar 03 2008 Than Ngo <than@redhat.com> 4.0.2-5
- respin

* Sat Mar 01 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.2-3
- apply upstream build fixes for Qt 4.3.4 (rev 780996)
- remove no longer existing protected KService::accessServiceTypes from PyKDE4

* Fri Feb 29 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.0.2-2
- drop lib64 patches (fixed upstream)

* Thu Feb 28 2008 Than Ngo <than@redhat.com> 4.0.2-1
- 4.0.2

* Thu Jan 31 2008 Rex Dieter <rdieter@fedoraproject.org> 4.0.1-1
- 4.0.1
- Provides: PyKDE4(-devel)
- BR: qscintilla-devel >= 2

* Tue Jan 08 2008 Rex Dieter <rdieter[AT]fedoraproject.org> 4.0.0-1
- kde-4.0.0

* Thu Jan 03 2008 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-8
- smoke.h is in %%{_includedir}, not %%{_kde4_includedir}

* Wed Dec 12 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-7
- rebuild for changed _kde4_includedir

* Tue Dec 11 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-6
- use patch to override PYTHON_SITE_PACKAGES_DIR (cmake -D doesn't work)

* Tue Dec 11 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-5
- override PYTHON_SITE_PACKAGES_DIR

* Tue Dec 11 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-4
- rewrite libsmokeqt-lib64 patch so it actually works
- add PyKDE4 files to file list
- specify minimum versions of sip-devel and PyQt4-devel
- require PyQt4 in main package, PyQt4-devel in -devel
- fix unowned Qt and KDE directories under ruby_sitelib

* Tue Dec 11 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-3
- omit BR: qwt-devel for now, causes build failure in smokeqt
- add BRs: sip-devel PyQt4-devel for PyKDE4

* Tue Dec 11 2007 Kevin Kofler <Kevin@tigcc.ticalc.org> 3.97.0-2
- remove X11 BRs now Required by kdelibs-devel
- add BR: qwt-devel
- fix libsmokeqt being in /usr/lib even on 64-bit arches
- use ruby_sitelib and ruby_sitearch properly

* Mon Dec 10 2007 Than Ngo <than@redhat.com> 3.97.0-1
- 3.97.0

* Sun Nov 18 2007 Sebastian Vahl <fedora@deadbabylon.de> 3.96.0-1
- Initial version for Fedora
