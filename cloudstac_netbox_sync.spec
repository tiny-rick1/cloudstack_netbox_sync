%define name cni
%define version 1.0
%define unmangled_version 1.0
%define unmangled_version 1.0
%define release 1

Summary: Tool for synchronizing cloudstack host to netbox
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv3
Requires: cs
Requires: pynetbox
Requires: python36-six
Requires: python36-pytz
Requires: python36-requests
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: rnowak <remigiusz.adam.nowak@gmail.com>

%description
Tool for synchronizing cloudstack host to netbox

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p %{buildroot}/etc/cni/
install -m 755 settings.ini.example %{buildroot}/etc/cni/settings.ini
%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%config(noreplace) /etc/cni/settings.ini
