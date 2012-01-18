%if %mdkversion <= 200910
%bcond_without ksmarttray
%else
%bcond_with    ksmarttray
%endif
%bcond_without smart_update
%bcond_without smart_applet

Name:		smart
Version:	1.4.1
Release:	1
Epoch:		1
Group:		System/Configuration/Packaging
Summary:	Next generation package handling tool
License:	GPLv2+
URL:		http://smartpm.org
Source0:	http://labix.org/download/smart/%{name}-%{version}.tar.bz2
Source1:	smart-mandriva-distro.py
Source2:	smart.console
Source4:	smart-package-manager.desktop
Source6:	smart-newer.py
Source7:	smart-install.desktop
Source8:	smart-applet.desktop
Source9:	smart-applet.png
Patch0:		smart-1.4.1-disable-pycurl-check-for-now.patch
Patch1:		smart-1.4.1-enable-distepoch.patch
Patch2:		smart-1.4.1-applet.patch

BuildRequires:	rpm-mandriva-setup
BuildRequires:	desktop-file-utils
# required by test suite
BuildRequires:	dpkg
BuildRequires:	python-rpm
Requires:	python-rpm python-liblzma >= 0.4.0
Requires:	usermode-consoleonly
%ifarch %{ix86}
Requires:	python-psyco
%endif
Suggests:	python-curl
BuildRequires:	python-devel

%description
Smart Package Manager is a next generation package handling tool.

%package	gui
Summary:	Smart GTK user interface
Group:		System/Configuration/Packaging
Requires(post):	desktop-file-utils
Requires(postun): desktop-file-utils
Requires:	%{name} = %{EVRD}
Requires:	pygtk2.0

%description	gui
Smart GTK user interface.

%if %{with smart_update}
%package	update
Summary:	Allows execution of 'smart update' by normal users (suid)
Group:		System/Configuration/Packaging
Requires:	%{name} = %{EVRD}

%description	update
Allows execution of 'smart update' by normal users through a
special suid command.
%endif

%if %{with smart_applet}
%package	applet
Summary:	Smart system tray applet
Group:		System/Configuration/Packaging
Requires:	%{name} = %{EVRD}
Requires:	gnome-python

%description	applet
Smart system tray applet.
%endif

%if %{with ksmarttray}
%package -n	ksmarttray
Summary:	KDE tray program for watching updates with Smart Package Manager
Group:		System/Configuration/Packaging
Requires(post):	desktop-file-utils
Requires(postun): desktop-file-utils
Requires:	%{name}-update = %{EVRD}
BuildRequires:	kdelibs-devel
BuildRequires:	popt
BuildRequires:	rpm-devel
 
%description -n ksmarttray
KDE tray program for watching updates with Smart Package Manager.
%endif

%prep
%setup -q
%patch0 -p1 -b .disable_curl~
%patch1 -p1 -b .distepoch~
%patch2 -p1 -b .applet~
cp %{SOURCE9} contrib/smart-applet

%build
%setup_compile_flags
%make

%if %{with ksmarttray}
pushd contrib/ksmarttray
make -f admin/Makefile.common

%configure_kde3
%make
popd
%endif

%if %{with smart_update}
pushd contrib/smart-update
%make
popd
%endif

%check
make test

%install
%makeinstall_std

install -m644 %{SOURCE1} -D %{buildroot}%{_prefix}/lib/smart/distro.py

install -m644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/security/console.apps/smart-root

ln -sf consolehelper %{buildroot}%{_bindir}/smart-root

mkdir -p %{buildroot}%{_sysconfdir}/pam.d

cat > %{buildroot}%{_sysconfdir}/pam.d/smart-root <<EOF
#%PAM-1.0
auth       sufficient   pam_rootok.so
auth       sufficient   pam_timestamp.so
auth       include      system-auth
account    required     pam_permit.so
session    required     pam_permit.so
session    optional     pam_timestamp.so
session    optional     pam_xauth.so
EOF

mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install \
        --dir %{buildroot}%{_datadir}/applications \
	%{SOURCE4}

install -m644 smart/interfaces/images/smart.png -D %{buildroot}%{_datadir}/pixmaps/smart-package-manager.png
mkdir -p %{buildroot}%{_localstatedir}/lib/smart/channels

install -m644 %{SOURCE6} -D %{buildroot}%{py_platsitedir}/%{name}/commands/newer.py

%if %{with smart_update}
install -m755 contrib/smart-update/smart-update -D %{buildroot}%{_bindir}/smart-update
%endif

%if %{with smart_applet}
desktop-file-install \
	--dir %{buildroot}%{_datadir}/applications \
	%{SOURCE8}
install -m755 contrib/smart-applet/smart-applet.py  -D %{buildroot}%{_bindir}/smart-applet
install -m644 contrib/smart-applet/smart-applet.png  -D %{buildroot}%{_datadir}/pixmaps/smart-applet.png
install -m644 contrib/smart-applet/smart-helper.pam %{buildroot}%{_sysconfdir}/pam.d/smart-helper
install -m644 contrib/smart-applet/smart-helper.helper %{buildroot}%{_sysconfdir}/security/console.apps/smart-helper
ln -sf consolehelper %{buildroot}%{_bindir}/smart-helper
%endif

%if %{with ksmarttray}
pushd contrib/ksmarttray
%makeinstall_std
popd

install -m755 contrib/servicemenus/kde_add_smart_channel.sh -D %{buildroot}%{_kde3_bindir}/kde_add_smart_channel.sh
mkdir -p %{buildroot}%{_kde3_datadir}/apps/konqueror/servicemenus
desktop-file-install \
        --dir %{buildroot}%{_kde3_datadir}/apps/konqueror/servicemenus \
        contrib/servicemenus/add_smart_channel.desktop

# XDG menu entry
mkdir -p %{buildroot}%{_kde3_datadir}/applications/
cat > ksmarttray.desktop << EOF
[Desktop Entry]
Name=KSmartTray
Comment=KDE Tray widget for updating RPM files
Exec=%{_kde3_bindir}/ksmarttray %%F
Icon=smart-package-manager
Type=Application
Categories=Qt;KDE;Settings;PackageManager;
EOF

%{_bindir}/desktop-file-install \
        --dir %{buildroot}%{_kde3_datadir}/applications  \
        ksmarttray.desktop
%endif

%find_lang %{name}

%if 0
%post gui
xdg-mime default smart-install.desktop application/x-rpm
xdg-mime default smart-install.desktop application/x-redhat-package-manager
%endif

%files -f %{name}.lang
%defattr(0644,root,root,0755)
%doc HACKING README TODO IDEAS doc/*.css doc/*.html
%config(noreplace) %{_sysconfdir}/security/console.apps/smart-root
%config(noreplace) %{_sysconfdir}/pam.d/smart-root
%attr(0755,root,root)%{_bindir}/%{name}
%attr(0755,root,root)%{_bindir}/%{name}-root
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/distro.py
%dir %{py_platsitedir}/smart
%{py_platsitedir}/smart/*
%{py_platsitedir}/*.egg-info
%exclude %{py_platsitedir}/smart/interfaces/gtk
%dir %{_localstatedir}/lib/smart/channels
%{_mandir}/*/*

%files gui
%defattr(0644,root,root,0755)
%{_datadir}/applications/smart-package-manager.desktop
%{_datadir}/pixmaps/smart-package-manager.png
%{py_platsitedir}/smart/interfaces/gtk

%if %{with smart_update}
%files update
%attr(4755,root,root) %{_bindir}/smart-update
%endif

%if %{with smart_applet}
%files applet
%config(noreplace) %{_sysconfdir}/security/console.apps/smart-helper
%config(noreplace) %{_sysconfdir}/pam.d/smart-helper
%attr(4755,root,root) %{_bindir}/smart-applet
%{_bindir}/smart-helper
%{_datadir}/applications/smart-applet.desktop
%{_datadir}/pixmaps/smart-applet.png
%endif

%if %{with ksmarttray}
%files -n ksmarttray
%{_kde3_bindir}/ksmarttray
%{_kde3_bindir}/kde_add_smart_channel.sh
%{_kde3_datadir}/apps/ksmarttray
%{_kde3_datadir}/applications/ksmarttray.desktop
%{_kde3_datadir}/apps/konqueror/servicemenus/add_smart_channel.desktop
%{_kde3_iconsdir}/hicolor/48x48/apps/ksmarttray.png
%endif
