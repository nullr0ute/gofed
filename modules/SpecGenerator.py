from ImportPath import GITHUB, GOOGLECODE, GOOGLEGOLANGORG, GOLANGORG, GOPKG, BITBUCKET, UNKNOWN
from PackageInfo import PackageInfo
from ProviderPrefixes import ProviderPrefixes
import os
from Utils import runCommand

class SpecGenerator:

	def __init__(self, import_path, commit="", skiperrors=False, with_build = False):
		self.import_path = import_path
		self.commit = commit
		self.spec_name = ""
		self.pkg_info = None
		self.warn = ""
		self.with_build = with_build

	def getWarning(self):
		return self.warn

	def setPackageInfo(self, pkg_info):
		self.pkg_info = pkg_info

	def generateHeaderEpilogue(self):
		self.file.write("%if 0%{?fedora} || 0%{?rhel} == 6\n")
		self.file.write("%global with_devel 1\n")
		self.file.write("%global with_bundled 0\n")

		# if generated with build section generate debuginfo as well
		if self.with_build:
			self.file.write("%global with_debug 1\n")
		else:
			self.file.write("%global with_debug 0\n")

		self.file.write("%global with_check 1\n")
		self.file.write("%global with_unit_test 1\n")
		self.file.write("%else\n")
		self.file.write("%global with_devel 0\n")
		self.file.write("%global with_bundled 0\n")
		self.file.write("%global with_debug 0\n")
		self.file.write("%global with_check 0\n")
		self.file.write("%global with_unit_test 0\n")
		self.file.write("%endif\n\n")

		# debug
		self.file.write("%if 0%{?with_debug}\n")
		self.file.write("%global _dwz_low_mem_die_limit 0\n")
		self.file.write("%else\n")
		self.file.write("%global debug_package   %{nil}\n")
		self.file.write("%endif\n\n")

		# license
		self.file.write("%define copying() \\\n")
		self.file.write("%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7 \\\n")
		self.file.write("%license %{*} \\\n")
		self.file.write("%else \\\n")
		self.file.write("%doc %{*} \\\n")
		self.file.write("%endif\n\n")

		# ifgccgo
		self.file.write("%global isgccgoarch 0\n")
		self.file.write("%if 0%{?gccgo_arches:1}\n")
		self.file.write("%ifarch %{gccgo_arches}\n")
		self.file.write("%global isgccgoarch 1\n")
		self.file.write("%endif\n")
		self.file.write("%endif\n\n")

	def generateGithubHeader(self, project, repository, url, provider_prefix, commit):
		self.file.write("%global provider        github\n")
		self.file.write("%global provider_tld    com\n")
		self.file.write("%%global project         %s\n" % project)
		self.file.write("%%global repo            %s\n" % repository)
		self.file.write("# https://%s\n" % provider_prefix)
		self.file.write("%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}\n")

		if url != provider_prefix:
			self.file.write("%%global import_path     %s\n" % url)
		else:
			self.file.write("%global import_path     %{provider_prefix}\n")

                self.file.write("%%global commit          %s\n" % commit)
		self.file.write("%global shortcommit     %(c=%{commit}; echo ${c:0:7})\n\n")
		self.file.write("Name:           golang-%{provider}-%{project}-%{repo}\n")
		self.file.write("Version:        0\n")
		self.file.write("Release:        0.0.git%{shortcommit}%{?dist}\n")
		self.file.write("Summary:        !!!!FILL!!!!\n")
		self.file.write("License:        !!!!FILL!!!!\n")
		self.file.write("URL:            https://%{provider_prefix}\n")
		self.file.write("Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz\n")

	def generateGooglecodeHeader(self, repository, url, provider_prefix, commit):
		parts = repository.split(".")
		stripped_repo = parts[-1]
		rrepository = ".".join(parts[::-1])
		self.file.write("%global provider        google\n")
		self.file.write("%global provider_sub    code\n")
		self.file.write("%global provider_tld    com\n")
		self.file.write("%global project         p\n")
		self.file.write("%%global repo            %s\n" % repository)
		self.file.write("%%global rrepo           %s\n" % rrepository)
		self.file.write("# https://%s\n" % provider_prefix)
		self.file.write("%global provider_prefix %{provider_sub}.%{provider}.%{provider_tld}/%{project}/%{repo}\n")

		if url != provider_prefix:
			self.file.write("%%global import_path     %s\n" % url)
		else:
			self.file.write("%global import_path     %{provider_prefix}\n")

		self.file.write("%%global rev             %s\n" % commit)
		self.file.write("%global shortrev        %(c=%{rev}; echo ${c:0:12})\n\n")
		self.file.write("Name:           golang-%%{provider}%%{provider_sub}-%s\n" % stripped_repo)
		self.file.write("Version:        0\n")
		self.file.write("Release:        0.0.hg%{shortrev}%{?dist}\n")
		self.file.write("Summary:        !!!!FILL!!!!\n")
		self.file.write("License:        !!!!FILL!!!!\n")
		self.file.write("URL:            https://%{provider_prefix}\n")
		self.file.write("Source0:        https://%{rrepo}.%{provider}%{provider_sub}.%{provider_tld}/archive/%{rev}.tar.gz\n")

	def generateBitbucketHeader(self, project, repository, url, provider_prefix, commit):
		self.file.write("%global provider        bitbucket\n")
		self.file.write("%global provider_tld    org\n")
		self.file.write("%%global project         %s\n" % project)
		self.file.write("%%global repo            %s\n" % repository)
		self.file.write("# https://%s\n" % provider_prefix)
		self.file.write("%%global provider_prefix %s\n" % provider_prefix)
		self.file.write("%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}\n")

		if url != provider_prefix:
			self.file.write("%%global import_path     %s\n" % url)
		else:
			self.file.write("%global import_path     %{provider_prefix}\n")

		self.file.write("%%global commit          %s\n" % commit)
		self.file.write("%global shortcommit     %(c=%{commit}; echo ${c:0:12})\n\n")
		self.file.write("Name:           golang-%{provider}-%{project}-%{repo}\n")
		self.file.write("Version:        0\n")
		self.file.write("Release:        0.0.git%{shortcommit}%{?dist}\n")
		self.file.write("Summary:        !!!!FILL!!!!\n")
		self.file.write("License:        !!!!FILL!!!!\n")
		self.file.write("URL:            https://%{provider_prefix}\n")
		self.file.write("Source0:        https://%{provider_prefix}/get/%%{shortcommit}.tar.gz\n")

	def generateHeaderPrologue(self):
		self.file.write("# If go_arches not defined fall through to implicit golang archs\n")
		self.file.write("%if 0%{?go_arches:1}\n")
		self.file.write("ExclusiveArch:  %{go_arches}\n")
		self.file.write("%else\n")
		self.file.write("ExclusiveArch:   %{ix86} x86_64 %{arm}\n")
		self.file.write("%endif\n")
		self.file.write("# If gccgo_arches does not fit or is not defined fall through to golang\n")
		self.file.write("%if %{isgccgoarch}\n")
		self.file.write("BuildRequires:   gcc-go >= %{gccgo_min_vers}\n")
		self.file.write("%else\n")
		self.file.write("BuildRequires:   golang\n")
		self.file.write("%endif\n\n")

                self.file.write("%description\n")
                self.file.write("%{summary}\n")
                self.file.write("\n")

	def generateDevelHeader(self, project, prefix):
		self.file.write("%if 0%{?with_devel}\n")
                self.file.write("%package devel\n")
                self.file.write("Summary:       %{summary}\n")
                self.file.write("BuildArch:     noarch\n")
                self.file.write("\n")

		# dependencies
		imported_packages = project.getImportedPackages()
		package_imports_occurence = project.getPackageImportsOccurences()

		self.file.write("%if 0%{?with_check}\n")
		for dep in imported_packages:
			if dep.startswith(prefix):
				continue

			# skip all dependencies occuring only in main packages
			skip = True
			if dep in package_imports_occurence:
				for occurrence in package_imports_occurence[dep]:
					if not occurrence.endswith(":main"):
						skip = False
						break
			if skip:
				continue


			self.file.write("BuildRequires: golang(%s)\n" % (dep))
		self.file.write("%endif\n")

		if imported_packages != []:
			self.file.write("\n")
			for dep in imported_packages:
				if dep.startswith(prefix):
					continue

				# skip all dependencies occuring only in main packages
				skip = True
				if dep in package_imports_occurence:
					for occurrence in package_imports_occurence[dep]:
						if not occurrence.endswith(":main"):
							skip = False
							break
				if skip:
					continue

				self.file.write("Requires:      golang(%s)\n" % (dep))

		# provides
		self.file.write("\n")
		for path in project.getProvidedPackages():
			# skip all provided packages with /internal/ keyword
			if "internal" in path.split("/"):
				continue

			sufix = ""
			if path != ".":
				sufix = "/%s" % path

			self.file.write("Provides:      golang(%%{import_path}%s) = %%{version}-%%{release}\n" % sufix)

		# description
		self.file.write("\n%description devel\n")
		self.file.write("%{summary}\n\n")
		self.file.write("This package contains library source intended for\n")
		self.file.write("building other packages which use import path with\n")
		self.file.write("%{import_path} prefix.\n")
		self.file.write("%endif\n")

	def generateUnitTestHeader(self):
		self.file.write("%if 0%{?with_unit_test}\n")
		self.file.write("%package unit-test\n")
		self.file.write("Summary:         Unit tests for %{name} package\n")
		self.file.write("# If go_arches not defined fall through to implicit golang archs\n")
		self.file.write("%if 0%{?go_arches:1}\n")
		self.file.write("ExclusiveArch:  %{go_arches}\n")
		self.file.write("%else\n")
		self.file.write("ExclusiveArch:   %{ix86} x86_64 %{arm}\n")
		self.file.write("%endif\n")
		self.file.write("# If gccgo_arches does not fit or is not defined fall through to golang\n")
		self.file.write("%if %{isgccgoarch}\n")
		self.file.write("BuildRequires:   gcc-go >= %{gccgo_min_vers}\n")
		self.file.write("%else\n")
		self.file.write("BuildRequires:   golang\n")
		self.file.write("%endif\n\n")
		self.file.write("%if 0%{?with_check}\n")
		self.file.write("#Here comes all BuildRequires: PACKAGE the unit tests\n#in %%check section need for running\n")
		self.file.write("%endif\n")
		self.file.write("\n")
		self.file.write("# test subpackage tests code from devel subpackage\n")
		self.file.write("Requires:        %{name}-devel = %{version}-%{release}\n")
		self.file.write("\n")
		self.file.write("%description unit-test\n")
		self.file.write("%{summary}\n")
		self.file.write("\n")
		self.file.write("This package contains unit tests for project\nproviding packages with %{import_path} prefix.\n")
		self.file.write("%endif\n")


	def generatePrepSection(self, provider):
		self.file.write("%prep\n")

		if provider == GOOGLECODE:
			self.file.write("%setup -q -n %{rrepo}-%{shortrev}\n")
		elif provider == BITBUCKET:
			self.file.write("%setup -q -n %{project}-%{repo}-%{shortcommit}\n")
		else:
			self.file.write("%setup -q -n %{repo}-%{commit}\n")

	def generateBuildSection(self, url):
		self.file.write("%build\n")

		if self.with_build:
			parts = url.split("/")
			self.file.write("# If gccgo_arches does not fit or is not defined fall through to golang\n")
			self.file.write("# gccco arches\n")
			self.file.write("%if %{isgccgoarch}\n")
			self.file.write("%if 0%{?gcc_go_build:1}\n")
			self.file.write("export GOCOMPILER='%{gcc_go_build}'\n")
			self.file.write("%else\n")
			self.file.write("echo \"No compiler for SA\"\n")
			self.file.write("exit 1\n")
			self.file.write("%endif\n")
			self.file.write("# golang arches (due to ExclusiveArch)\n")
			self.file.write("%else\n")
			self.file.write("%if 0%{?golang_build:1}\n")
			self.file.write("export GOCOMPILER='%{golang_build} -ldflags \"$LDFLAGS\"'\n")
			self.file.write("%else\n")
			self.file.write("export GOCOMPILER='go build -ldflags \"$LDFLAGS\"'\n")
			self.file.write("%endif\n")
			self.file.write("%endif\n")
			self.file.write("\n")
			self.file.write("export LDFLAGS=""\n")
			self.file.write("%if 0%{?with_debug}\n")
			self.file.write("%if %{isgccgoarch}\n")
			self.file.write("export OLD_RPM_OPT_FLAGS=\"$RPM_OPT_FLAGS\"\n")
			self.file.write("function gobuild {\n")
			self.file.write("export RPM_OPT_FLAGS=\"$OLD_RPM_OPT_FLAGS -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')\"\n")
			self.file.write("eval ${GOCOMPILER} -a -v -x \"$@\";\n")
			self.file.write("}\n")
			self.file.write("%else\n")
			self.file.write("export OLD_LDFLAGS=\"$LDFLAGS\"\n")
			self.file.write("function gobuild {\n")
			self.file.write("export LDFLAGS=\"$OLD_LDFLAGS -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')\"\n")
			self.file.write("eval ${GOCOMPILER} -a -v -x \"$@\";\n")
			self.file.write("}\n")
			self.file.write("%endif\n")
			self.file.write("%else\n")
			self.file.write("function gobuild { eval ${GOCOMPILER} -a -v -x \"$@\"; }\n")
			self.file.write("%endif\n")
			self.file.write("\n")
			self.file.write("mkdir -p src/%s\n" % "/".join(parts[:-1]))
			self.file.write("ln -s ../../../ src/%s\n" % url)
			self.file.write("\n")
			self.file.write("%if ! 0%{?with_bundled}\n")
			self.file.write("export GOPATH=$(pwd):%{gopath}\n")
			self.file.write("%else\n")
			self.file.write("export GOPATH=$(pwd):$(pwd)/Godeps/_workspace:%{gopath}\n")
			self.file.write("%endif\n")
			self.file.write("\n")
			self.file.write("#gobuild -o bin/NAME %{import_path}/NAME\n")

	def generateInstallSection(self, direct_go_files = False):
		self.file.write("%install\n")
		if self.with_build:
			self.file.write("install -d -p %{buildroot}%{_bindir}\n")
			self.file.write("#install -p -m 755 bin/NAME %{buildroot}%{_bindir}\n")
			self.file.write("\n")

		self.file.write("# source codes for building projects\n")
		self.file.write("%if 0%{?with_devel}\n")
		self.file.write("install -d -p %{buildroot}/%{gopath}/src/%{import_path}/\n")
		self.file.write("# find all *.go but no *_test.go files and generate devel.file-list\n")
		self.file.write("for file in $(find . -iname \"*.go\" \! -iname \"*_test.go\") ; do\n")
		self.file.write("    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)\n")
		self.file.write("    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file\n")
		self.file.write("    echo \"%%{gopath}/src/%%{import_path}/$file\" >> devel.file-list\n")
		self.file.write("done\n")
		self.file.write("%endif\n\n")

		self.file.write("# testing files for this project\n")
		self.file.write("%if 0%{?with_unit_test}\n")
		self.file.write("install -d -p %{buildroot}/%{gopath}/src/%{import_path}/\n")
		self.file.write("# find all *_test.go files and generate unit-test.file-list\n")
		self.file.write("for file in $(find . -iname \"*_test.go\"); do\n")
		self.file.write("    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)\n")
		self.file.write("    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file\n")
		self.file.write("    echo \"%%{gopath}/src/%%{import_path}/$file\" >> unit-test.file-list\n")
		self.file.write("done\n")
		self.file.write("%endif\n")

	def generateCheckSection(self, project):
		self.file.write("%check\n")
		self.file.write("%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}\n")
		self.file.write("%if %{isgccgoarch}\n")
		self.file.write("function gotest { %{gcc_go_test} \"$@\"; }\n")
		self.file.write("%else\n")
		self.file.write("%if 0%{?golang_test:1}\n")
		self.file.write("function gotest { %{golang_test} \"$@\"; }\n")
		self.file.write("%else\n")
		self.file.write("function gotest { go test \"$@\"; }\n")
		self.file.write("%endif\n")
		self.file.write("%endif\n\n")
		self.file.write("export GOPATH=%{buildroot}/%{gopath}:%{gopath}\n")

		sdirs = sorted(project.getTestDirectories())
                for dir in sdirs:

			sufix = ""
			if dir != ".":
				sufix = "/%s" % dir

			self.file.write("gotest %%{import_path}%s\n" % sufix)
		self.file.write("%endif\n")

	def generateFilesSection(self, provider, project, ip_prefix = ""):
		# doc all *.md files
		docs = project.getDocs()
		licenses = []
		restdocs = []
		if docs != []:
			# scan for license
			for doc in docs:
				if doc.lower().find('license') != -1:
					licenses.append(doc)
				elif doc.lower().find('copying') != -1:
					licenses.append(doc)
				else:
					restdocs.append(doc)

		if self.with_build:
			self.file.write("%files\n")
			if license != []:
				self.file.write("%%copying %s\n" % (" ".join(licenses)))
			if restdocs != []:
				self.file.write("%%doc %s\n" % (" ".join(restdocs)))

			self.file.write("#%{_bindir}/NAME\n")
			self.file.write("\n")


		self.file.write("%if 0%{?with_devel}\n")
		self.file.write("%files devel -f devel.file-list\n")

		if license != []:
			self.file.write("%%copying %s\n" % (" ".join(licenses)))
		if restdocs != []:
			self.file.write("%%doc %s\n" % (" ".join(restdocs)))

		# http://www.rpm.org/max-rpm/s1-rpm-inside-files-list-directives.html
		# it takes every dir and file recursively
		if provider in [GITHUB, BITBUCKET]:
			if ip_prefix != "":
				pp_obj = ProviderPrefixes()
				ok, prefixes = pp_obj.loadCommonProviderPrefixes()
				if not ok or ip_prefix not in prefixes:
					self.file.write("%%dir %%{gopath}/src/%s\n" % ip_prefix)
			else:
				self.file.write("%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}\n")

		self.file.write("%dir %{gopath}/src/%{import_path}\n")
		self.file.write("%endif\n\n")

		self.file.write("%if 0%{?with_unit_test}\n")
		self.file.write("%files unit-test -f unit-test.file-list\n")

		if license != []:
			self.file.write("%%copying %s\n" % (" ".join(licenses)))
		if restdocs != []:
			self.file.write("%%doc %s\n" % (" ".join(restdocs)))

		self.file.write("%endif\n")


	def generateChangelogSection(self):
		self.file.write("%changelog\n")

	def generate(self):
		if self.pkg_info == None:
			self.err = "PackageInfo not set"
			return False

		cwd = os.getcwd()
		repo_info = self.pkg_info.getRepositoryInfo()
		archive_info = repo_info.getArchiveInfo()
		ip_info = repo_info.getImportPathInfo()
		prj_info = self.pkg_info.getProjectInfo()

		self.warn = prj_info.getWarning()

		provider = ip_info.getProvider()
		project = ip_info.project
		repository = ip_info.repository
		commit = repo_info.getCommit()
		url = ip_info.getPrefix()
		archive_dir = archive_info.archive_dir
		prefix = ip_info.getPrefix()
		provider_prefix = ip_info.getProviderPrefix()

		# generate header
		self.generateHeaderEpilogue()

		if provider == GITHUB:
			self.generateGithubHeader(project, repository, url, provider_prefix, commit)
		elif provider == GOOGLECODE:
			self.generateGooglecodeHeader(repository, url, provider_prefix, commit)
		elif provider == BITBUCKET:
			self.generateBitbucketHeader(project, repository, url, provider_prefix, commit)

		self.file.write("\n")
		self.generateHeaderPrologue()

		# generate devel subpackage
		self.generateDevelHeader(prj_info, prefix)
		self.file.write("\n")

		# generate unit-test subpackage
		self.generateUnitTestHeader()
		self.file.write("\n")

		# generate prep section
		self.generatePrepSection(provider)
		self.file.write("\n")

		# generate build section
		self.generateBuildSection(url)
		self.file.write("\n")

		# generate install section
		direct_go_files = False
		if "." in prj_info.getProvidedPackages():
			direct_go_files = True

		self.generateInstallSection(direct_go_files)
		self.file.write("\n")

		# generate check section
		self.generateCheckSection(prj_info)
		self.file.write("\n")

		# generate files section
		if url != provider_prefix:
			ip_prefix, _ = os.path.split(url)
		else:
			ip_prefix = ""

		self.generateFilesSection(provider, prj_info, ip_prefix)
		self.file.write("\n")

		# generate changelog section
		self.generateChangelogSection()
		self.file.write("\n")

		return True

	def setOutputFile(self, file):
		self.file = file

