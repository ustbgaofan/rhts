%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name: rhts
Summary: Automated software testing
Version: 4.55
Release: 1%{?dist}
Group: Development/Libraries
License: GPL
Source0: http://fedorahosted.org/releases/r/h/%{name}-%{version}.tar.gz
Buildroot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
BuildRequires: python-devel
%if 0%{?rhel}%{?fedora} > 4
BuildRequires: selinux-policy-devel
%endif

%description
This package is intended for people creating and maintaining tests, and
contains (or requires) the runtime components of the test system for 
installation on a workstation, along with development tools.

%package devel
Summary: Testing
Group: Development/Libraries
Obsoletes: rhts-rh-devel
Provides: rhts-rh-devel
Requires: rhts-test-env = %{version}
Requires: rhts-python = %{version}
Requires: beaker-client
Requires: tar
Requires: sed
Requires: make
Requires: rpm-build
# beaker-wizard was moved from here to beaker-client in 0.9.4
Conflicts: beaker-client < 0.9.4

%description devel
This package contains components of the test system used when running 
tests, either on a developer's workstation, or within a lab.

%package test-env
Summary: Testing API
Group: Development/Libraries
Obsoletes: rhts-testhelpers
Provides: rhts-testhelpers
Obsoletes: rhts-test-env-lab
Provides: rhts-test-env-lab
Obsoletes: rhts-devel-test-env
Provides: rhts-devel-test-env
Obsoletes: rhts-legacy
Provides: rhts-legacy
Requires: rhts-python = %{version}
Requires: beakerlib
Requires: make
%if 0%{?rhel}%{?fedora} > 4
Requires(post): policycoreutils
%endif

%description test-env
This package contains components of the test system used when running 
tests, either on a developer's workstation, or within a lab.

%package python
Summary:        Python module for test development
Group:          Development/Libraries
Conflicts:      rhts-test-env < 4.44

%description python
This package provides the rhts Python module, for use by rhts scripts and 
related programs.

%prep
%setup -q


%build
[ "$RPM_BUILD_ROOT" != "/" ] && [ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;
pushd python-modules
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
popd

%install
DESTDIR=$RPM_BUILD_ROOT make install
pushd python-modules 
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd

%if 0%{?rhel}%{?fedora} > 4
# Build RHTS Selinux Testing Policy 
pushd selinux
# If dist specific selinux module is present use that.
# Why:
#  newer releases may introduce new selinux macros which are not present in
#  older releases.  This means that a module built under the newer release
#  will no longer load on an older release.  
# How:
#  Simply issue the else statement on the older release and commit the 
#  policy to git with the appropriate dist tag.
if [ -e "rhts%{?dist}.pp" ]; then
    install -p -m 644 -D rhts%{?dist}.pp $RPM_BUILD_ROOT%{_datadir}/selinux/packages/%{name}/rhts.pp
else
    make -f %{_datadir}/selinux/devel/Makefile
    install -p -m 644 -D rhts.pp $RPM_BUILD_ROOT%{_datadir}/selinux/packages/%{name}/rhts.pp
fi
popd
%endif

# Legacy support.
ln -s rhts-db-submit-result $RPM_BUILD_ROOT/usr/bin/rhts_db_submit_result
ln -s rhts-environment.sh $RPM_BUILD_ROOT/usr/bin/rhts_environment.sh
ln -s rhts-sync-set $RPM_BUILD_ROOT/usr/bin/rhts_sync_set
ln -s rhts-sync-block $RPM_BUILD_ROOT/usr/bin/rhts_sync_block
ln -s rhts-submit-log $RPM_BUILD_ROOT/usr/bin/rhts_submit_log
mkdir -p $RPM_BUILD_ROOT/mnt/scratchspace
mkdir -p $RPM_BUILD_ROOT/mnt/testarea

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && [ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;

%post test-env
%if 0%{?rhel}%{?fedora} > 4
if [ "$1" -le "1" ] ; then # First install
semodule -i %{_datadir}/selinux/packages/%{name}/rhts.pp || :
fi
%endif

%preun test-env
%if 0%{?rhel}%{?fedora} > 4
if [ "$1" -lt "1" ] ; then # Final removal
semodule -r rhts || :
fi
%endif

%postun test-env
%if 0%{?rhel}%{?fedora} > 4
if [ "$1" -ge "1" ] ; then # Upgrade
semodule -i %{_datadir}/selinux/packages/%{name}/rhts.pp || :
fi
%endif

%files test-env
%defattr(-,root,root)
%attr(0755, root, root)%{_bindir}/rhts-db-submit-result
%attr(0755, root, root)%{_bindir}/rhts_db_submit_result
%attr(0755, root, root)%{_bindir}/rhts-environment.sh
%attr(0755, root, root)%{_bindir}/rhts_environment.sh
%attr(0755, root, root)%{_bindir}/rhts-run-simple-test
%attr(0755, root, root)%{_bindir}/rhts-report-result
%attr(0755, root, root)%{_bindir}/rhts-submit-log
%attr(0755, root, root)%{_bindir}/rhts_submit_log
%attr(0755, root, root)%{_bindir}/rhts-sync-block
%attr(0755, root, root)%{_bindir}/rhts_sync_block
%attr(0755, root, root)%{_bindir}/rhts-sync-set
%attr(0755, root, root)%{_bindir}/rhts_sync_set
%attr(0755, root, root)%{_bindir}/rhts-recipe-sync-block
%attr(0755, root, root)%{_bindir}/rhts-recipe-sync-set
%attr(0755, root, root)%{_bindir}/rhts-reboot
%attr(0755, root, root)%{_bindir}/rhts-backup
%attr(0755, root, root)%{_bindir}/rhts-restore
%attr(0755, root, root)%{_bindir}/rhts-system-info
%attr(0755, root, root)%{_bindir}/rhts-abort
%attr(0755, root, root)%{_bindir}/rhts-test-runner.sh
%attr(0755, root, root)%{_bindir}/rhts-test-checkin
%attr(0755, root, root)%{_bindir}/rhts-test-update
%attr(0755, root, root)%{_bindir}/rhts-extend
%attr(0755, root, root)%{_bindir}/rhts-power
%{_datadir}/%{name}/lib/rhts-make.include
%{_datadir}/%{name}/failurestrings
%{_datadir}/%{name}/falsestrings
%if 0%{?rhel}%{?fedora} > 4
%{_datadir}/selinux/packages/%{name}/rhts.pp
%endif
/mnt/scratchspace
%attr(1777,root,root)/mnt/testarea
%doc doc/README

%files devel
%defattr(-,root,root)
%attr(0755, root, root)%{_bindir}/rhts-lint
%attr(0755, root, root)%{_bindir}/rhts-run-package
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-build-package
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-snake-template
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-generate-specfile
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-get-current-tag
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-get-next-tag
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-get-test-package-name
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-get-version-info
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-tag-release
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-test-import
%attr(0755, root, root)%{_libexecdir}/rhts/rhts-mk-diff-since-last-tag
%doc doc/Makefile.template
%doc doc/runtest.sh.template

%files python
%defattr(-,root,root)
%{python_sitelib}/%{name}*

%changelog
* Fri Apr 05 2013 Dan Callaghan <dcallagh@redhat.com> 4.55-1
- Import the SSL error exception conditionally (qwan@redhat.com)
- Add 'cut here' and 'Badness at' as the kernel failure strings
  (pbunyan@redhat.com)

* Mon Jan 14 2013 Nick Coghlan <ncoghlan@redhat.com> 4.54-1
- use RHEL6 selinux policy when %%{dist} is .el6 as well (dcallagh@redhat.com)
- Fix dist tag for selinux policy load for RHEL 6.0 (asaha@redhat.com)
- don't hide %%post script errors (bpeck@redhat.com)
- Prevent 'basename' error spew when task does not have remote git.
  (asaha@redhat.com)

* Wed Nov 07 2012 Dan Callaghan <dcallagh@redhat.com> 4.53-1
- Copy procfs and sysfs files for uploading (qwan@redhat.com)
- use stricter glob pattern when searching for current tag
  (dcallagh@redhat.com)

* Thu Oct 18 2012 Dan Callaghan <dcallagh@redhat.com> 4.52-3
- Fix package name regex in mk-generate-specfile
  (Nikolai.Kondrashov@redhat.com)
- Use bash explicitly for bash scripts (Nikolai.Kondrashov@redhat.com)

* Thu Oct 04 2012 Dan Callaghan <dcallagh@redhat.com> 4.52-2
- fix for bz526348 (bpeck@redhat.com)

* Fri Sep 28 2012 Dan Callaghan <dcallagh@redhat.com> 4.52-1
- moved beaker-wizard to beaker-client package (dcallagh@redhat.com)
- add ability to timeout in rhts-sync-block (bpeck@redhat.com)
- rhts-sync-block -- catching state from arbitrary machine (bpeck@redhat.com)
- rhts selinux module fails to load on RHEL-7.0-20120711.2 (bpeck@redhat.com)

* Fri Aug 03 2012 Bill Peck <bpeck@redhat.com> 4.51-1
- test env command for sending power commands (dcallagh@redhat.com)
- clean out some old junk (dcallagh@redhat.com)
- AVC subtest provide incorrect results on RHEL7 (bpeck@redhat.com)

* Thu Jul 12 2012 Bill Peck <bpeck@redhat.com> 4.50-1
- beaker-wizard: Abort when environment is not ready [BZ#838575]
  (psplicha@redhat.com)
- rhts-lint: exit non-zero if errors or warnings are found
  (dcallagh@redhat.com)
- accurate exit status for `make bkradd` (dcallagh@redhat.com)
- tito config for releasing in dist-git (dcallagh@redhat.com)

* Thu Jun 21 2012 Bill Peck <bpeck@redhat.com> 4.49-1
- /usr/bin/rhts-backup and /usr/bin/rhts-restore doesn't preserve selinux
  context (bpeck@redhat.com)
- beaker-wizard: Update valid releases [BZ#828338] (psplicha@redhat.com)
- beaker-wizard: Do not replace existing files with attachments [BZ#797244]
  (isenfeld@redhat.com)
- BeakerLib has moved (long time ago) to /usr/share (psplicha@redhat.com)

* Thu Apr 12 2012 Bill Peck <bpeck@redhat.com> 4.48-1
- rhts-mk-get-version-info should use $TESTVERSION (bpeck@redhat.com)

* Mon Mar 26 2012 Bill Peck <bpeck@redhat.com> 4.47-1
- rhts-test-runner overrides PATH adjusted by tortilla wrapper
  (bpeck@redhat.com)

* Wed Feb 29 2012 Bill Peck <bpeck@redhat.com> 4.46-1
- Added consistent identifier for bugs but test name remains the same
  (isenfeld@redhat.com)
- Update the beaker-wizard to work with Git (psplicha@redhat.com)

* Thu Feb 23 2012 Bill Peck <bpeck@redhat.com> 4.45-1
- Add make to dependencies (mcsontos@redhat.com)

* Fri Jan 27 2012 Dan Callaghan <dcallagh@redhat.com> 4.44-2
- add Conflicts to rhts-python for old rhts-test-env (dcallagh@redhat.com)

* Tue Jan 24 2012 Bill Peck <bpeck@redhat.com> 4.44-1
- [RFE] add Provides: ability to test Makefile. (bpeck@redhat.com)
- split rhts python module into its own subpackage (dcallagh@redhat.com)
- internal variable value not quoted (dcallagh@redhat.com)

* Mon Nov 14 2011 Bill Peck <bpeck@redhat.com> 4.43-1
- test times can be longer than 6 hours.  For example: reservesys
  (bpeck@redhat.com)

* Fri Nov 04 2011 Bill Peck <bpeck@redhat.com> 4.42-1
- update testinfo.py to be consistent with the version in beaker
  (dcallagh@redhat.com)
- fix use of tmpnam in unit tests (dcallagh@redhat.com)
- fix parsing of Destructive field in testinfo (dcallagh@redhat.com)
- TestTime with no suffix means seconds (dcallagh@redhat.com)
- Slight change in error message when uploading file (rmancy@redhat.com)

* Fri Sep 30 2011 Bill Peck <bpeck@redhat.com> 4.41-1
- rhts-create-new-test is not needed anymore (bpeck@redhat.com)

* Fri Sep 02 2011 Bill Peck <bpeck@redhat.com> 4.40-1
- rhts selinux module fails to load on RHEL6.0 (bpeck@redhat.com)

* Tue Aug 23 2011 Bill Peck <bpeck@redhat.com> 4.39-1
- make rpm doesn't take version into account when run on directory outside
  version control (bpeck@redhat.com)
- add missing Requires for rhts-devel (dcallagh@redhat.com)
- Owner field should be mandatory (dcallagh@redhat.com)
- beaker-wizard: Use  instead of  in the templates (psplicha@redhat.com)
- better regexp for validating Owner: field (dcallagh@redhat.com)
- beaker-wizard: Description may not contain colons [BZ#722413]
  (psplicha@redhat.com)
- beaker-wizard: updated links (psplicha@redhat.com)
- beaker-wizard: chmod scripts only when necessary [BZ#709753]
  (psplicha@redhat.com)
- Write pending changes to disk (mcsontos@redhat.com)

* Thu Jun 02 2011 Bill Peck <bpeck@redhat.com> 4.38-1
- fix Makefile to install beaker-wizard (bpeck@redhat.com)

* Thu Jun 02 2011 Bill Peck <bpeck@redhat.com> 4.37-1
- Renamed rhts-wizard to beaker-wizard (bpeck@redhat.com)

* Wed May 11 2011 Bill Peck <bpeck@redhat.com> 4.36-1
- need to dereference tags now that they are heavyweight (dcallagh@redhat.com)
- fallback logic when no annotated tags are found (dcallagh@redhat.com)
- Verify the tags hash matches upstream (bpeck@redhat.com)
- Revert "fix checking of remote tags to be consistent with make package."
  (bpeck@redhat.com)

* Tue May 10 2011 Bill Peck <bpeck@redhat.com> 4.35-1
- fix checking of remote tags to be consistent with make package.
  (bpeck@redhat.com)

* Fri May 06 2011 Bill Peck <bpeck@redhat.com> 4.34-1
- remove * from tagcommiter. (bpeck@redhat.com)

* Mon May 02 2011 Bill Peck <bpeck@redhat.com> 4.33-1
- Fix git tagging to work on new repos with no current_tag. (bpeck@redhat.com)
- fix to use annoted tags so that taggerdate can be used for sorting.
  (bpeck@redhat.com)
- fix from tosky@redhat.com to fix tagging to support periods in those version
  control systems that support it. (bpeck@redhat.com)

* Tue Apr 05 2011 Marian Csontos <mcsontos@redhat.com> 4.32-1
- bz644805 - Added hook to run scripts on watchdog (mcsontos@redhat.com)
- bz688218 - make rpm does not handle regexp metachars in test names
  (bpeck@redhat.com)

* Fri Mar 11 2011 Bill Peck <bpeck@redhat.com> 4.31-1
- Support uefibootmgr on all arches that have it installed. (bpeck@redhat.com)
- sanity checks for git tags (dcallagh@redhat.com)
- rhts-run-simple-test doesn't need to use tee -a, produces redundant output.
  (bpeck@redhat.com)
- rhts-mk-get-current-tag ignores packed-refs (dcallagh@redhat.com)

* Mon Feb 07 2011 Bill Peck <bpeck@redhat.com> 4.30-1
- ignore rpm -q error. (bpeck@redhat.com)
- Avoid reporting selinux errors on the harness itself. (bpeck@redhat.com)
- bz664764 - rhts-devel and svn+ssh problem (mcsontos@redhat.com)

* Fri Jan 14 2011 Bill Peck <bpeck@redhat.com> 4.29-1
- revert tighter selinux controls (bpeck@redhat.com)
- Added: CompatService to RhtsOptions (mcsontos@redhat.com)

* Fri Dec 17 2010 Bill Peck <bpeck@redhat.com> 4.28-1
- use /mnt/testarea instead of /tmp.  /tmp should not be used as it will
  trigger avc errors. (bpeck@redhat.com)
- make package not working with local git repos (mcsontos@redhat.com)

* Mon Dec 06 2010 Bill Peck <bpeck@redhat.com> 4.27-1
- Merge branch 'master' of ssh://git.fedorahosted.org/git/rhts
  (bpeck@redhat.com)
- extend watchdog's directly through lab controller. (bpeck@redhat.com)

* Tue Nov 30 2010 Marian Csontos <mcsontos@redhat.com> 4.26-1
- Added: Print selinux status into AVCs (mcsontos@redhat.com)
- Fixed: ausearch always using en_US date format (mcsontos@redhat.com)

* Wed Nov 24 2010 Marian Csontos <mcsontos@redhat.com> 4.25-1
- Enhanced ausearch (mcsontos@redhat.com)

* Thu Nov 18 2010 Bill Peck <bpeck@redhat.com> 4.24-1
- make it work with python2.7 (bpeck@redhat.com)

* Mon Nov 08 2010 Bill Peck <bpeck@redhat.com> 4.23-1
- bz640395  -  make bkradd does not work (bpeck@redhat.com)
- Added: Environment and RhtsOptions to metadata (mcsontos@redhat.com)

* Wed Sep 08 2010 Bill Peck <bpeck@redhat.com> 4.22-1
- Merge branch 'TESTOUT' (mcsontos@redhat.com)
- Make prev. TESTOUT patch prettier (mcsontos@redhat.com)
- fix rhts-db-submit-result mkstemp on rhel3. (bpeck@redhat.com)
- Fixed re-sending TESTOUT.log (mcsontos@redhat.com)

* Wed Sep 01 2010 Marian Csontos <mcsontos@redhat.com> 4.21-1
- Fixed wrong timestamp format
- Improved AVC logging.

* Fri Aug 27 2010 Marian Csontos <mcsontos@redhat.com> 4.20-1
- PartialRevert "BZ616455 - Report all AVC denials" (mcsontos@redhat.com)

* Tue Aug 24 2010 Marian Csontos <mcsontos@redhat.com> 4.19-1
- Use runuser instead of su (mcsontos@redhat.com)

* Mon Aug 16 2010 Marian Csontos <mcsontos@redhat.com> 4.18-1
- BZ616455 - Report all AVC denials (ebenes@redhat.com)

* Tue Jul 13 2010 Bill Peck <bpeck@redhat.com> 4.17-1
- Update to require beaker-client (bpeck@redhat.com)

* Tue Jun 29 2010 Bill Peck <bpeck@redhat.com> 4.16-1
- fix rhts-test-runner.sh logic. (bpeck@redhat.com)

* Thu Jun 17 2010 Bill Peck <bpeck@redhat.com> 4.15-1
- Include Marians patch for md5/sha/none.  Allows FIPS testing to work.
  (bpeck@redhat.com)
- bz605360 prevent rhts-mk-get-current-tag from confusing (bpeck@redhat.com)

* Fri Jun 11 2010 Bill Peck <bpeck@redhat.com> 4.14-1
- sync up with 108 (bpeck@redhat.com)

* Wed Jun 09 2010 Bill Peck <bpeck@redhat.com> 4.13-1
- tell ausearch to only look at the logs, ignore stdin (bpeck@redhat.com)
- add missing rhts_workflow (bpeck@redhat.com)

* Fri Jun 04 2010 Bill Peck <bpeck@redhat.com> 4.10-1
- add missing rhts namespace (bpeck@redhat.com)

* Thu Jun 03 2010 Bill Peck <bpeck@redhat.com> 4.9-1
- New rhts
